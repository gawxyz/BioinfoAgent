from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum

from bioinfogpt_graph import app as bioinfo_graph
from docQA import get_rag_response
from toolRecommend import bioinfo_tools_retriever, recommend_tools_chain
from langchainA import agent as bio_db_agent
from langchain_core.messages import HumanMessage

app = FastAPI(title="BioinfoGPT API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"

class Message(BaseModel):
    role: Role
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{id}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    try:
        # 提取最后一条用户消息
        user_message = next(
            (msg.content for msg in reversed(request.messages) if msg.role == Role.user),
            None
        )
        if not user_message:
            raise HTTPException(status_code=400, message="No user message found")

        response_content = ""
        usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # 根据model选择不同的处理流程
        if request.model == "bioinfo-tool-recommend":
            # 工具推荐智能体
            docs = bioinfo_tools_retriever.invoke(user_message)
            response_content = recommend_tools_chain.invoke({
                "question": user_message,
                "tools_docs": docs
            })

        elif request.model == "bioinfo-doc-qa":
            # 文档问答智能体
            response_content, _ = await get_rag_response(user_message)

        elif request.model == "bioinfo-db-agent":
            # 数据库查询智能体
            response = bio_db_agent.invoke({
                "messages": [HumanMessage(content=user_message)]
            })
            response_content = response["messages"][-1].content

        elif request.model == "bioinfo-graph":
            # 综合路由智能体
            response = bioinfo_graph.invoke({
                "messages": [HumanMessage(content=user_message)]
            })
            response_content = response["messages"][-1].content

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model: {request.model}"
            )

        return ChatCompletionResponse(
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            usage=usage
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 