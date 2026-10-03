# OpenAI API with FastAPI — Step-by-Step Practice Guide

This project continues the AI learning path:

```text
FastAPI
   ↓
OpenAI API   ← YOU ARE HERE
   ↓
Prompt Engineering
   ↓
Structured Output
   ↓
Function / Tool Calling
   ↓
Embeddings
   ↓
Vector Database
   ↓
RAG
   ↓
AI Agents
   ↓
Model Context Protocol (MCP)
   ↓
Agentic Workflows
   ↓
Evaluation & Observability
   ↓
Docker
   ↓
Cloud Deployment
```

The goal of this README is to learn how to connect a FastAPI application to the OpenAI API step by step.

---

# 1. What is the OpenAI API?

The OpenAI API allows your application to send requests to AI models and receive generated responses.

Your application architecture becomes:

```text
User / Browser / React
        ↓
FastAPI
        ↓
OpenAI API
        ↓
AI Model
        ↓
OpenAI API
        ↓
FastAPI
        ↓
JSON Response
```

Your FastAPI application acts as the backend layer between your user interface and OpenAI.

---

# 2. What We Will Learn

In this section, we will learn:

1. Install the OpenAI Python SDK
2. Create an OpenAI API key
3. Store the API key safely
4. Load `.env` variables
5. Create the OpenAI client
6. Send a request to OpenAI
7. Read the AI response
8. Connect OpenAI to FastAPI
9. Use Pydantic request models
10. Handle errors
11. Add instructions
12. Understand the response object
13. Test through Swagger
14. Organize the project cleanly
15. Practice exercises

---

# 3. Project Structure

Continue with the same FastAPI project:

```text
ai-fastapi-learning/
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 4. Activate the Virtual Environment

Open the VS Code terminal.

Windows:

```bash
.venv\Scripts\activate
```

---

# 5. Install the OpenAI SDK

Install the official OpenAI Python package:

```bash
pip install openai
```

Install `python-dotenv`:

```bash
pip install python-dotenv
```

If FastAPI is not already installed:

```bash
pip install fastapi uvicorn
```

Update `requirements.txt`:

```bash
pip freeze > requirements.txt
```

---

# 6. Create an OpenAI API Key

Create an API key from your OpenAI developer account.

Never put your API key directly inside your Python source code.

Do NOT do this:

```python
client = OpenAI(
    api_key="sk-my-secret-key"
)
```

Instead, store the key in an environment variable.

---

# 7. Create the `.env` File

Create:

```text
.env
```

Add:

```text
OPENAI_API_KEY=your-openai-api-key-here
```

---

# 8. Protect the `.env` File

Open:

```text
.gitignore
```

Add:

```text
.env
.venv/
__pycache__/
*.pyc
```

If `.env` was already committed:

```bash
git rm --cached .env
git add .gitignore
git commit -m "Remove env file from source control"
```

If a real API key was exposed publicly, revoke it and create a new one.

---

# 9. First OpenAI API Test

Create a temporary file:

```text
test_openai.py
```

Add:

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Explain artificial intelligence in one sentence."
)

print(response.output_text)
```

Run:

```bash
python test_openai.py
```

The model name can change over time or depend on your API project, so use a currently available model for your account.

---

# 10. Understand the OpenAI Client

This line:

```python
client = OpenAI()
```

creates an OpenAI client.

Think of it like this:

```text
Your Python Application
        ↓
OpenAI Client
        ↓
OpenAI API
```

The `client` object gives your application access to OpenAI API capabilities.

---

# 11. Understand `client.responses.create()`

This is the most important part:

```python
response = client.responses.create(
    model="gpt-5",
    input="Explain machine learning."
)
```

Breakdown:

```text
response =              Store the result
client                  OpenAI client
responses               Responses API resource
create()                Create a model response
model                   Model to use
input                    User input
```

---

# 12. Read the Model Response

For basic text output, use:

```python
response.output_text
```

Example:

```python
print(response.output_text)
```

Conceptually:

```text
response
   │
   ├── id
   ├── model
   ├── output
   ├── usage
   └── output_text
```

---

# 13. Connect OpenAI to FastAPI

Update:

```text
app/main.py
```

```python
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI(
    title="AI Learning API",
    description="Learning FastAPI and OpenAI API",
    version="1.0.0"
)

client = OpenAI()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {
        "application": "AI Learning API",
        "status": "running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    response = client.responses.create(
        model="gpt-5",
        input=request.message
    )

    return {
        "message": request.message,
        "response": response.output_text
    }
```

---

# 14. Understand the `/chat` Flow

Request:

```json
{
  "message": "Explain RAG"
}
```

Flow:

```text
POST /chat
     ↓
FastAPI
     ↓
ChatRequest
     ↓
request.message
     ↓
OpenAI Responses API
     ↓
AI Model
     ↓
response.output_text
     ↓
FastAPI JSON Response
```

---

# 15. Run the API

Start FastAPI:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Select:

```text
POST /chat
```

Try:

```json
{
  "message": "What is machine learning?"
}
```

---

# 16. Add Instructions

You can provide high-level behavior instructions to the model.

Example:

```python
response = client.responses.create(
    model="gpt-5",
    instructions="You are an AI instructor. Explain concepts in simple language.",
    input=request.message
)
```

Think of it like this:

```text
Instructions
      ↓
"Act as an AI teacher"

User Input
      ↓
"Explain embeddings"

      ↓

Model

      ↓

Teacher-style explanation
```

---

# 17. Improve the Chat Endpoint

```python
@app.post("/chat")
def chat(request: ChatRequest):

    response = client.responses.create(
        model="gpt-5",
        instructions="""
        You are an AI instructor.
        Explain technical concepts clearly.
        Assume the student is learning AI development.
        Give simple examples when useful.
        """,
        input=request.message
    )

    return {
        "question": request.message,
        "answer": response.output_text
    }
```

