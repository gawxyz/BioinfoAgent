import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings

# 使用相对路径加载.env文件
# current_dir = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(current_dir, '.env')
env_path = '/home/awgao/BioinfoGPT/.env'
load_dotenv(dotenv_path=env_path)

# 从.env文件中获取base_url
OLLAMA_BASE_URL1 = os.getenv("OLLAMA_BASE_URL1")
OLLAMA_BASE_URL2 = os.getenv("OLLAMA_BASE_URL2")

# 定义模型实例
chat_ollama_llama31_json = ChatOllama(
    model="llama3.1",
    format="json",
    base_url=OLLAMA_BASE_URL1,
    temperature=0.1
)

chat_ollama_llama31 = ChatOllama(
    model="llama3.1",
    base_url=OLLAMA_BASE_URL1,
    temperature=0.1
)

chat_ollama_llama31_fp16 = ChatOllama(
    model="llama3.1:8b-instruct-fp16",
    base_url=OLLAMA_BASE_URL1,
    temperature=0.1
)

chat_ollama_llama32_3b_fp16 = ChatOllama(
    model="llama3.2:3b-instruct-fp16",
    base_url=OLLAMA_BASE_URL1,
    temperature=0
)

chat_ollama_llama31_fp16_json = ChatOllama(
    model="llama3.1:8b-instruct-fp16",
    base_url=OLLAMA_BASE_URL2,
    format="json",
    temperature=0.1
)

chat_ollama_llama31_70b = ChatOllama(
    model="llama3.1:70b",
    base_url=OLLAMA_BASE_URL2,
    temperature=0.1
)

embeddings_nomic = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=OLLAMA_BASE_URL1
)

embeddings_jina = OllamaEmbeddings(
    model="jina-embeddings-v2-base-en",
    base_url=OLLAMA_BASE_URL1
)

embeddings_bge_m3 = OllamaEmbeddings(
    model="bge-m3",
    base_url=OLLAMA_BASE_URL1
)

# 导出模型实例
__all__ = [
    "chat_ollama_llama31_json",
    "chat_ollama_llama31",
    "chat_ollama_llama31_fp16",
    "embeddings_nomic",
    "embeddings_jina",
    "embeddings_bge_m3"
]

# 示例用法（如果直接运行此文件）
if __name__ == "__main__":
    question = "常见的十字花科植物有哪些？"
    answer = chat_ollama_llama31.invoke(question)
    print(f"问题：{question}")
    print(f"回答：{answer.content}")
    answer = chat_ollama_llama31_70b.invoke(question)
    print(f"70B回答：{answer.content}")
