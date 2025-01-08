from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langchain_milvus import Milvus
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from bridge_llm.llm_doubao import chat_doubao   
from bridge_llm.llm_ollama import embeddings_nomic, embeddings_bge_m3
from langchain_community.document_loaders import SQLDatabaseLoader
from langchain_community.utilities import SQLDatabase

current_embedding_model = embeddings_nomic
current_llm = chat_doubao

def create_tools_vectorstore(csv_file_path:str) :
    """初始化工具向量数据库
    args:
        csv_file_path: 生信工具数据文件路径
    returns:
        vectorstore: 生信工具向量数据库
    """
    # 加载CSV数据
    
    # column_name: doi,pmc,pmid,title,year,description,function,homepage,keyword,tooltype,topic
    loader = CSVLoader(
        file_path=file_path,
        csv_args={
            'delimiter': ',',
        },
        source_column='pmid',
        metadata_columns=('year', 'keyword', 'tooltype', 'topic'),
    )
    documents = loader.load()
    
    # 初始化embedding模型
    embeddings = current_embedding_model
    
    # 创建向量数据库
    vectorstore = Milvus(
        embedding_function=embeddings,
        collection_name="bioinfo_tools",
        connection_args={"uri":"/home/awgao/BioinfoGPT/data/vector_db/milvus_100_test.db"},
        auto_id=True,
        drop_old=True
    )
     
    # 添加文档到向量数据库
    vectorstore.add_documents(documents)

    return vectorstore

file_path = "/home/awgao/BioinfoGPT/data/tools/bioinfo_tools_test.csv"
create_tools_vectorstore(file_path)

# 载入已有的向量数据库
bioinfo_tools_vectorstore = Milvus(
    embedding_function=current_embedding_model,
    collection_name="bioinfo_tools",
    connection_args={"uri":"/home/awgao/BioinfoGPT/data/vector_db/milvus_7000_test.db"},
    auto_id=True,
)   
# 创建retriever并设置搜索参数
bioinfo_tools_retriever = bioinfo_tools_vectorstore.as_retriever(search_kwargs={'k': 5})


# 使用 bge-m3 作为嵌入模型
current_embedding_model = embeddings_bge_m3

# 直接使用 .db 文件作为文档源，使用SQLDatabaseloader 直接读取而不是使用 csvloader
# db 文件的列名是 toolname,pmid,pmc,doi,year,keyword,homepage,title,abstract,content,description,function,tooltype,topic
def create_tools_vectorstore_from_db(db_file_path: str,vector_db_path:str):
    db_url = f"sqlite:///{db_file_path}"
    db = SQLDatabase.from_uri(db_url)
    
    def content_mapper(row):
        title = row.title or ''
        description = row.description or ''
        function = row.function or ''
        homepage = row.homepage or ''
        return f"Title: {title}\nDescription: {description}\nFunction: {function}\nHomepage: {homepage}"
     
    def metadata_mapper(row):
        # 处理 JSON 字符串格式的字段
        def clean_json_string(value):
            if not value:
                return ''
            # 移除 [] 和 引号，分割并重新组合
            cleaned = value.strip('[]').replace('"', '').split(',')
            return ', '.join(cleaned)
        
        return {
            "year": str(row.year) if row.year else '',
            "keyword": str(row.keyword) if row.keyword else '',
            "tooltype": clean_json_string(row.tooltype),
            "topic": clean_json_string(row.topic),
            "pmid": f"https://pubmed.ncbi.nlm.nih.gov/{row.pmid}/" if row.pmid else '',
            "doi": str(row.doi) if row.doi else ''
        }
    
    loader = SQLDatabaseLoader(
        query="SELECT * FROM articles",
        db=db,
        metadata_mapper=metadata_mapper,
        page_content_mapper=content_mapper
    )
    documents = loader.load()

    embeddings = current_embedding_model
    
    # 创建向量数据库
    vectorstore = Milvus(
        embedding_function=embeddings,
        collection_name="bioinfo_tools",
        connection_args={"uri":vector_db_path},
        auto_id=True,
        drop_old=True
    )
     
    # 添加文档到向量数据库
    vectorstore.add_documents(documents)

    return vectorstore


db_file_path = "/home/awgao/BioinfoGPT/data/paper_summaries_local_xml_v2.db"
milvus_vdb_path = "/home/awgao/BioinfoGPT/data/vector_db/milvus_7000_bge_m3.db"
bioinfo_tools_vectorstore = create_tools_vectorstore_from_db(db_file_path, milvus_vdb_path)

# 载入已有的向量数据库
bioinfo_tools_vectorstore = Milvus(
    embedding_function=current_embedding_model,
    collection_name="bioinfo_tools",
    connection_args={"uri":"/home/awgao/BioinfoGPT/data/vector_db/milvus_7000_bge_m3.db"},
    auto_id=True,
)






recommend_tools_prompt = PromptTemplate(
    input_variables=["question", "tools_docs"],
    template="""
你是一个生物信息学工具推荐专家。
根据用户的问题和检索到的工具信息,生成一个专业的推荐回答。

问题: {question}
检索到的工具信息:{tool_docs}

回答需要:
1. 解释为什么这些工具适合用户的需求。
2. 简要介绍每个工具的主要功能和特点。
3. 如果工具之间有优劣或互补关系,也要说明。
4. 尽量提供工具的 DOI 链接和 pubmed ID。
保持回答简洁专业。
"""
)


recommend_tools_chain = recommend_tools_prompt | current_llm | StrOutputParser()

question = '有哪些分析ATACseq数据的软件？'
document = bioinfo_tools_retriever.invoke(question)
print(f'问题 {question} 找到的文档有：\n {document}')
res1 = recommend_tools_chain.invoke({'question': question, 'tool_docs': document})
print(res1)


recommend_tools_prompt_KR = PromptTemplate(
    input_variables=["question", "tools_docs"],
    template="""
당신은 생물정보학 도구 추천 전문가입니다. 사용자의 질문과 검색된 도구 정보를 바탕으로 전문적인 추천 답변을 생성합니다.

질문: {question} 검색된 도구 정보: {tool_docs}

답변 요구사항: 
1. 이 도구들이 사용자의 요구에 적합한 이유를 설명합니다. 
2. 각 도구의 주요 기능과 특징을 간략히 소개합니다. 
3. 도구 간에 우열 또는 상호보완 관계가 있다면 설명합니다. 
4. 가능한 도구의 DOI 링크와 PubMed ID를 제공합니다. 
답변을 간결하고 전문적으로 유지합니다.
"""
)
bioinfo_tools_retriever_KR = bioinfo_tools_vectorstore.as_retriever(search_kwargs={'k': 5})

KR_question = '관련 단일 세포 증강 인자 데이터베이스에는 어떤 것이 있나요?'
KR_document = bioinfo_tools_retriever_KR.invoke(KR_question)
for f in KR_document:
    print(f.page_content)

    
recommend_tools_chain_KR = recommend_tools_prompt_KR | current_llm | StrOutputParser()
res2 = recommend_tools_chain_KR.invoke({'question': KR_question, 'tool_docs': KR_document})
print(res2)

question1 = "有哪些相关单细胞增强子的数据库？"
document1 = bioinfo_tools_retriever.invoke(question1)
for f in document1:
    print(f.page_content)
res3 = recommend_tools_chain.invoke({'question': question1, 'tool_docs': document1})
print(res3)