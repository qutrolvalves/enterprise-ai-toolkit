from pydantic import BaseModel


class RequestIn(BaseModel):
    """客户请求。"""
    message: str


class RequestOut(BaseModel):
    """Agent 处理结果。"""
    message: str
    result: dict


class HealthResponse(BaseModel):
    """健康检查响应。"""
    status: str
    db_available: bool