---

# 18. Add a Response Model

```python
class ChatResponse(BaseModel):
    question: str
    answer: str
```

Then:

```python
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    response = client.responses.create(
        model="gpt-5",
        instructions="You are an AI instructor.",
        input=request.message
    )

    return ChatResponse(
        question=request.message,
        answer=response.output_text
    )
```

Now you have:

```text
Request Validation
        ↓
ChatRequest

Response Validation
        ↓
ChatResponse
```

---

# 19. Error Handling

External API calls can fail because of:

```text
Invalid API key
Network problem
Rate limit
Billing issue
Invalid model
Server error
Bad request
```

For learning:

```python
from fastapi import HTTPException
```

Then:

```python
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        response = client.responses.create(
            model="gpt-5",
            instructions="You are an AI instructor.",
            input=request.message
        )

        return ChatResponse(
            question=request.message,
            answer=response.output_text
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate AI response."
        )
```

Avoid returning sensitive internal exception details directly to users in production.

---

# 20. Validate Empty Messages

Use Pydantic validation:

```python
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=2000
    )
```

This means:

```text
Minimum length: 1
Maximum length: 2000
```

FastAPI automatically validates it.

---

# 21. Inspect the Full Response Object

For learning, temporarily try:

```python
print(response)
```

This helps you see that the API response contains more than just generated text.

For normal text output, use:

```python
response.output_text
```

---

# 22. Example: AI Learning Endpoint

```python
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
```

Try:

```json
{
  "topic": "Embeddings"
}
```

Then:

```json
{
  "topic": "RAG"
}
```

---

# 23. Example: Summary Endpoint

```python
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
```

---

# 24. Example: Translation Endpoint

```python
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
```

Example request:

```json
{
  "text": "Good morning",
  "language": "Amharic"
}
```

---

# 25. Practice Exercise 1

Create:

```text
POST /ask
```

Request:

```json
{
  "question": "What is deep learning?"
}
```

Return:

```json
{
  "question": "What is deep learning?",
  "answer": "..."
}
```

---

# 26. Practice Exercise 2

Create:

```text
POST /explain
```

Request:

```json
{
  "topic": "Vector Database"
}
```

Tell OpenAI:

```text
Explain the topic for a beginner.
Give one real-world example.
```

---

# 27. Practice Exercise 3

Create:

```text
POST /summarize
```

Request:

```json
{
  "text": "Long text goes here..."
}
```

Return:

```json
{
  "summary": "..."
}
```

---

# 28. Practice Exercise 4

Create:

```text
POST /translate
```

Request:

```json
{
  "text": "Artificial intelligence is changing software development.",
  "language": "Amharic"
}
```

---

# 29. Practice Exercise 5

Create:

```text
POST /teacher
```

Request:

```json
{
  "message": "Explain embeddings."
}
```

Instructions:

```text
You are an AI instructor.

Explain the topic using:

1. Simple definition
2. Real-world analogy
3. Technical explanation
4. Small example
```

Observe how changing instructions changes the answer.

This leads directly into Prompt Engineering.

---

# 30. Suggested Complete Project Code

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


app = FastAPI(
    title="AI Learning API",
    description="FastAPI application for learning the OpenAI API",
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


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        response = client.responses.create(
            model="gpt-5",
            instructions="""
            You are an AI instructor.
            Explain technical concepts clearly.
            Assume the student is learning AI development.
            Use simple examples when appropriate.
            """,
            input=request.message
        )

        return ChatResponse(
            question=request.message,
            answer=response.output_text
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate AI response."
        )
```

---

# 31. Important Concepts Learned

| Concept | Example |
|---|---|
| OpenAI client | `client = OpenAI()` |
| Responses API | `client.responses.create()` |
| Model | `model="gpt-5"` |
| User input | `input=request.message` |
| Instructions | `instructions="You are an AI instructor"` |
| Text output | `response.output_text` |
| Environment variables | `.env` |
| Load environment | `load_dotenv()` |
| FastAPI request | `ChatRequest` |
| FastAPI response | `ChatResponse` |
| Error handling | `HTTPException` |

---

# 32. FastAPI + OpenAI Mental Model

Remember this pattern:

```python
@app.post("/chat")
def chat(request: ChatRequest):

    response = client.responses.create(
        model="gpt-5",
        input=request.message
    )

    return {
        "answer": response.output_text
    }
```

Think:

```text
HTTP Request
    ↓
FastAPI
    ↓
Pydantic
    ↓
OpenAI Client
    ↓
Responses API
    ↓
AI Model
    ↓
Response Object
    ↓
output_text
    ↓
FastAPI JSON Response
```

---

# 33. Next Step — Prompt Engineering

The next stage is:

```text
FastAPI
   ↓
OpenAI API
   ↓
Prompt Engineering   ← NEXT
```

We will learn:

```text
Instructions
System behavior
User input
Prompt structure
Few-shot examples
Context
Constraints
Output formatting
Prompt variables
Reusable prompts
Prompt injection awareness
```

Then we will move into Structured Output.

---

# 34. Current AI Learning Progress

```text
✅ FastAPI
✅ OpenAI API
⬜ Prompt Engineering
⬜ Structured Output
⬜ Function / Tool Calling
⬜ Embeddings
⬜ Vector Database
⬜ RAG
⬜ AI Agents
⬜ Model Context Protocol (MCP)
⬜ Agentic Workflows
⬜ Evaluation & Observability
⬜ Docker
⬜ Cloud Deployment
```

Continue building on the same project so each concept builds on the previous one.
