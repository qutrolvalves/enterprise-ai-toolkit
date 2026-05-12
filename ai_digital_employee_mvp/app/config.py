import os
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/ai_agents')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
