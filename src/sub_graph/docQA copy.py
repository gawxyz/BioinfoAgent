from typing import Dict
from langchain_milvus import Milvus
from bridge_llm.llm_ollama import embeddings_bge_m3
from bridge_llm.llm_deepseek import chat_openai
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter,MarkdownTextSplitter
import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

current_embedding_model = embeddings_bge_m3
current_llm = chat_openai

## 生信工具文档库检索

# 初始化生信工具文档库
def init_docs_vectorstores(
        docs_dir:str="/home/awgao/BioinfoGPT/data/documents/bioconductor_75",
        vector_db_path:str="/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db"
) -> Dict[str, Milvus]:
    """初始化生信工具文档向量数据库
    
    所有工具共用一个db文件,但使用不同的collection
    """
    vectorstores = {}
    
    # 初始化embedding模型
    embeddings = current_embedding_model
    
    # 文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        length_function=len,
    )
    
    # 遍历所有工具目录
    for tool_dir in os.listdir(docs_dir):
        tool_path = os.path.join(docs_dir, tool_dir)
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
                    connection_args={"uri": vector_db_path},  # 所有工具共用一个db
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
def load_existing_docs_vectorstores(
        vector_db_path:str="/home/awgao/BioinfoGPT/data/vector_db/Bioconductor_top_75",
        docs_dir:str="/home/awgao/BioinfoGPT/data/documents/bioconductor_75"
) -> Dict[str, Milvus]:
    """加载已存在的向量数据库collections
    """
    all_bioinfo_tools_docs_vectorstores_dict = {}
    
    # 初始化embedding模型
    embeddings = current_embedding_model
    
    # 遍历所有工具目录
    for tool_dir in os.listdir(docs_dir):
        if not os.path.isdir(os.path.join(docs_dir, tool_dir)):
            continue
            
        try:
            # 连接到对应的collection
            vectorstore = Milvus(
                embedding_function=embeddings,
                collection_name=f"bioinfo_{tool_dir}",
                connection_args={"uri": vector_db_path},
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
    
    all_bioinfo_tools_docs_vectorstores_dict = load_existing_docs_vectorstores()
    if toolname not in all_bioinfo_tools_docs_vectorstores_dict:
        raise ValueError(f"工具 {toolname} 不存在")
    return all_bioinfo_tools_docs_vectorstores_dict[toolname].as_retriever(search_kwargs={'k': 3})

# 文档问答 RAG chain

## prompt 
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

"""
)

## chain 
doc_query_chain = doc_query_prompt | current_llm | StrOutputParser()


