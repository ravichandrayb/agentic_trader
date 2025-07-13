from fastapi import FastAPI
from pydantic import BaseModel
from langgraph_flow import graph

app = FastAPI()

class StockRequest(BaseModel):
    stock: str

@app.post("/analyze")
def analyze_stock(request: StockRequest):
    result = graph.invoke({"stock": request.stock})
    return result
