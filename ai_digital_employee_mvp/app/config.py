"""
应用配置：从环境变量读取所有配置项。
"""

import os
import logging

logger = logging.getLogger(__name__)

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/ai_agents")

# Redis 连接（预留，暂未使用）
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 启动时检查关键配置
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY 未设置！Agent 调用将返回错误。请设置环境变量 OPENAI_API_KEY。")
else:
    logger.info("OPENAI_API_KEY 已配置 (%s...)", OPENAI_API_KEY[:8])
