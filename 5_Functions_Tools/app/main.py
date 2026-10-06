# main.py

from fastapi import FastAPI

from app.models.models import ChatRequest
from app.services.ai_service import process_message


app = FastAPI(
    title="AI Tool Calling API",
    description="FastAPI + OpenAI Function Calling",
    version="1.0.0"
)


@app.get("/")
def home():

    return {
        "application": "AI Tool Calling API",
        "status": "running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    response = process_message(
        request.message
    )

    return {
        "message": request.message,
        "response": response
    }