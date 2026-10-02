# FastAPI for AI Development — Step-by-Step Practice Guide

This project is part of my AI learning path:

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

The goal of this README is to learn FastAPI step by step and build a foundation for AI application development.

---

# 1. What is FastAPI?

FastAPI is a Python web framework used to build APIs.

In AI applications, FastAPI commonly sits between the frontend and AI services.

Example architecture:

```text
React / Browser
       ↓
FastAPI
       ↓
OpenAI API
       ↓
AI Model
       ↓
FastAPI
       ↓
React / Browser
```

FastAPI is useful because it provides:

- Fast API development
- Automatic request validation
- Automatic JSON serialization
- Swagger/OpenAPI documentation
- Async support
- Easy integration with AI services
- Easy integration with databases
- Easy deployment using Docker and cloud platforms

---

# 2. FastAPI Learning Path

We will learn FastAPI in this order:

1. Create a basic FastAPI application
2. GET endpoints
3. Path parameters
4. Query parameters
5. POST requests
6. Pydantic request models
7. Response models
8. PUT requests
9. DELETE requests
10. Error handling
11. Dependency injection
12. Environment variables
13. Project organization
14. Async programming
15. Connect FastAPI to OpenAI

---

# 3. Project Structure

Create the following structure:

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

# 4. Create the Python Virtual Environment

Open a terminal in VS Code.

Navigate to your project:

```bash
cd ai-fastapi-learning
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

When activated, the terminal should look similar to:

```text
(.venv) C:\projects\ai-fastapi-learning>
```

---

# 5. Install FastAPI

Install FastAPI and Uvicorn:

```bash
pip install fastapi uvicorn
```

Save dependencies:

```bash
pip freeze > requirements.txt
```

Later, dependencies can be restored with:

```bash
pip install -r requirements.txt
```

---

# 6. Create Your First FastAPI Application

Open:

```text
app/main.py
```

Add:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Welcome to my AI API"
    }
```

## Explanation

This line imports FastAPI:

```python
from fastapi import FastAPI
```

This creates the API application:

```python
app = FastAPI()
```

This creates a GET endpoint:

```python
@app.get("/")
```

It means:

```text
When a user sends:

GET /

Run the function below.
```

The function:

```python
def home():
```

returns:

```python
{
    "message": "Welcome to my AI API"
}
```

FastAPI automatically converts the Python dictionary into JSON.

---

# 7. Run the FastAPI Application

From the project root, run:

```bash
uvicorn app.main:app --reload
```

Explanation:

```text
app.main:app
 │   │    │
 │   │    └── FastAPI object
 │   └────── main.py
 └────────── app folder
```

The `--reload` option restarts the development server whenever Python code changes.

Open:

```text
http://127.0.0.1:8000
```

Expected result:

```json
{
  "message": "Welcome to my AI API"
}
```

---

# 8. Swagger / OpenAPI Documentation

FastAPI automatically creates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can test your API without Postman.

Typical steps:

```text
1. Open /docs
2. Select an endpoint
3. Click "Try it out"
4. Enter request data
5. Click "Execute"
6. Review the response
```

---

# 9. Create Multiple GET Endpoints

Update `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()


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
```

Test:

```text
GET /
GET /hello
GET /ai
```

FastAPI automatically converts Python dictionaries to JSON.

Python:

```python
{
    "topic": "Artificial Intelligence"
}
```

JSON response:

```json
{
  "topic": "Artificial Intelligence"
}
```

---

# 10. Path Parameters

Suppose the application needs URLs like:

```text
/users/1
/users/2
/users/100
```

Instead of creating separate endpoints, use a path parameter.

Add:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id,
        "message": f"User {user_id} found"
    }
```

Test:

```text
http://127.0.0.1:8000/users/10
```

Response:

```json
{
  "user_id": 10,
  "message": "User 10 found"
}
```

The following:

```python
user_id: int
```

means that `user_id` must be an integer.

For example:

```text
/users/10
```

is valid.

But:

```text
/users/abc
```

will fail validation.

FastAPI automatically validates input.

---

# 11. Query Parameters

Query parameters appear after `?` in a URL.

Example:

```text
/search?query=machine learning
```

Create:

```python
@app.get("/search")
def search(query: str):
    return {
        "query": query,
        "message": f"You searched for {query}"
    }
