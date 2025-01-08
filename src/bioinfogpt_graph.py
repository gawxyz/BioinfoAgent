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
from bridge_llm.llm_ollama import embeddings_nomic

current_embedding_model = embeddings_nomic
current_llm = chat_doubao

## 工具库检索

# 初始化工具库向量数据库连接
def create_tools_vectorstore() :
    """初始化工具向量数据库
    args:
        csv_file_path: 生信工具数据文件路径
    returns:
        vectorstore: 生信工具向量数据库
    """
    # 加载CSV数据
    file_path = "/home/awgao/BioinfoGPT/data/tools/bioinfo_tools_test.csv"
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

# load vectorstore
embeddings = current_embedding_model
bioinfo_tools_vectorstore = Milvus(
    embedding_function=embeddings,
    collection_name="bioinfo_tools",
    connection_args={"uri":"/home/awgao/BioinfoGPT/data/vector_db/milvus_100_demo.db"},
    auto_id=True,
)

# 创建retriever并设置搜索参数
bioinfo_tools_retriever = bioinfo_tools_vectorstore.as_retriever(search_kwargs={'k': 3})
    
# 工具推荐rag chain

recommend_tools_prompt = PromptTemplate(
    input_variables=["question", "tools_docs"],
    template="""
你是一个生物信息学工具推荐专家。
根据用户的问题和检索到的工具信息,生成一个专业的推荐回答。

问题: {question}
检索到的工具信息:{tools_docs}

回答需要:
1. 解释为什么这些工具适合用户的需求。
2. 简要介绍每个工具的主要功能和特点。
3. 如果工具之间有优劣或互补关系,也要说明。
4. 尽量提供工具的 DOI 链接和 pubmed ID。
保持回答简洁专业。
"""
)
recommend_tools_chain = recommend_tools_prompt | current_llm | StrOutputParser()


## 生信工具文档库检索

# 初始化生信工具文档库
def create_bioinfo_tools_docs_vectorstores() -> Dict[str, Milvus]:
    """初始化生信工具文档向量数据库
    
    所有工具共用一个db文件,但使用不同的collection
    """
    base_path = "/home/awgao/BioinfoGPT/data/vBioconduactor_top_75"
    vectorstores = {}
    
    # 初始化embedding模型
    embeddings = current_embedding_model
    
    # 文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        length_function=len,
    )
    
    # 遍历所有工具目录
    for tool_dir in os.listdir(base_path):
        tool_path = os.path.join(base_path, tool_dir)
        if not os.path.isdir(tool_path):
            continue
            
        # 查找merged.txt文件
        merged_file = os.path.join(tool_path, "merged.txt")
        if os.path.exists(merged_file):
            try:
                # 加载文档
                loader = TextLoader(merged_file, encoding='utf-8')
                tool_docs = loader.load()
                
                # 为文档添加元数据
                for doc in tool_docs:
                    doc.metadata.update({
                        "tool_name": tool_dir,
                        "source": "Bioconductor",
                        "doc_type": "manual"
                    })
                
                # 分割文档
                splits = text_splitter.split_documents(tool_docs)
                
                # 创建该工具的collection
                vectorstore = Milvus(
                    embedding_function=embeddings,
                    collection_name=f"bioinfo_{tool_dir}",
                    connection_args={"uri": "/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db"},  # 所有工具共用一个db
                    auto_id=True,
                    drop_old=True
                )
                
                # 添加文档到向量数据库
                vectorstore.add_documents(splits)
                
                # 保存到字典
                vectorstores[tool_dir] = vectorstore
                
                print(f"成功处理工具: {tool_dir}")
                
            except Exception as e:
                print(f"处理 {tool_dir} 时出错: {str(e)}")
    
    return vectorstores
# 加载已存在的向量数据库collections
def load_existing_bioinfo_tools_docs_vectorstores() -> Dict[str, Milvus]:
    """加载已存在的向量数据库collections
    """
    base_path = "/home/awgao/BioinfoGPT/data/vector_db/Bioconduactor_top_75"
    all_bioinfo_tools_docs_vectorstores_dict = {}
    
    # 初始化embedding模型
    embeddings = current_embedding_model
    
    # 遍历所有工具目录
    for tool_dir in os.listdir(base_path):
        if not os.path.isdir(os.path.join(base_path, tool_dir)):
            continue
            
        try:
            # 连接到对应的collection
            vectorstore = Milvus(
                embedding_function=embeddings,
                collection_name=f"bioinfo_{tool_dir}",
                connection_args={"uri": "/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db"},
                auto_id=True,
                drop_old=False  # 不删除已有数据
            )
            
            all_bioinfo_tools_docs_vectorstores_dict[tool_dir] = vectorstore
            print(f"成功加载工具collection: {tool_dir}")
            
        except Exception as e:
            print(f"加载 {tool_dir} collection时出错: {str(e)}")
    
    return all_bioinfo_tools_docs_vectorstores_dict

