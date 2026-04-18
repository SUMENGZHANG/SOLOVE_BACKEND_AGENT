#!/bin/bash

# SoLove Backend 启动脚本

echo "🚀 启动 SoLove Backend 服务..."

# 进入项目目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在，请先运行：python -m venv .venv"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置数据库和 AI API Key"
fi

# 检查依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt

# 启动服务
echo "🌟 启动服务..."
echo "📖 API 文档：http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
