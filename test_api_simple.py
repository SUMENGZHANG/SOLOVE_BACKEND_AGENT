#!/usr/bin/env python
"""
简单 API 测试 - 不依赖数据库

测试 AI 服务核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service

print("\n🤖 SoLove Agent API 测试（简化版）\n")
print("=" * 60)

# 测试 1: 基础聊天
print("\n【测试 1】基础聊天")
print("-" * 60)
messages = [{"role": "user", "content": "你好，我今天心情不太好"}]
response = ai_service.chat(messages=messages, system_prompt="你是 SoLove，温暖的情绪陪伴助手。")
print(f"用户：你好，我今天心情不太好")
print(f"Agent: {response[:200]}...")

# 测试 2: 情绪分析
print("\n【测试 2】情绪分析")
print("-" * 60)
mood = ai_service.analyze_mood("我最近很难过，感觉一切都糟透了")
print(f"文本：我最近很难过，感觉一切都糟透了")
print(f"情绪分：{mood.get('mood_score')}/10")
print(f"情绪标签：{mood.get('mood_label')}")
print(f"关键词：{mood.get('keywords')}")

# 测试 3: 任务生成
print("\n【测试 3】建议任务生成")
print("-" * 60)
tasks = ai_service.generate_suggested_tasks(
    user_mood=3.0,
    conversation_context="用户情绪低落，工作压力大"
)
print(f"为情绪分 3.0 的用户生成任务：")
for i, task in enumerate(tasks, 1):
    print(f"{i}. {task.get('name')} - {task.get('category')} ({task.get('estimated_time')}分钟)")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)
