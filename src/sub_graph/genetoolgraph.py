from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from bridge_llm.llm_doubao import chat_doubao
from tools.ncbitools import get_gene_info, get_snp_info
from langchain_core.tools import Tool
import logging
from pydantic import BaseModel, Field

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义工具的输入模型
class GeneQuery(BaseModel):
    query: str = Field(
        description="基因查询字符串，可以是基因符号名称(如BRCA1)、ensembl ID或疾病名称"
    )

class SNPQuery(BaseModel):
    query: str = Field(
        description="SNP查询字符串，可以是rs ID（带或不带rs前缀）"
    )

def safe_get_gene_info(query: GeneQuery) -> str:
    """带错误处理的基因信息获取"""
    try:
        result = get_gene_info(query.query)
        if not result or result.strip() == "":
            return f"未找到关于 {query.query} 的信息"
        return result
    except Exception as e:
        logger.error(f"获取基因信息失败: {str(e)}")
        return f"获取基因信息时发生错误: {str(e)}"

def safe_get_snp_info(query: SNPQuery) -> str:
    """带错误处理的SNP信息获取"""
    try:
        result = get_snp_info(query.query)
        if not result or result.strip() == "":
            return f"未找到关于 {query.query} 的信息"
        return result
    except Exception as e:
        logger.error(f"获取SNP信息失败: {str(e)}")
        return f"获取SNP信息时发生错误: {str(e)}"

# 创建工具
tools = [
    Tool(
        name="get_gene_info",
        description="获取基因信息，用于查询基因的详细信息",
        func=safe_get_gene_info,
        args_schema=GeneQuery
    ),
    Tool(
        name="get_snp_info",
        description="获取SNP信息，用于查询SNP的详细信息",
        func=safe_get_snp_info,
        args_schema=SNPQuery
    )
]

# 创建工具节点
tool_node = ToolNode(tools)

# 移除 system_message，直接绑定工具
model_with_tools = chat_doubao.bind_tools(tools=tools)

def should_continue(state: MessagesState) -> Literal["tools", "END"]:
    """决定是否继续执行工具调用"""
    messages = state["messages"]
    last_message = messages[-1]
    # 添加调用次数限制
    tool_call_count = sum(1 for msg in messages if getattr(msg, "tool_calls", None))
    if last_message.tool_calls and tool_call_count < 2:  # 限制最多调用一次
        return "tools"
    return END

def call_model(state: MessagesState) -> Dict[str, Any]:
    """调用模型处理消息"""
    try:
        messages = state["messages"]
        # 在消息列表开头添加系统提示
        system_prompt = ("system", """你是一个生物信息学助手。使用提供的工具来回答问题。
如果工具返回错误或空结果，请直接告知用户没有找到相关信息，不要重复尝试。
每个问题最多使用工具一次。""")
        
        all_messages = [system_prompt] + messages
        response = model_with_tools.invoke(all_messages)
        return {"messages": [response]}
    except Exception as e:
        logger.error(f"模型调用失败: {str(e)}")
        error_message = f"模型处理失败: {str(e)}"
        return {"messages": [("assistant", error_message)]}

# 创建工作流图
workflow = StateGraph(MessagesState)

# 添加节点
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# 添加边
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# 编译图
app = workflow.compile()

def process_query(query: str):
    """处理查询并返回结果"""
    try:
        # 添加系统提示
        system_prompt = ("system", """你是一个生物信息学助手。使用提供的工具来回答问题。
如果工具返回错误或空结果，请直接告知用户没有找到相关信息，不要重复尝试。
每个问题最多使用工具一次。""")
        
        response = app.invoke(
            {
                "messages": [system_prompt, ("human", query)]
            },
            {"recursion_limit": 5}
        )
        
        for message in response["messages"]:
            print(f"{message.type.upper()}: {message.content}\n")
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        print(f"错误: {str(e)}\n")

if __name__ == "__main__":
    # 测试案例
    test_queries = [
        "What is the official gene symbol of C20orf195",
        "Which gene is SNP rs1217074595 associated with?",
    ]
    
    for query in test_queries:
        print(f"查询: {query}")
        print("="*50)
        process_query(query)
        print("="*50)
