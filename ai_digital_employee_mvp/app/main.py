from fastapi import FastAPI
from .schemas import RequestIn, RequestOut
from .orchestrator import orchestrate_request
app = FastAPI()
@app.post('/process', response_model=RequestOut)
def process_request(req: RequestIn):
    result = orchestrate_request(req.message)
    return {'message': req.message, 'result': result}
