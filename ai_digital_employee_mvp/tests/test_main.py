"""
基础测试：验证 API 路由、请求/响应模型、健康检查。
不依赖 OpenAI API（使用 mock）和数据库。
"""

from unittest.mock import patch, AsyncMock

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    """创建异步测试客户端。"""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_check(client):
    """健康检查端点应返回 200 及服务状态。"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "db_available" in data


@pytest.mark.asyncio
async def test_process_empty_message(client):
    """空消息应返回 400。"""
    resp = await client.post("/process", json={"message": ""})
    assert resp.status_code == 400
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_process_request_success(client):
    """正常请求应返回预期的响应结构。"""
    mock_result = {
        "sales": {"status": "ok", "agent": "sales", "content": "报价方案"},
        "tech": {"status": "ok", "agent": "tech", "content": "技术分析"},
        "quote": {"status": "ok", "agent": "quote", "content": "详细报价"},
        "followup": {"status": "ok", "agent": "followup", "content": "跟进策略"},
    }

    with patch("app.main.orchestrate_request", new=AsyncMock(return_value=mock_result)):
        resp = await client.post("/process", json={"message": "我们需要一套CRM系统"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "我们需要一套CRM系统"
        assert data["result"]["sales"]["status"] == "ok"
        assert data["result"]["tech"]["status"] == "ok"
        assert data["result"]["quote"]["status"] == "ok"
        assert data["result"]["followup"]["status"] == "ok"


@pytest.mark.asyncio
async def test_process_partial_failure(client):
    """部分 Agent 失败时，其他 Agent 结果应正常返回。"""
    mock_result = {
        "sales": {"status": "ok", "agent": "sales", "content": "报价方案"},
        "tech": {"status": "error", "agent": "tech", "content": "调用失败: API 错误"},
        "quote": {"status": "ok", "agent": "quote", "content": "详细报价"},
        "followup": {"status": "error", "agent": "followup", "content": "调用失败: 超时"},
    }

    with patch("app.main.orchestrate_request", new=AsyncMock(return_value=mock_result)):
        resp = await client.post("/process", json={"message": "测试部分失败"})
        assert resp.status_code == 200
        data = resp.json()
        # 成功的 Agent
        assert data["result"]["sales"]["status"] == "ok"
        assert data["result"]["quote"]["status"] == "ok"
        # 失败的 Agent
        assert data["result"]["tech"]["status"] == "error"
        assert data["result"]["followup"]["status"] == "error"


@pytest.mark.asyncio
async def test_orchestrator_agent_configs():
    """验证 AGENT_CONFIGS 包含所有必需的类型。"""
    from app.agents.agent import AGENT_CONFIGS, AGENT_TYPES

    for at in AGENT_TYPES:
        assert at in AGENT_CONFIGS, f"缺少 Agent 类型: {at}"
        assert "name" in AGENT_CONFIGS[at]
        assert "prompt_template" in AGENT_CONFIGS[at]


@pytest.mark.asyncio
async def test_schemas():
    """验证 Pydantic 模型正常工作。"""
    from app.schemas import RequestIn, RequestOut, HealthResponse

    req = RequestIn(message="test")
    assert req.message == "test"

    out = RequestOut(message="test", result={"key": "value"})
    assert out.message == "test"
    assert out.result["key"] == "value"

    health = HealthResponse(status="ok", db_available=False)
    assert health.status == "ok"
    assert health.db_available is False
