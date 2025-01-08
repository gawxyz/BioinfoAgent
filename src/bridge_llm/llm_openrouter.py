import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 使用相对路径加载.env文件
# current_dir = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(current_dir, '.env')
env_path = '/home/awgao/BioinfoGPT/.env'
load_dotenv(dotenv_path=env_path)

chat_openrouter = ChatOpenAI(
    # model="google/gemini-2.0-flash-thinking-exp:free", 
    model= "meta-llama/llama-3.2-90b-vision-instruct:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base=os.getenv("OPENROUTER_API_BASE_URL"),
    temperature=0,  # 可以根据需要调整
)

# 示例用法（如果直接运行此文件）
if __name__ == "__main__":
    question = "常见的十字花科植物有哪些？"
    answer = chat_openrouter.invoke(question)
    print(f"问题：{question}")
    print(f"回答：{answer.content}")


