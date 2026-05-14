"""
AI 数字员工 + 多 Agent 协同系统 - API 主入口。

用法:
    uvicorn app.main:app --reload
    # 或
    python -m app.main
"""

import logging
from contextlib import asynccontextmanager

import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from .schemas import RequestIn, RequestOut, HealthResponse
from .orchestrator import orchestrate_request
from .database import init_db, save_request, get_db_available

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 应用生命周期
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭生命周期。"""
    logger.info("🚀 AI 数字员工系统启动中...")
    init_db()
    logger.info("服务就绪")
    yield
    logger.info("服务关闭")


app = FastAPI(
    title="AI 数字员工 + 多 Agent 协同系统",
    description="""
    基于 OpenAI 的多 Agent 协同系统，模拟 B2B 销售客服全流程。

    ## 核心流程
    1. 接收客户消息
    2. **并行**调用 4 个 AI Agent：
       - 销售代理 — 生成报价方案
       - 技术代理 — 分析技术需求
       - 报价代理 — 生成详细报价
       - 跟进取暖 — 制定跟进策略
    3. 聚合所有结果并返回

    ## 部署方式
    - **Docker Compose（推荐）**: `docker compose up`
    - **本地开发**: 见 README
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# 静态文件路径（前端 UI）
# ---------------------------------------------------------------------------
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/", include_in_schema=False)
async def root():
    """根路径返回前端页面。"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    return HTMLResponse(content="<h1>前端页面未就绪</h1>", status_code=503)


# ---------------------------------------------------------------------------
# 接口
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查端点。"""
    return HealthResponse(
        status="ok",
        db_available=get_db_available(),
    )


@app.post("/process", response_model=RequestOut, tags=["业务"])
async def process_request(req: RequestIn) -> RequestOut:
    """
    处理客户消息。

    并行调用 4 个 AI Agent（销售/技术/报价/跟进），
    聚合结果后返回。单个 Agent 失败不影响整体。
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    logger.info("收到请求: message=%s...", req.message[:50])

    # 调用编排器
    result = await orchestrate_request(req.message)

    # 尝试持久化（优雅降级）
    save_request(req.message, result)

    return RequestOut(message=req.message, result=result)
