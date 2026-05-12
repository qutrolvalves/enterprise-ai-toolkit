from pydantic import BaseModel
class RequestIn(BaseModel):
    message: str
class RequestOut(BaseModel):
    message: str
    result: dict
