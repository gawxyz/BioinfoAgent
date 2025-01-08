# BioinfoGPT

BioinfoGPT 是一个基于 LangGraph 的生物信息学智能助手，集成了工具推荐、文档问答和数据库查询等功能，旨在帮助研究人员更高效地解决生物信息学分析问题。

## 🌟 核心功能

### 1️⃣ 生物信息分析工具推荐

智能化的生信工具推荐系统：

- 基于本地 SQLite 的生物信息工具知识库
- 使用向量检索匹配用户需求
- 智能分析并生成个性化工具推荐
- 提供工具的详细使用说明
- 支持多语言查询（中文、英文、韩文）

### 2️⃣ 生物信息软件文档智能问答

基于 Self-reflection RAG 的智能问答系统：

- 智能文档路由
  - 自动定位相关软件文档
  - 动态调用在线搜索补充
  - 多轮交互优化答案质量

- 文档检索增强
  - 精准提取相关文档片段
  - 持续评估文档相关性
  - 动态扩展检索范围

- 答案质量保证
  - 持续评估答案质量
  - 自动补充必要信息
  - 综合多源信息生成答案

### 3️⃣ 生物信息数据库智能体

集成多个生物信息数据库的智能查询功能：

- NCBI 数据库查询
  - 基因信息检索 (Gene)
  - SNP 变异查询
  - 序列数据库搜索

- BLAST 序列分析
  - 支持多种 BLAST 类型
  - 智能解析比对结果
  - 自动选择最佳策略

## 🚀 快速开始

### 环境配置
```bash
# 克隆仓库
git clone https://github.com/yourusername/BioinfoGPT.git
cd BioinfoGPT
# 创建虚拟环境
python -m venv venv
# 激活环境
source venv/bin/activate # Linux/Mac
或
venv\Scripts\activate # Windows
# 安装依赖
pip install -r requirements.txt
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件填写必要配置
```
### 启动服务

```bash
python src/main.py
```

服务将在 http://localhost:8000 启动，API 文档：http://localhost:8000/docs


## 📚 API 使用

BioinfoGPT 提供兼容 OpenAI 格式的 API：

```python

import openai

openai.api_base = "http://localhost:8000/v1"
openai.api_key = "dummy" # 可以是任意值
# 工具推荐示例
response = openai.ChatCompletion.create(
model="bioinfo-tool-recommend",
messages=[{"role": "user", "content": "推荐RNA-seq分析工具"}]
)
# 文档问答示例
response = openai.ChatCompletion.create(
model="bioinfo-doc-qa",
messages=[{"role": "user", "content": "如何使用DESeq2分析差异表达"}]
)
# 数据库查询示例
response = openai.ChatCompletion.create(
model="bioinfo-db-agent",
messages=[{"role": "user", "content": "查询BRCA1基因信息"}]
)
# 自动路由示例
response = openai.ChatCompletion.create(
model="bioinfo-graph",
messages=[{"role": "user", "content": "你的问题"}]
)
```

## 📦 项目结构
```
BioinfoGPT/
├── src/
│ ├── main.py # FastAPI 主程序
│ ├── router.py # 查询路由逻辑
│ ├── bioinfogpt_graph.py # 主工作流程图
│ ├── docQA.py # 文档问答系统
│ ├── toolRecommend.py # 工具推荐系统
│ ├── langchainA.py # 数据库查询智能体
│ └── bridge_llm/ # LLM 模型集成
├── data/
│ ├── tools/ # 工具库数据
│ ├── documents/ # 软件文档
│ └── vector_db/ # 向量数据库
└── requirements.txt # 项目依赖
```


## 🛠️ 支持的模型

- bioinfo-tool-recommend: 工具推荐智能体
- bioinfo-doc-qa: 文档问答智能体
- bioinfo-db-agent: 数据库查询智能体
- bioinfo-graph: 综合路由智能体


# BioinfoGPT Frontend

A Next.js based frontend for BioinfoGPT - an intelligent assistant for bioinformatics research.

## Demo

[Live Demo](https://bioinfo-gpt.vercel.app)

![BioinfoGPT Demo 1](./doc/pic/pic(1).png)
![BioinfoGPT Demo 2](./doc/pic/pic(2).png)
![BioinfoGPT Demo 3](./doc/pic/pic(3).png)
![BioinfoGPT Demo 4](./doc/pic/pic(4).png)
![BioinfoGPT Demo 5](./doc/pic/pic(5).png)


## Tech Stack

```
frontend/
├── app/ # Next.js app router pages
│ ├── api/ # API routes
│ ├── chat/ # Chat interface
│ ├── docs/ # Documentation browser
│ ├── solutions/ # Solutions database
│ └── tools/ # Tools database
├── components/ # React components
│ ├── ui/ # UI components from shadcn/ui
│ └── navigation.tsx # Navigation component
└── lib/ # Utility functions
```
## Getting Started

1. Install dependencies:

```bash
npm install
```

2. Run the development server:

```bash
npm run dev
```


## 👨‍💻 开发指南

- 代码风格遵循 PEP 8
- 使用 typing 进行类型注解
- 函数必须包含 docstring
- 保持函数单一职责
- 编写单元测试

## 📄 许可证

[MIT License](LICENSE)

## 🤝 贡献指南

欢迎提交 Pull Request 或创建 Issue。
