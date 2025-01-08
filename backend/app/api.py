from fastapi import APIRouter, HTTPException
from .models import ChatRequest, ChatResponse, Message
from langchain_core.messages import HumanMessage, AIMessage
import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_path = str(Path(__file__).parent.parent.parent / "src")
sys.path.append(src_path)

from sub_graph.langchainA import agent

router = APIRouter()

@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
            
        # Extract the last message from the chat history
        last_message = request.messages[-1]
        
        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # Convert chat history to LangChain format
        history = []
        for msg in request.messages[:-1]:  # exclude last message
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                history.append(AIMessage(content=msg.content))
        
        # Add the last message
        history.append(HumanMessage(content=last_message.content))
        
        # Use the agent to process the message
        response = agent.invoke({
            "messages": history
        })
        
        # Extract the assistant's response
        assistant_message = response["messages"][-1].content
        
        return ChatResponse(response=assistant_message)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
