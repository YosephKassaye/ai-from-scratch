from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import HTTPException
from pydantic import BaseModel, Field
# from app.prompts.ai_teacher import AI_TEACHER_PROMPT
load_dotenv()

app = FastAPI(
    title="AI Learning API",
    description="Learning FastAPI and OpenAI API",
    version="1.0.0"
)

client = OpenAI()

AI_TEACHER_INSTRUCTIONS = """
You are an AI instructor.

Audience:
A software developer learning AI development.

Rules:
- Explain concepts clearly.
- Use simple language.
- Include one practical example.
- Avoid unnecessary jargon.
- Keep the answer focused on the user's question.
"""

class ExplainRequest(BaseModel):
    topic: str
    level: str = "beginner"

class SummaryRequest(BaseModel): 
    text: str


@app.post("/explain")
def explain(request: ExplainRequest):

    prompt = f"""
    Explain this topic:

    {request.topic}

    Student level:
    {request.level}

    Include:
    1. Definition
    2. Example
    3. Why it matters
    """

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=AI_TEACHER_INSTRUCTIONS,
        input=prompt
    )

    return {
        "topic": request.topic,
         "level": request.level,
        "answer": response.output_text
    }

@app.post("/summarize")
def summarize(request: SummaryRequest):

    instructions = """
    You are a summarization assistant.

    Requirements:
    - Maximum 5 bullet points.
    - Preserve important facts, dates, and numbers.
    - Do not invent missing information.
    """

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=instructions,
        input=request.text
    )

    return {
        "summary": response.output_text
    }    