```

Test:

```text
http://127.0.0.1:8000/search?query=machine%20learning
```

Response:

```json
{
  "query": "machine learning",
  "message": "You searched for machine learning"
}
```

---

# 12. Multiple Query Parameters

You can use more than one query parameter.

Example:

```python
@app.get("/search")
def search(query: str, limit: int = 5):
    return {
        "query": query,
        "limit": limit
    }
```

Test:

```text
/search?query=FastAPI&limit=10
```

Response:

```json
{
  "query": "FastAPI",
  "limit": 10
}
```

This:

```python
limit: int = 5
```

means:

```text
Type: integer
Default value: 5
```

If the caller does not provide `limit`, FastAPI uses `5`.

---

# 13. POST Requests

POST requests are extremely important in AI applications.

Later, our AI endpoint will look like:

```text
POST /chat
```

Request:

```json
{
  "message": "Explain machine learning"
}
```

To define the expected request body, use Pydantic.

---

# 14. Pydantic Request Models

<!-- When you inherit from BaseModel, Pydantic automatically:

Validates input data
Converts types when possible
Generates API documentation
Creates Python objects from JSON -->


Update `main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "received_message": request.message
    }
```

## What does this class mean?

```python
class ChatRequest(BaseModel):
    message: str
```

It defines the shape of the incoming JSON.

It means:

```text
ChatRequest
    │
    └── message
          │
          └── string
```

FastAPI expects:

```json
{
  "message": "Hello AI"
}
```

---

# 15. Request Validation

Because `message` is defined as a string:

```python
message: str
```

FastAPI validates the incoming request automatically.

Expected request:

```json
{
  "message": "Explain FastAPI"
}
```

If required values are missing or invalid, FastAPI returns a validation error.

This validation becomes very useful when building AI applications.

---

# 16. Create a Simple AI-Style API

Now build an endpoint that behaves like a fake AI service.

```python
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="AI Learning API",
    description="FastAPI project for learning AI development",
    version="1.0.0"
)


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

    user_message = request.message

    response = f"You asked: {user_message}"

    return {
        "user_message": user_message,
        "ai_response": response
    }
```

---

# 17. Test the Chat API

Open:

```text
http://127.0.0.1:8000/docs
```

Select:

```text
POST /chat
```

Click:

```text
Try it out
```

Enter:

```json
{
  "message": "What is machine learning?"
}
```

Click:

```text
Execute
```

Response:

```json
{
  "user_message": "What is machine learning?",
  "ai_response": "You asked: What is machine learning?"
}
```

---

# 18. Current Architecture

At this point, the application works like this:

```text
User
 ↓
POST /chat
 ↓
FastAPI
 ↓
Python function
 ↓
JSON Response
```

Later, the same endpoint will become:

```text
User
 ↓
POST /chat
 ↓
FastAPI
 ↓
OpenAI API
 ↓
AI Model
 ↓
FastAPI
 ↓
JSON Response
```

The important point is that we do not need to rebuild the entire API.

We will replace the fake response:

```python
response = f"You asked: {user_message}"
```

with a real OpenAI request.

Conceptually:

```python
response = client.responses.create(
    model="MODEL_NAME",
    input=user_message
)
```

---

# 19. Practice Exercise

Create these endpoints yourself:

```text
GET  /health
GET  /courses
GET  /courses/{course_id}
POST /chat
```

## Exercise 1 — Health Endpoint

Create:

```text
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## Exercise 2 — Courses Endpoint

Create:

```text
GET /courses
```

Example response:

```json
[
  {
    "course_id": 1,
    "course_name": "Artificial Intelligence"
  },
  {
    "course_id": 2,
    "course_name": "Machine Learning"
  },
  {
    "course_id": 3,
    "course_name": "FastAPI"
  }
]
```

