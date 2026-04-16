"""
应用核心配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "SoLove Backend"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "情绪陪伴打卡 APP 后端服务"
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 数据库配置（MySQL：mysql+pymysql://用户:密码@主机:端口/库名?charset=utf8mb4）
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/solove?charset=utf8mb4"
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # AI 配置
    AI_API_KEY: Optional[str] = None
    AI_API_BASE: Optional[str] = None
    AI_MODEL: str = "qwen-plus"
    
    # 项目路径
    PROJECT_ROOT: str = "/Users/sumengzhang/Desktop/projects/agent_dev/back_end/solove_backend"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
