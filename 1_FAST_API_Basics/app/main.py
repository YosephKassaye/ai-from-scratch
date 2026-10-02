from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {
        "message": "Welcome to my AI API"
    }


@app.get("/hello")
def hello():
    return {
        "message": "Hello from FastAPI"
    }


@app.get("/ai")
def ai():
    return {
        "topic": "Artificial Intelligence",
        "status": "Learning FastAPI"
    }
#  Path Parameter   
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "message": f"User {user_id} found"
    }
    
# Query Parameter 
@app.get("/search")
def search(query: str):
    return {
        "query": query,
        "message": f"You searched for {query}"
    }
    
# 12. Multiple Query Parameters
@app.get("/search")
def search(query: str, limit: int = 5):
    return {
        "query": query,
        "limit": limit
    }
# 14. Pydantic Request Models
@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "received_message": request.message
    }