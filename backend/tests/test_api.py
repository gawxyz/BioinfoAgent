import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Message, ChatRequest, ChatResponse

client = TestClient(app)

def test_chat_endpoint():
    # Test valid request
    request_data = {
        "messages": [
            {"role": "user", "content": "What tools can I use for sequence alignment?"}
        ]
    }
    response = client.post("/api/chat", json=request_data)
    assert response.status_code == 200
    assert "response" in response.json()
    
    # Test empty messages
    request_data = {
        "messages": []
    }
    response = client.post("/api/chat", json=request_data)
    assert response.status_code == 400
    assert "No messages provided" in response.json()["detail"]
    
    # Test invalid role
    request_data = {
        "messages": [
            {"role": "assistant", "content": "This should fail"}
        ]
    }
    response = client.post("/api/chat", json=request_data)
    assert response.status_code == 400
    assert "Last message must be from user" in response.json()["detail"]
    
    # Test chat history
    request_data = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "What bioinformatics tools do you know?"}
        ]
    }
    response = client.post("/api/chat", json=request_data)
    assert response.status_code == 200
    assert "response" in response.json() 