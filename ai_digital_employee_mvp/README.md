# 🤖 AI 数字员工 + 多 Agent 协同系统 MVP

基于 **FastAPI + OpenAI** 的多 Agent 协同系统，模拟 B2B 销售客服全流程。

## 系统架构

```
客户消息
    │
    ▼
┌─────────────────────────────────────┐
│         编排器 (orchestrator)         │
│    ┌────────┬────────┬──────┬──────┐ │
│    │ 销售   │ 技术   │ 报价  │ 跟进 │ │
│    │ Agent  │ Agent  │ Agent│ Agent│ │
│    └───┬────┴───┬────┴──┬───┴──┬──┘ │
│        │        │       │      │     │
│        └────────┴───┬───┴──────┘     │
│             并行调用 (asyncio.gather) │
└──────────────────┬──────────────────┘
                   │
                   ▼
          聚合结果 + (可选)持久化
```

### 4 个 AI Agent

| Agent | 职责 |
|-------|------|
| 🛒 **销售代理** | 根据客户消息生成报价方案 |
| 🔧 **技术代理** | 分析客户技术需求并提供建议 |
| 💰 **报价代理** | 生成含各项费用明细的详细报价单 |
| 📞 **跟进取暖** | 制定后续跟进策略和沟通计划 |

## 快速开始

### 方式 1：Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/<your-org>/ai-digital-employee-mvp.git
cd ai-digital-employee-mvp

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY

# 3. 启动（PostgreSQL + Redis + API）
docker compose up -d

# 4. 访问 API 文档
open http://localhost:8000/docs
```

### 方式 2：本地开发

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 4. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查（含数据库状态） |
| POST | `/process` | 处理客户消息 |

### 调用示例

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"message": "我们需要一套企业级CRM系统，预算50万，技术栈要求Java微服务"}'
```

**响应结构：**

```json
{
  "message": "我们需要一套企业级CRM系统，预算50万，技术栈要求Java微服务",
  "result": {
    "sales": {
      "status": "ok",
      "agent": "sales",
      "content": "...报价方案..."
    },
    "tech": {
      "status": "ok",
      "agent": "tech",
      "content": "...技术分析..."
    },
    "quote": {
      "status": "ok",
      "agent": "quote",
      "content": "...详细报价..."
    },
    "followup": {
      "status": "ok",
      "agent": "followup",
      "content": "...跟进策略..."
    }
  }
}
```

> 单个 Agent 调用失败不影响其他 Agent，失败的 Agent 会返回 `status: "error"` 及错误信息。

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `OPENAI_API_KEY` | ✅ | — | OpenAI API 密钥 |
| `DATABASE_URL` | ❌ | `postgresql://postgres:password@db:5432/ai_agents` | PostgreSQL 连接 |
| `REDIS_URL` | ❌ | `redis://redis:6379/0` | Redis 连接（预留） |

> 数据库不可用时，API 仍然可以正常工作（仅无法持久化请求记录）。

## 项目结构

```
ai-digital-employee-mvp/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent.py          # 统一 AI Agent 模块
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── database.py           # 数据库（惰性初始化 + 优雅降级）
│   ├── main.py               # FastAPI 主入口
│   ├── models.py             # SQLAlchemy 数据模型
│   ├── orchestrator.py       # Agent 编排器（异步并行）
│   └── schemas.py            # Pydantic 请求/响应模型
├── tests/
│   └── test_main.py          # 基础测试
├── .env.example              # 环境变量模板
├── .gitignore
├── docker-compose.yml        # Docker 编排
├── Dockerfile                # 容器构建
├── requirements.txt          # Python 依赖
└── README.md
```

## 开发

### 运行测试

```bash
python -m pytest tests/ -v
```

### 扩展新 Agent

在 `app/agents/agent.py` 的 `AGENT_CONFIGS` 中添加新配置即可：

```python
AGENT_CONFIGS = {
    # ... 现有 Agent ...
    "qa": {
        "name": "质检代理",
        "prompt_template": "你是一个质检专家。请审核以下客户消息：\n\n{message}",
    },
}
```

无需修改编排器代码，新 Agent 会自动被并行调用。

## 许可证

MIT