---

## Exercise 3 — Course by ID

Create:

```text
GET /courses/1
```

Expected response:

```json
{
  "course_id": 1,
  "course_name": "Artificial Intelligence"
}
```

Try:

```text
GET /courses/2
GET /courses/3
GET /courses/100
```

Think about how the application should respond when the course does not exist.

We will learn proper error handling later.

---

## Exercise 4 — Chat Endpoint

Create:

```text
POST /chat
```

Request:

```json
{
  "message": "Explain RAG"
}
```

Response:

```json
{
  "message": "Explain RAG",
  "response": "AI response will go here"
}
```

---

# 20. Suggested Complete Practice File

You can use this as your starting `main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="AI Learning API",
    description="Learning FastAPI for AI development",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str


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


@app.get("/courses")
def get_courses():
    return [
        {
            "course_id": 1,
            "course_name": "Artificial Intelligence"
        },
        {
            "course_id": 2,
            "course_name": "Machine Learning"
        },
        {
            "course_id": 3,
            "course_name": "FastAPI"
        }
    ]


@app.get("/courses/{course_id}")
def get_course(course_id: int):
    return {
        "course_id": course_id,
        "course_name": f"Course {course_id}"
    }


@app.get("/search")
def search(query: str, limit: int = 5):
    return {
        "query": query,
        "limit": limit
    }


@app.post("/chat")
def chat(request: ChatRequest):

    response = f"You asked: {request.message}"

    return {
        "message": request.message,
        "response": response
    }
```

---

# 21. Important FastAPI Concepts Learned

At this point, you should understand:

| Concept | Example |
|---|---|
| FastAPI application | `app = FastAPI()` |
| GET endpoint | `@app.get("/")` |
| POST endpoint | `@app.post("/chat")` |
| Path parameter | `/users/{user_id}` |
| Query parameter | `/search?query=AI` |
| Pydantic model | `class ChatRequest(BaseModel)` |
| Request body | `request: ChatRequest` |
| JSON response | `return {"message": "Hello"}` |
| Swagger | `/docs` |
| Development server | `uvicorn app.main:app --reload` |

---

# 22. Next Step — Connect FastAPI to OpenAI

The next lesson will add:

```text
FastAPI
   ↓
OpenAI Python SDK
   ↓
OpenAI Responses API
   ↓
AI Model
```

We will update the project to include:

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

The `.env` file will contain the API key:

```text
OPENAI_API_KEY=your-api-key
```

Important:

```text
Never commit the .env file to GitHub.
```

Add it to `.gitignore`:

```text
.env
.venv/
__pycache__/
```

---

# 23. AI Development Roadmap

After completing FastAPI, continue in this order:

```text
1. FastAPI
       ↓
2. OpenAI API
       ↓
3. Prompt Engineering
       ↓
4. Structured Output
       ↓
5. Function / Tool Calling
       ↓
6. Embeddings
       ↓
7. Vector Database
       ↓
8. RAG
       ↓
9. AI Agents
       ↓
10. Model Context Protocol (MCP)
       ↓
11. Agentic Workflows
       ↓
12. Evaluation & Observability
       ↓
13. Docker
       ↓
14. Cloud Deployment
```

The goal is to keep extending the same project so each new AI concept builds on the previous one.

---

# 24. Recommended Practice Strategy

For every FastAPI feature:

```text
Learn
 ↓
Write the code yourself
 ↓
Run the API
 ↓
Open Swagger
 ↓
Test the endpoint
 ↓
Change something
 ↓
Break it intentionally
 ↓
Read the error
 ↓
Fix it
```

This is one of the best ways to learn FastAPI and AI API development.

---

# Next Lesson

Next:

```text
FastAPI
   ↓
OpenAI API
```

Topics:

- Install the OpenAI Python SDK
- Store the API key in `.env`
- Load environment variables
- Create the OpenAI client
- Call the Responses API
- Send the user's message
- Return the AI response
- Handle API errors
- Test everything through FastAPI Swagger
