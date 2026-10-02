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