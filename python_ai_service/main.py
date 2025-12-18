from fastapi import FastAPI
from pydantic import BaseModel
from agent import AnalyticsAgent

app = FastAPI()
agent = AnalyticsAgent()

class QuestionRequest(BaseModel):
    shop_domain: str
    access_token: str
    question: str

@app.post("/ask")
def ask(req: QuestionRequest):
    return agent.handle(req)
