#!/usr/bin/env python
"""
Agent 聊天功能快速测试脚本

使用方法：
1. 确保 .env 已配置 AI_API_KEY
2. 运行：python test_agent.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import ai_service

def test_basic_chat():
    """测试基础聊天"""
    print("=" * 50)
    print("测试 1: 基础聊天")
    print("=" * 50)
    
    messages = [
        {"role": "user", "content": "你好，我今天心情不太好"}
    ]
    
    response = ai_service.chat(
        messages=messages,
        system_prompt="你是一个温暖的情绪陪伴助手，名叫 SoLove。",
        temperature=0.7
    )
    
    print(f"用户：你好，我今天心情不太好")
    print(f"Agent: {response}")
    print()


def test_emotional_chat():
    """测试情绪化聊天"""
    print("=" * 50)
    print("测试 2: 情绪低落时的聊天")
    print("=" * 50)
    
    messages = [
        {"role": "user", "content": "我最近很难过，感觉一切都糟透了，工作压力大，睡眠也不好"}
    ]
    
    response = ai_service.chat(
        messages=messages,
        system_prompt="你是一个温暖的情绪陪伴助手，名叫 SoLove。",
        temperature=0.7
    )
    
    print(f"用户：我最近很难过，感觉一切都糟透了，工作压力大，睡眠也不好")
    print(f"Agent: {response}")
    print()
    
    # 测试情绪分析
    print("情绪分析：")
    mood = ai_service.analyze_mood("我最近很难过，感觉一切都糟透了")
    print(f"  情绪分：{mood.get('mood_score')}/10")
    print(f"  情绪标签：{mood.get('mood_label')}")
    print(f"  关键词：{mood.get('keywords')}")
    print()
    
    # 测试任务生成
    print("建议任务：")
    tasks = ai_service.generate_suggested_tasks(
        user_mood=3.0,
        conversation_context="用户最近很难过，工作压力大，睡眠不好"
    )
    for task in tasks:
        print(f"  - {task.get('name')}: {task.get('description')}")
    print()


def test_multi_turn():
    """测试多轮对话"""
    print("=" * 50)
    print("测试 3: 多轮对话")
    print("=" * 50)
    
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好呀！我是 SoLove，今天过得怎么样？"},
        {"role": "user", "content": "还行吧，就是有点累"},
        {"role": "assistant", "content": "听起来你今天辛苦了。累的时候，记得给自己一些休息的时间哦。想聊聊是什么让你觉得累吗？"},
        {"role": "user", "content": "工作太多了，做不完"}
    ]
    
    response = ai_service.chat(
        messages=messages,
        system_prompt="你是一个温暖的情绪陪伴助手，名叫 SoLove。",
        temperature=0.7
    )
    
    print("对话历史：")
    for msg in messages:
        role = "用户" if msg["role"] == "user" else "Agent"
        print(f"  {role}: {msg['content'][:50]}...")
    print(f"\nAgent 回复：{response}")
    print()


if __name__ == "__main__":
    print("\n🤖 SoLove Agent 功能测试\n")
    
    # 检查配置
    if not ai_service.client:
        print("⚠️  警告：AI_API_KEY 或 AI_API_BASE 未配置，将使用占位响应")
        print("   请在 .env 文件中配置阿里云 DashScope API Key\n")
    else:
        print("✅ AI 服务已配置，使用模型：" + ai_service.model)
        print()
    
    test_basic_chat()
    test_emotional_chat()
    test_multi_turn()
    
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)
