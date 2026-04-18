"""
Agent 聊天功能测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from app.models.models import User

# 创建测试数据库
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建表
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆盖数据库依赖
app.dependency_overrides[get_db] = override_get_db


def setup_module():
    """测试前准备：创建测试用户"""
    db = TestingSessionLocal()
    
    # 清理旧数据
    db.query(User).filter(User.openid == "test_user_001").delete()
    
    # 创建测试用户
    test_user = User(
        openid="test_user_001",
        nickname="测试用户",
        mood_baseline=5.0
    )
    db.add(test_user)
    db.commit()
    db.close()


def teardown_module():
    """测试后清理"""
    db = TestingSessionLocal()
    db.query(User).filter(User.openid == "test_user_001").delete()
    db.commit()
    db.close()


def test_chat_basic():
    """测试基础聊天"""
    response = client.post(
        "/api/chat/",
        json={"message": "你好，我今天心情不太好"},
        params={"openid": "test_user_001"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    print(f"Agent 回复：{data['response']}")


def test_chat_with_sad_mood():
    """测试情绪低落时的聊天（应该生成建议任务）"""
    response = client.post(
        "/api/chat/",
        json={"message": "我最近很难过，感觉一切都糟透了"},
        params={"openid": "test_user_001"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    print(f"Agent 回复：{data['response']}")
    
    # 情绪低落时应该生成建议任务
    if data.get("suggested_tasks"):
        print(f"建议任务：{data['suggested_tasks']}")
        assert isinstance(data["suggested_tasks"], list)
        assert len(data["suggested_tasks"]) > 0


def test_chat_history():
    """测试获取聊天历史"""
    # 先发送几条消息
    messages = [
        "你好",
        "今天天气不错",
        "我想做一些让自己开心的事"
    ]
    
    for msg in messages:
        client.post(
            "/api/chat/",
            json={"message": msg},
            params={"openid": "test_user_001"}
        )
    
    # 获取历史
    response = client.get(
        "/api/chat/history",
        params={"openid": "test_user_001", "limit": 10}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(messages)
    print(f"聊天历史条数：{len(data)}")


def test_chat_user_not_found():
    """测试用户不存在的情况"""
    response = client.post(
        "/api/chat/",
        json={"message": "你好"},
        params={"openid": "non_existent_user"}
    )
    
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
