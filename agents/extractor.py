"""
Extractor Agent: 长链推理证据提取
从冗余召回的文档中提取最小且连贯的证据链
"""

from typing import List, Dict
import re

class ExtractorAgent:
    def __init__(self, llm_client):
        self.llm = llm_client
        
    def extract_evidence_chain(
        self, 
        retrieved_docs: List[str], 
        sub_task_query: str,
        context_window_limit: int = 8000
    ) -> Dict:
        """
        长链推理核心方法
        
        Args:
            retrieved_docs: 召回的原始文档片段（可能包含大量冗余）
            sub_task_query: 当前子任务的检索查询
            context_window_limit: Token限制
            
        Returns:
            包含证据链和置信度的字典
        """
        # Step 1: 文档预过滤（去除明显不相关）
        filtered = [doc for doc in retrieved_docs if self._quick_filter(doc, sub_task_query)]
        
        # Step 2: 构建时间线/逻辑链（长链推理的关键）
        timeline = self._build_timeline(filtered)
        
        # Step 3: 调用LLM提取最小证据链
        prompt = f"""
        你是一个证据提取专家。从以下文档中提取与查询「{sub_task_query}」最相关的**最小证据链**。
        
        要求：
        1. 只保留必要的推理步骤，去掉无关描述
        2. 使用 "→" 符号连接因果/时序关系
        3. 如果文档中存在冲突信息，保留置信度更高的一条
        
        文档内容：
        {'---'.join(filtered[:5])}
        
        输出格式：
        证据链：[步骤1 → 步骤2 → 步骤3]
        关键时间戳：xxx
        置信度：高/中/低
        不相关信息摘要：xxx（如果存在）
        """
        
        # 实际LLM调用会返回结构化结果
        evidence = self._simulate_llm_extraction(sub_task_query)
        return evidence
    
    def _quick_filter(self, doc: str, query: str) -> bool:
        """快速关键词过滤"""
        keywords = query.lower().split()
        doc_lower = doc.lower()
        return any(kw in doc_lower for kw in keywords[:3])
    
    def _build_timeline(self, docs: List[str]) -> List[Dict]:
        """
        从文档中提取时间线（长链推理的骨架）
        实际实现会提取时间戳、事件、状态变更
        """
        timeline = []
        for doc in docs:
            # 正则提取时间戳模式
            timestamps = re.findall(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', doc)
            if timestamps:
                timeline.append({
                    "timestamp": timestamps[0],
                    "content": doc[:200]
                })
        return sorted(timeline, key=lambda x: x["timestamp"])
    
    def _simulate_llm_extraction(self, query: str) -> Dict:
        """模拟长链推理输出（实际使用时替换为真实LLM调用）"""
        if "网关" in query or "gateway" in query.lower():
            return {
                "evidence_chain": "网关信号RSSI < -70dBm → 触发重连机制 → 连续失败3次 → 标记为离线",
                "key_timestamp": "2026-05-14 03:21:45",
                "confidence": "高",
                "irrelevant_summary": "共过滤掉2段Wi-Fi通用配置文档（与具体故障无关）"
            }
        else:
            return {
                "evidence_chain": "APP进程OOM → 系统kill → 用户感知为'卡死'",
                "key_timestamp": None,
                "confidence": "中",
                "irrelevant_summary": "无"
            }


# 测试长链推理
if __name__ == "__main__":
    extractor = ExtractorAgent(None)
    mock_docs = [
        "2026-05-14 03:21:45 [ERROR] gateway offline, RSSI=-72dBm",
        "网关通用配置：建议放置在开阔区域",
        "2026-05-14 03:21:48 [WARN] reconnect attempt 1 failed",
        "Wi-Fi 2.4GHz频段干扰源较多"
    ]
    result = extractor.extract_evidence_chain(mock_docs, "网关掉线原因")
    print(f"提取的证据链：{result['evidence_chain']}")
    print(f"置信度：{result['confidence']}")
