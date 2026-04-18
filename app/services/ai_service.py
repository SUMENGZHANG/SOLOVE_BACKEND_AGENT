"""
AI 服务 - 接入 Qwen 大模型

用于 Agent 聊天、任务生成、情绪分析等
"""

import json
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI

from ..core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务类"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        # 使用 OpenAI 兼容接口（阿里云 DashScope 支持）
        self.client = None
        self.model = settings.AI_MODEL
        
        if settings.AI_API_KEY and settings.AI_API_BASE:
            self.client = OpenAI(
                api_key=settings.AI_API_KEY,
                base_url=settings.AI_API_BASE
            )
            logger.info(f"AI 服务已初始化，模型：{self.model}")
        else:
            logger.warning("AI_API_KEY 或 AI_API_BASE 未配置，AI 服务将使用占位响应")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        与 AI 对话
        
        Args:
            messages: 对话历史 [{"role": "user/assistant", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数 (0-1)
            max_tokens: 最大 token 数
        
        Returns:
            AI 回复的内容
        """
        # 构建消息列表
        full_messages = []
        
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        
        full_messages.extend(messages)
        
        # 如果没有配置 API，返回占位响应
        if not self.client:
            return self._fallback_response(messages)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"AI 调用失败：{e}")
            return f"抱歉，我现在有点累，但我会一直陪着你。（系统提示：AI 服务暂时不可用 - {str(e)}）"
    
    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """
        占位响应（当 AI 服务未配置时使用）
        
        模拟一个温暖的陪伴者角色
        """
        last_message = messages[-1].get("content", "") if messages else ""
        
        # 简单的关键词匹配
        if any(word in last_message for word in ["难过", "伤心", "委屈", "累", "烦"]):
            return "我能感受到你现在不太好受。没关系，我在这里陪着你，想说什么都可以告诉我。🫂"
        elif any(word in last_message for word in ["开心", "高兴", "棒", "好"]):
            return "太好了！看到你心情不错，我也为你开心！继续保持这份美好～ ✨"
        elif any(word in word in last_message for word in ["任务", "计划", "今天"]):
            return "我来帮你想想今天可以做些什么让自己感觉更好的小事，好吗？"
        else:
            return "我收到你的消息了。我会认真倾听，陪你一起面对。想说什么都可以告诉我。💙"
    
    def analyze_mood(self, text: str) -> Dict[str, Any]:
        """
        分析用户情绪
        
        Returns:
            {
                "mood_score": 5.0,  # 1-10 分
                "mood_label": "平静",  # 情绪标签
                "keywords": ["关键词"]
            }
        """
        system_prompt = """你是一个情绪分析助手。请分析用户文本的情绪状态，返回 JSON 格式：
{
    "mood_score": 5.0,  // 1-10 分，1=非常低落，10=非常积极
    "mood_label": "平静",  // 情绪标签：低落/焦虑/平静/开心/兴奋等
    "keywords": ["关键词 1", "关键词 2"]  // 情绪关键词
}

只返回 JSON，不要其他内容。"""
        
        messages = [{"role": "user", "content": f"分析这段文字的情绪：{text}"}]
        
        if not self.client:
            # 占位返回
            return {
                "mood_score": 5.0,
                "mood_label": "平静",
                "keywords": []
            }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            logger.error(f"情绪分析失败：{e}")
            return {
                "mood_score": 5.0,
                "mood_label": "平静",
                "keywords": []
            }
    
    def generate_suggested_tasks(
        self,
        user_mood: float,
        conversation_context: str
    ) -> List[Dict[str, Any]]:
        """
        根据用户情绪和对话内容，生成建议任务
        
        Args:
            user_mood: 用户当前情绪分 (1-10)
            conversation_context: 对话上下文
        
        Returns:
            建议任务列表 [{"name": "...", "description": "...", "category": "..."}]
        """
        system_prompt = f"""你是一个温暖的陪伴助手。根据用户当前情绪状态，生成 1-3 个简单的自我关怀任务。

用户当前情绪分：{user_mood}/10
- 1-3 分：情绪低落，需要温和的安慰和非常简单的任务
- 4-6 分：情绪平稳，适合日常自我关怀
- 7-10 分：情绪积极，可以尝试稍有挑战的任务

任务类型包括：运动、阅读、冥想、社交、自我关怀、创意表达

返回 JSON 格式：
[
    {{
        "name": "任务名称",
        "description": "任务描述",
        "category": "运动/阅读/冥想/社交/自我关怀/创意表达",
        "estimated_time": 10
    }}
]

只返回 JSON 数组，不要其他内容。"""
        
        messages = [{"role": "user", "content": f"对话上下文：{conversation_context}"}]
        
        if not self.client:
            # 占位返回
            return [
                {
                    "name": "深呼吸 3 次",
                    "description": "找个舒服的姿势，深呼吸 3 次，感受气息进出身体",
                    "category": "冥想",
                    "estimated_time": 2
                }
            ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=0.5,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result if isinstance(result, list) else [result]
        
        except Exception as e:
            logger.error(f"任务生成失败：{e}")
            return [
                {
                    "name": "深呼吸 3 次",
                    "description": "找个舒服的姿势，深呼吸 3 次，感受气息进出身体",
                    "category": "冥想",
                    "estimated_time": 2
                }
            ]


# 全局 AI 服务实例
ai_service = AIService()
