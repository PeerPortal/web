#!/usr/bin/env python3
"""
查询分类器 - 智能分析用户查询意图
预处理用户查询，判断最适合的工具需求
"""

import re
from typing import Dict, List, Tuple, Any

class QueryClassifier:
    """智能查询分类器 - 基础版本"""
    
    def __init__(self):
        # 知识库指标关键词
        self.knowledge_base_keywords = [
            # 直接指标
            "案例", "成功案例", "申请案例", "知识库", "文档", "上传的", "根据",
            
            # 学校名称 (常见顶级院校)
            "CMU", "Carnegie Mellon", "卡内基梅隆",
            "Stanford", "斯坦福",
            "MIT", "麻省理工",
            "Harvard", "哈佛", 
            "Berkeley", "UC Berkeley", "伯克利",
            "Princeton", "普林斯顿",
            "Yale", "耶鲁",
            "Columbia", "哥伦比亚",
            "UPenn", "宾夕法尼亚",
            "Cornell", "康奈尔",
            
            # 申请相关具体内容
            "推荐信", "recommendation letter", "推荐人",
            "文书写作", "个人陈述", "SOP", "personal statement",
            "面试准备", "面试技巧", "interview",
            "申请流程", "申请步骤", "申请时间", "申请规划",
            "申请费用", "申请预算", "费用预算",
            "录取结果", "offer", "录取案例",
            "申请材料", "申请文档", "材料准备",
            
            # 背景相关
            "背景要求", "申请条件", "入学要求",
            "实习经历", "项目经验", "研究经历",
            "工作经验", "课外活动"
        ]
        
        # 分数相关正则模式
        self.score_patterns = [
            r"GPA\s*[:\s]*\d+\.\d+",     # GPA 3.8
            r"托福\s*[:\s]*\d+",          # 托福 105
            r"TOEFL\s*[:\s]*\d+",        # TOEFL 105
            r"雅思\s*[:\s]*\d+\.\d+",     # 雅思 7.5
            r"IELTS\s*[:\s]*\d+\.\d+",   # IELTS 7.5
            r"GRE\s*[:\s]*\d+",          # GRE 325
            r"GMAT\s*[:\s]*\d+",         # GMAT 720
        ]
        
        # 网络搜索指标
        self.web_search_keywords = [
            # 时间相关
            "2024", "2025", "最新", "当前", "最近", "今年", "现在",
            "latest", "current", "recent", "new",
            
            # 排名和统计
            "排名", "ranking", "录取率", "acceptance rate",
            "申请要求", "requirements", "admission requirements",
            "政策", "policy", "新闻", "news",
            "变化", "变更", "更新", "update",
            
            # 趋势分析
            "趋势", "trend", "统计", "statistics",
            "数据", "data", "报告", "report"
        ]
        
        # 知识库相关的语义关键词
        self.kb_semantic_keywords = [
            "申请经验", "经验分享", "申请建议", "建议",
            "怎么写", "如何写", "怎么准备", "如何准备",
            "技巧", "要点", "方法", "步骤",
            "注意事项", "准备什么", "需要什么",
            "申请攻略", "申请指南", "留学指南",
            "写作指导", "准备指导", "申请指导"
        ]
        
        print("✅ 查询分类器初始化完成")
    
    def has_kb_keywords(self, query: str) -> Tuple[bool, List[str]]:
        """检查查询是否包含知识库关键词"""
        query_lower = query.lower()
        found_keywords = []
        
        # 检查关键词
        for keyword in self.knowledge_base_keywords:
            if keyword.lower() in query_lower:
                found_keywords.append(keyword)
        
        # 检查语义关键词
        for keyword in self.kb_semantic_keywords:
            if keyword.lower() in query_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def has_score_patterns(self, query: str) -> Tuple[bool, List[str]]:
        """检查查询是否包含分数模式"""
        found_patterns = []
        
        for pattern in self.score_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            found_patterns.extend(matches)
        
        return len(found_patterns) > 0, found_patterns
    
    def has_web_indicators(self, query: str) -> Tuple[bool, List[str]]:
        """检查查询是否包含网络搜索指标"""
        query_lower = query.lower()
        found_indicators = []
        
        for indicator in self.web_search_keywords:
            if indicator.lower() in query_lower:
                found_indicators.append(indicator)
        
        return len(found_indicators) > 0, found_indicators
    
    def semantic_similarity_score(self, query: str) -> float:
        """计算查询与知识库模板的简单相似度 (基于关键词重叠)"""
        query_lower = query.lower()
        overlap_count = 0
        
        # 简单的关键词重叠计算
        for keyword in self.kb_semantic_keywords:
            if keyword.lower() in query_lower:
                overlap_count += 1
        
        # 归一化得分
        max_possible = min(len(self.kb_semantic_keywords), 5)  # 最多考虑5个匹配
        return min(overlap_count / max_possible, 1.0)
    
    def classify_query(self, query: str) -> Dict[str, Any]:
        """综合分类查询"""
        result = {
            "query": query,
            "recommended_tool": "knowledge_base_retriever",  # 默认推荐
            "confidence": 0.0,
            "reasons": [],
            "analysis": {}
        }
        
        # 1. 关键词匹配
        has_kb_kw, kb_keywords = self.has_kb_keywords(query)
        has_scores, score_patterns = self.has_score_patterns(query)
        has_web_kw, web_keywords = self.has_web_indicators(query)
        
        # 2. 语义相似度
        semantic_score = self.semantic_similarity_score(query)
        
        # 3. 综合判断
        kb_score = 0.0
        web_score = 0.0
        
        # 知识库得分计算
        if has_kb_kw:
            kb_score += 0.4
            result["reasons"].append(f"包含知识库关键词: {kb_keywords}")
        
        if has_scores:
            kb_score += 0.3
            result["reasons"].append(f"包含具体分数: {score_patterns}")
        
        if semantic_score > 0.5:
            kb_score += 0.3
            result["reasons"].append(f"语义相似度高: {semantic_score:.2f}")
        
        # 网络搜索得分计算
        if has_web_kw:
            web_score += 0.6
            result["reasons"].append(f"包含网络搜索指标: {web_keywords}")
        
        # 决策逻辑
        if kb_score > web_score and kb_score > 0.3:
            result["recommended_tool"] = "knowledge_base_retriever"
            result["confidence"] = kb_score
        elif web_score > 0.4:
            result["recommended_tool"] = "web_search"
            result["confidence"] = web_score
        else:
            # 默认策略：优先知识库
            result["recommended_tool"] = "knowledge_base_retriever"
            result["confidence"] = 0.5
            result["reasons"].append("默认策略：优先使用知识库")
        
        # 分析详情
        result["analysis"] = {
            "kb_keywords_found": kb_keywords,
            "score_patterns_found": score_patterns,
            "web_keywords_found": web_keywords,
            "semantic_similarity": semantic_score,
            "kb_score": kb_score,
            "web_score": web_score
        }
        
        return result
    
    def should_use_knowledge_base(self, query: str, threshold: float = 0.3) -> bool:
        """简化的知识库使用判断"""
        classification = self.classify_query(query)
        return (classification["recommended_tool"] == "knowledge_base_retriever" and 
                classification["confidence"] >= threshold)

# 创建全局实例
query_classifier = QueryClassifier()
