from typing import Dict, Any, List
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
import re

class Router:
    """路由器类，用于确定使用哪个智能体处理查询"""
    
    @staticmethod
    def route_query(query: str) -> str:
        """
        根据查询内容确定使用哪个智能体
        
        Returns:
            str: 'tool-recommend', 'doc-qa', 'bio-db', 或 'unknown'
        """
        # 工具推荐模式的关键词
        tool_keywords = [
            r"工具", r"软件", r"推荐", r"用什么", r"怎么做",
            r"tool", r"software", r"recommend", r"how to",
            r"도구", r"소프트웨어", r"추천"
        ]
        
        # 文档问答模式的关键词
        doc_keywords = [
            r"怎么使用", r"参数", r"文档", r"说明",
            r"how to use", r"parameter", r"document",
            r"사용 방법", r"매개변수", r"문서"
        ]
        
        # 生物数据库查询模式的关键词
        bio_db_keywords = [
            r"基因", r"序列", r"BLAST", r"SNP",
            r"gene", r"sequence", r"protein",
            r"유전자", r"서열", r"단백질"
        ]
        
        # 转换查询为小写以进行匹配
        query_lower = query.lower()
        
        # 检查关键词匹配
        if any(re.search(kw.lower(), query_lower) for kw in tool_keywords):
            return "tool-recommend"
        elif any(re.search(kw.lower(), query_lower) for kw in doc_keywords):
            return "doc-qa"
        elif any(re.search(kw.lower(), query_lower) for kw in bio_db_keywords):
            return "bio-db"
        
        # 默认返回工具推荐
        return "tool-recommend" 