def get_specific_doc_vectorstore_retriever(toolname:str):
    """获取指定工具的向量存储库
    """
    
    all_bioinfo_tools_docs_vectorstores_dict = load_existing_bioinfo_tools_docs_vectorstores()
    if toolname not in all_bioinfo_tools_docs_vectorstores_dict:
        raise ValueError(f"工具 {toolname} 不存在")
    return all_bioinfo_tools_docs_vectorstores_dict[toolname].as_retriever(search_kwargs={'k': 3})

# 文档问答 RAG chain
doc_query_prompt = PromptTemplate(
    input_variables=["question", "documents"],
    template="""
作为一位专业的生物信息学分析专家，请基于{tool_name}软件文档内容回答用户问题。

用户问题：
{question}

相关文档内容：
{context}

请按照以下结构组织回答：

1. 问题解答
- 直接、准确地回答用户问题
- 如果文档内容不足以完全回答，请说明并提供可能的解决方案
- 使用专业但易于理解的语言

2. 代码示例（如适用）
- 提供完整可执行的代码
- 详细解释关键参数和函数
- 说明预期输出和结果解释

3. 最佳实践
- 提供实用建议和注意事项
- 说明常见问题的解决方法
- 推荐高效的使用方式

4. 补充信息
- 相关的生物学背景知识
- 推荐的后续分析步骤
- 建议的学习资源
"""
)
promote_english_prompt = PromptTemplate(
    input_variables=["question", "documents"],
    template="""
As a professional bioinformatics analyst, please answer the user's question based on the {tool_name} software documentation.

User Question:
{question}

Relevant Documentation:
{context}

Please structure your response as follows:

1. Direct Answer
- Provide a clear and accurate answer to the user's question
- If documentation is insufficient, explain and suggest possible solutions
- Use professional yet accessible language

2. Code Examples (if applicable)
- Provide complete executable code
- Explain key parameters and functions
- Describe expected output and result interpretation

3. Best Practices
- Provide practical tips and considerations
- Address common issues and solutions
- Recommend efficient usage patterns

4. Additional Information
- Relevant biological background
- Suggested follow-up analyses
- Recommended learning resources

Please ensure:
1. If documentation is insufficient, direct users to complete documentation or Bioconductor community
2. Indicate if newer versions or alternative methods exist
3. Provide relevant references when necessary
4. Format response in markdown

Remember to check the function's help page first, as noted in the documentation:
"""
)

doc_query_chain = doc_query_prompt | current_llm | StrOutputParser()






# 定义图状态
class GraphState(TypedDict):
    """
    
    """
    question: str
    retrieve_bioinfo_tools_name: str
    tools: str
    documents: List[str] 
    web_search_results: str
    database_results: Dict[str, Any] 
    generation: str # 生成的答案 generation_anwser

# 定义图结构
workflow = StateGraph(GraphState)

# 路由节点
def route_question(state: GraphState) -> str:
    # 实现路由逻辑
    pass

workflow.add_node("router", route_question)


# RECOMMEND TOOLS LINE 
def retrieve_recommend_tools(state: GraphState) -> GraphState:
    """基于问题推荐相关工具
    
    Args:
        state: 图状态,包含用户问题
        
    Returns:
        state: 更新后的状态,包含推荐工具信息和生成的回答
    """
    question = state.question
    
    # 执行检索
    tools_docs = bioinfo_tools_retriever.invoke(question)
    tools_docs_str = "\n".join([doc.page_content for doc in tools_docs])

    return {"question": question, "tools_docs": tools_docs_str}

def generate_tool_recommendation(tools_info: List[dict], question: str) -> str:
    pass


workflow.add_node("tool_recommender", recommend_tools)

# DOCUMENT QUERY LINE
def retrieve_bioinfo_tools_documents_context(state: GraphState) -> GraphState:
    # 实现文档查询逻辑
    question = state['question']
    retrieve_bioinfo_tools_name = state['retrieve_bioinfo_tools_name']
    
    retriever = get_specific_doc_vectorstore_retriever(retrieve_bioinfo_tools_name)
    docs = retriever.invoke(question)
    docs_str = "\n".join([doc.page_content for doc in docs])
    
    return {"question": question, "documents": docs_str}

## 根据找到的文档内容生成回答

def generate_documents_query_anwser(state: GraphState):
    question = state['question']
    generation = doc_query_chain.invoke({'question':question,'documents':state['documents']})
    
    return {"question": question, "generation": generation}

workflow.add_node("document_query", query_documents)

# DATABASE QUERY LINE
def query_database(state: GraphState) -> GraphState:
    # 实现数据库查询逻辑
    pass

workflow.add_node("database_query", query_database)

# 生成答案节点
def generate_answer(state: GraphState) -> GraphState:

    
    return state

workflow.add_node("answer_generator", generate_answer)

# 定义边和条件
workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    lambda x: x["next_step"],
    {
        "tool_recommender": "tool_recommender",
        "document_query": "document_query",
        "database_query": "database_query",
    }
)
workflow.add_edge("tool_recommender", "answer_generator")
workflow.add_edge("document_query", "answer_generator")
workflow.add_edge("database_query", "answer_generator")
workflow.add_edge("answer_generator", END)

# 编译图
app = workflow.compile()