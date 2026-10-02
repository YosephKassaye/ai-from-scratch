# FastAPI Environment Setup for AI Development

This guide shows how to set up a Python development environment for building AI applications with **FastAPI**, **OpenAI**, and **VS Code**.

---

## 1. Install the Basics

Install the following tools:

- Python 3.11 or 3.12
- Visual Studio Code
- VS Code Python extension
- Git

Check your Python installation:

```powershell
python --version
```

If that does not work on Windows, try:

```powershell
py --version
```

For a new AI project, Python 3.12 is a good default unless a specific AI library requires another version.

---

## 2. Create the FastAPI AI Project

Create a new project folder:

```powershell
mkdir ai-api
cd ai-api
code .
```

A recommended project structure is:

```text
ai-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── chat.py
│   ├── services/
│   │   └── ai_service.py
│   └── models/
│       └── schemas.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 3. Create a Python Virtual Environment

Inside the `ai-api` directory:

```powershell
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

You should see something like:

```text
(.venv) PS C:\Projects\ai-api>
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 4. Select the Python Interpreter in VS Code

In VS Code:

1. Press `Ctrl + Shift + P`
2. Search for `Python: Select Interpreter`
3. Select:

```text
.venv\Scripts\python.exe
```

---

## 5. Install FastAPI and AI Packages

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install FastAPI and Uvicorn:

```powershell
pip install fastapi "uvicorn[standard]"
```

Install OpenAI and environment support:

```powershell
pip install openai python-dotenv pydantic
```

---

## 6. Create the First FastAPI Application

Create:

```text
app/main.py
```

Add:

```python
from fastapi import FastAPI

app = FastAPI(
    title="AI API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
```

Run:

```powershell
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## 7. Configure the OpenAI API Key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=sk-your-key-here
```

Never commit the `.env` file to Git.

Add this to `.gitignore`:

```gitignore
# Environment variables
.env
.env.*

# Python
.venv/
venv/
__pycache__/
*.pyc

# VS Code
.vscode/

# OS files
.DS_Store
Thumbs.db
```

If `.env` was already committed:

```bash
git rm --cached .env
git add .gitignore
git commit -m "Remove .env from repository and ignore it"
git push
```

If the API key was already pushed to a remote repository, rotate or revoke it and create a new key.

---

## 8. Call OpenAI from FastAPI

Update `app/main.py`:

```python
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel

# Load values from .env
load_dotenv()

# Read the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not configured")

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Create FastAPI application
app = FastAPI(
    title="AI FastAPI Service",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "message": "AI FastAPI service is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = client.responses.create(
            model="gpt-6-luna",
            input=request.message
        )

        return {
            "question": request.message,
            "answer": response.output_text
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )
```

### How the API key is loaded

This loads `.env`:

```python
load_dotenv()
```

This reads the API key:

```python
api_key = os.getenv("OPENAI_API_KEY")
```

This creates the OpenAI client:

```python
client = OpenAI(api_key=api_key)
```

---

## 9. Run and Test the AI Endpoint

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Find:

```text
POST /chat
```

Click **Try it out** and send:

```json
{
  "message": "Explain machine learning in simple terms"
}
```

Example response:

```json
{
  "question": "Explain machine learning in simple terms",
  "answer": "Machine learning is a way for computers to learn patterns from data..."
}
```

Request flow:

```text
User / Client
      │
      ▼
POST /chat
      │
      ▼
FastAPI
      │
      ▼
OpenAI Python SDK
      │
      ▼
OpenAI Responses API
      │
      ▼
GPT Model
      │
      ▼
Response returned to client
```

---

## 10. Recommended Service-Layer Structure

For learning, calling OpenAI directly from `main.py` is fine.

As the application grows, move OpenAI logic into a service:

```text
ai-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── chat.py
│   ├── services/
│   │   └── openai_service.py
│   └── models/
│       └── chat_model.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

Example `app/services/openai_service.py`:

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def ask_ai(question: str) -> str:
    response = client.responses.create(
        model="gpt-6-luna",
        input=question
    )

    return response.output_text
```

Then `main.py` can be simplified:

```python
from fastapi import FastAPI
from pydantic import BaseModel

from app.services.openai_service import ask_ai

app = FastAPI(title="AI FastAPI Service")


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    answer = ask_ai(request.message)

    return {
        "question": request.message,
        "answer": answer
    }
```

Architecture:

```text
React / Web / Mobile
        │
        ▼
 FastAPI Endpoint
        │
        ▼
 OpenAI Service
        │
        ▼
OpenAI Responses API
        │
        ▼
       LLM
```

---

## 11. Save Python Dependencies

Save installed packages:

```powershell
pip freeze > requirements.txt
```

A new environment can be recreated with:

```bash
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Recommended AI Learning Path

```text
FastAPI
   ↓
OpenAI API
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

This architecture works well when enterprise APIs are implemented in .NET while Python and FastAPI are used for AI-specific workloads.
