from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain.schema import Document, BaseMessage
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import Tool
from langchain.tools.retriever import create_retriever_tool

from langchain_core.messages import HumanMessage, AIMessage
from langchain_milvus import Milvus
from bridge_llm.llm_ollama import embeddings_bge_m3
from bridge_llm.llm_openai import chat_openai
from langchain_community.document_loaders import UnstructuredMarkdownLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter
from langchain_community.tools.tavily_search import TavilySearchResults
import os
import json

current_embedding_model = embeddings_bge_m3
current_llm = chat_openai

## 生信工具文档库检索

## Init vectorstores

# 初始化生信工具文档库
def init_bioconductor_docs_vectorstores(
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

def init_bioconda_docs_vectorstores(
        docs_dir:str="/home/awgao/BioinfoGPT/data/documents/bioconda_44",
        vector_db_path:str="/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db"
) -> Dict[str, Milvus]:
    """初始化bioconda工具文档向量数据库"""
    vectorstores = {}
    embeddings = current_embedding_model
    
    # Markdown专用分割器
    text_splitter = MarkdownTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    
    for tool_dir in os.listdir(docs_dir):
        tool_path = os.path.join(docs_dir, tool_dir)
        if not os.path.isdir(tool_path):
            continue
            
        try:
            # 加载所有markdown文件
            md_files = [f for f in os.listdir(tool_path) if f.endswith('.md')]
            tool_docs = []
            
            for md_file in md_files:
                loader = UnstructuredMarkdownLoader(
                    os.path.join(tool_path, md_file),
                    encoding='utf-8'
                )
                docs = loader.load()
                
                # 添加元数据
                for doc in docs:
                    doc.metadata.update({
                        "tool_name": tool_dir,
                        "source": "Bioconda",
                        "doc_type": "manual",
                        "file_name": md_file
                    })
                tool_docs.extend(docs)
            
            # 分割文档
            splits = text_splitter.split_documents(tool_docs)
            
            # 创建向量存储
            vectorstore = Milvus(
                embedding_function=embeddings,
                collection_name=f"bioconda_{tool_dir}",
                connection_args={"uri": vector_db_path},
                auto_id=True,
                drop_old=True
            )
            
            vectorstore.add_documents(splits)
            vectorstores[tool_dir] = vectorstore
            print(f"成功处理bioconda工具: {tool_dir}")
            
        except Exception as e:
            print(f"处理 {tool_dir} 时出错: {str(e)}")
    
    return vectorstores

# 加载已存在的向量数据库collections
def load_existing_docs_vectorstores(
        vector_db_path:str="/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db",
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


def create_tool_retrievers() -> List[Tool]:
    """创建所有工具的检索器"""
    tools = []
    
    # 加载bioconductor工具
    bioconductor_stores = load_existing_docs_vectorstores(
        vector_db_path="/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db"
    )
    
    for tool_name, vectorstore in bioconductor_stores.items():
        retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
        tool = create_retriever_tool(
            retriever,
            f"search_{tool_name}_docs",
            f"Search documentation for the Bioconductor tool {tool_name} to answer questions about usage, parameters, and examples."
        )
        tools.append(tool)
    
    # 加载bioconda工具
    bioconda_stores = load_existing_docs_vectorstores(
        vector_db_path="/home/awgao/BioinfoGPT/data/vector_db/milvus_tools.db",
        docs_dir="/home/awgao/BioinfoGPT/data/documents/bioconda_44"
    )
    
    for tool_name, vectorstore in bioconda_stores.items():
        retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
        tool = create_retriever_tool(
            retriever,
            f"search_{tool_name}_docs",
            f"Search documentation for the Bioconda tool {tool_name} to answer questions about installation, usage and examples."
        )
        tools.append(tool)
    
    # 添加Tavily搜索工具
    tools.append(TavilySearchResults())
    
    return tools


# 文档问答 RAG chain

## prompt 
doc_query_prompt = PromptTemplate(
    input_variables=["question", "context"],
    template="""
As a professional bioinformatics analyst, please answer the user's question based on the software documentation.

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

# State Management
class AgentState(BaseModel):
    """Track RAG workflow state"""
    question: str
    current_docs: List[Document] = Field(default_factory=list)
    current_answer: Optional[str] = None 
    chat_history: List[BaseMessage] = Field(default_factory=list)
    should_retrieve: bool = True
    should_generate: bool = False
    should_refine: bool = False
    retrieval_attempts: int = 0
    max_attempts: int = 3

async def retrieve(state: AgentState) -> AgentState:
    """Retrieve relevant documents"""
    if not state.should_retrieve:
        return state
        
    try:
        tools = create_tool_retrievers()
        tool_enabled_llm = current_llm.bind_tools(tools)
        
        # Select tools and retrieve docs
        # ... existing tool selection logic ...
        
        state.should_retrieve = False
        state.should_generate = True
        
    except Exception as e:
        state.current_answer = f"Retrieval error: {str(e)}"
        state.should_retrieve = False
        
    return state

async def generate(state: AgentState) -> AgentState:
    """Generate answer from retrieved docs"""
    if not state.should_generate:
        return state
        
    try:
        # ... existing answer generation logic ...
        
        state.should_generate = False
        state.should_refine = True
        
    except Exception as e:
        state.current_answer = f"Generation error: {str(e)}"
        state.should_generate = False
        
    return state

async def refine(state: AgentState) -> AgentState:
    """Decide whether to continue retrieval"""
    if not state.should_refine:
        return state
        
    try:
        eval_prompt = ChatPromptTemplate.from_messages([
            ("system", """Evaluate if the current answer is satisfactory:
            1. Is it complete and accurate?
            2. Does it need more context?
            Return: {"needs_refinement": true/false, "reason": "explanation"}"""),
            ("user", f"Question: {state.question}\nAnswer: {state.current_answer}")
        ])
        
        chain = eval_prompt | current_llm | StrOutputParser()
        result = await chain.ainvoke({})
        evaluation = json.loads(result)
        
        if evaluation["needs_refinement"] and state.retrieval_attempts < state.max_attempts:
            state.retrieval_attempts += 1
            state.should_retrieve = True
        else:
            state.should_refine = False
            
    except Exception as e:
        state.current_answer = f"Refinement error: {str(e)}"
        state.should_refine = False
        
    return state

def create_rag_graph() -> StateGraph:
    """Create enhanced RAG workflow graph"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate) 
    workflow.add_node("refine", refine)
    
    # Add edges
    workflow.add_conditional_edges(
        "retrieve",
        lambda x: "generate" if x.should_generate else END
    )
    
    workflow.add_conditional_edges(
        "generate",
        lambda x: "refine" if x.should_refine else END
    )
    
    workflow.add_conditional_edges(
        "refine",
        lambda x: "retrieve" if x.should_retrieve else END
    )
    
    workflow.set_entry_point("retrieve")
    
    return workflow.compile()

# Usage
async def get_rag_response(
    question: str,
    chat_history: Optional[List[BaseMessage]] = None
) -> Tuple[str, List[BaseMessage]]:
    """运行增强版RAG工作流"""
    graph = create_rag_graph()
    
    config = {
        "recursion_limit": 10,
        "timeout": 30  # 30秒超时
    }
    
    state = AgentState(
        question=question,
        chat_history=chat_history or []
    )
    
    try:
        result = await graph.stream(state, config)
        return result.current_answer, result.chat_history
    except Exception as e:
        error_msg = f"工作流执行错误: {str(e)}"
        return error_msg, chat_history or []


