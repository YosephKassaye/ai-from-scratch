from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import HTTPException
from pydantic import BaseModel, Field
load_dotenv()

app = FastAPI(
    title="AI Learning API",
    description="Learning FastAPI and OpenAI API",
    version="1.0.0"
)

client = OpenAI()


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000
    )

class ChatResponse(BaseModel):
    question: str
    answer: str
    
@app.get("/")
def home():
    return {
        "application": "AI Learning API",
        "status": "running"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        response = client.responses.create(
            model="gpt-5",
            instructions="You are an AI instructor.",
            input=request.message
        )
        print(response)

        return ChatResponse(
            question=request.message,
            answer=response.output_text
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate AI response."
        )
class ExplainRequest(BaseModel):
    topic: str


@app.post("/explain")
def explain(request: ExplainRequest):

    response = client.responses.create(
        model="gpt-5",
        instructions="""
        You are an AI teacher.
        Explain the topic for a beginner.
        Include:
        1. Definition
        2. Simple example
        3. Why it matters
        """,
        input=request.topic
    )

    return {
        "topic": request.topic,
        "explanation": response.output_text
    }

class SummaryRequest(BaseModel):
    text: str


@app.post("/summarize")
def summarize(request: SummaryRequest):

    response = client.responses.create(
        model="gpt-5",
        instructions="Summarize the user's text clearly and concisely.",
        input=request.text
    )

    return {
        "summary": response.output_text
    }

class TranslationRequest(BaseModel):
    text: str
    language: str


@app.post("/translate")
def translate(request: TranslationRequest):

    prompt = f"""
    Translate the following text to {request.language}:

    {request.text}
    """

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return {
        "original": request.text,
        "language": request.language,
        "translation": response.output_text
    }