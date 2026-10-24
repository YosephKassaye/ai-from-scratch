# FastAPI From Zero to Hero — Hands-on Course

Build REST APIs with Python, Pydantic, external HTTP services, SQL Server, and an optional OpenAI integration. This course starts with a single endpoint and ends with a layered application.

**Audience:** Python beginners with basic programming knowledge. **Platform:** Windows PowerShell (Linux/macOS alternatives included). **Python:** 3.11 or 3.12.

## Learning outcomes

By the end, you will be able to explain HTTP and REST, distinguish path/query/body parameters, validate input using Pydantic v2, implement CRUD operations, consume JSONPlaceholder, connect to SQL Server safely, test APIs, and integrate an AI endpoint without exposing API keys.

## 1. Prerequisites and project setup

Install Python, VS Code (Python extension), and Git. Check Python:

```powershell
python --version
py --version
```

Create the project and virtual environment:

```powershell
mkdir ai-api
cd ai-api
code .
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi "uvicorn[standard]" httpx pyodbc python-dotenv openai pytest
pip freeze > requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` (or use `.venv\Scripts\python.exe` directly). On Linux/macOS use `source .venv/bin/activate`.

**What the packages do:** FastAPI defines HTTP endpoints and generates OpenAPI documentation; Uvicorn is the ASGI server that runs the app; Pydantic (installed by FastAPI) validates data; httpx calls external APIs; pyodbc connects to SQL Server; python-dotenv loads local configuration; openai provides the OpenAI SDK; pytest runs tests.

## 2. Start with Hello World

Create `app/__init__.py` and `app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="FastAPI Zero to Hero", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

Run from the project root:

```powershell
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/`, `http://127.0.0.1:8000/docs` (Swagger UI), `http://127.0.0.1:8000/redoc`, and `http://127.0.0.1:8000/openapi.json`. `--reload` is for local development only.

**How it works:** `app.main:app` means import the `app` object from the `app/main.py` module. `@app.get` registers a GET route. A Python dictionary becomes a JSON response.

## 3. HTTP and REST fundamentals

| Method | Purpose | Typical response |
|---|---|---|
| GET | Read resources | 200 |
| POST | Create resource | 201 |
| PUT | Replace resource | 200/204 |
| PATCH | Partially update | 200/204 |
| DELETE | Remove resource | 204 |

Common errors: **400** bad request; **401** unauthenticated; **403** forbidden; **404** missing resource; **422** invalid request data; **500** server error; **502/503** upstream/service unavailable.

A URL may contain **path parameters** (`/products/10`), **query parameters** (`/products?category=books&page=2`), and a request may also have a **JSON body** (usually POST/PUT/PATCH).

## 4. Path parameters — identify one resource

Add to `app/main.py`:

```python
from fastapi import Path

@app.get("/hello/{name}")
def hello(name: str):
    return {"greeting": f"Hello, {name}"}

@app.get("/square/{number}")
def square(number: int = Path(ge=0, le=1000)):
    return {"number": number, "square": number ** 2}
```

Try `/hello/Maria`, `/square/12`, `/square/-1`, and `/square/abc`. The latter two produce validation errors (422). A path parameter is **required** and is part of the URL path. Type hints trigger conversion and validation.

## 5. Query parameters — filter, search, and paginate

```python
from fastapi import Query

@app.get("/search")
def search(
    q: str | None = Query(default=None, min_length=2),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    active: bool = True,
):
    return {"query": q, "page": page, "page_size": page_size, "active": active}
```

Try `/search?q=python&page=2&page_size=5&active=false`. Query parameters follow `?`, are separated by `&`, and often have defaults. FastAPI converts `page` to an integer and `active` to a boolean. Missing optional `q` becomes `None`.

**Compare:** `GET /students/7` fetches student 7; `GET /students?grade=5&active=true` searches a collection. Do not put optional filters into the path.

## 6. Pydantic models — validate JSON request bodies

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=5, le=120)
    grade: int = Field(ge=1, le=12)
    email: str | None = None

class Student(StudentCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

students: dict[int, Student] = {}
next_id = 1

@app.post("/students", response_model=Student, status_code=201)
def create_student(payload: StudentCreate):
    global next_id
    student = Student(id=next_id, **payload.model_dump())
    students[next_id] = student
    next_id += 1
    return student
```

POST `/students` with:

```json
{"name": "Sara", "age": 14, "grade": 8, "email": "sara@example.com"}
```

Try age `-2` or missing `name` and inspect the automatic 422 validation response. `BaseModel` describes the data; `Field` adds constraints; `model_dump()` converts a model to a dictionary. `response_model` documents and validates/filters the output. For true email validation, install `email-validator` and use `EmailStr` (the example uses plain `str` to keep dependencies minimal).

**Important:** The in-memory dictionary resets whenever the process restarts and is not safe for concurrent production updates.

## 7. CRUD with path, query, body, and errors

Append these endpoints after the student model:

```python
from fastapi import HTTPException, Response

@app.get("/students", response_model=list[Student])
def list_students(grade: int | None = None, skip: int = 0, limit: int = Query(10, ge=1, le=100)):
    results = list(students.values())
    if grade is not None:
        results = [s for s in results if s.grade == grade]
    return results[skip:skip + limit]

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    return students[student_id]

@app.put("/students/{student_id}", response_model=Student)
def replace_student(student_id: int, payload: StudentCreate):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    students[student_id] = Student(id=student_id, **payload.model_dump())
    return students[student_id]

class StudentPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    age: int | None = Field(default=None, ge=5, le=120)
    grade: int | None = Field(default=None, ge=1, le=12)
    email: str | None = None

@app.patch("/students/{student_id}", response_model=Student)
def patch_student(student_id: int, payload: StudentPatch):
    current = get_student(student_id)
    updates = payload.model_dump(exclude_unset=True)
    updated = current.model_copy(update=updates)
    # Validate merged data because model_copy(update=...) does not revalidate.
    validated = Student.model_validate(updated.model_dump())
    students[student_id] = validated
    return validated

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]
    return Response(status_code=204)
```

**Practice:** Create two students, list by grade, update one, delete the other, and confirm GET returns 404. Note that PATCH is partial, while PUT expects a complete student body.

## 8. External REST API — JSONPlaceholder

JSONPlaceholder is a public demo API at `https://jsonplaceholder.typicode.com`. Its data is sample data; write operations are simulated and do not persist. Use `httpx.AsyncClient` in async endpoints, set a timeout, and translate upstream errors.

Add to `app/main.py`:

```python
import httpx
from fastapi import HTTPException

JSON_BASE = "https://jsonplaceholder.typicode.com"

@app.get("/external/posts")
async def external_posts(user_id: int | None = Query(default=None, ge=1), limit: int = Query(5, ge=1, le=100)):
    params = {"_limit": limit}
    if user_id is not None:
        params["userId"] = user_id
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{JSON_BASE}/posts", params=params)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="External API timed out")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"External API returned {exc.response.status_code}")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="External API unavailable")

@app.get("/external/posts/{post_id}")
async def external_post(post_id: int = Path(ge=1)):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{JSON_BASE}/posts/{post_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Post not found")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="External API timed out")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="External API error")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="External API unavailable")
```

Try `/external/posts?user_id=1&limit=3` and `/external/posts/2`. **Security:** The external hostname is hard-coded here; in production, allowlist destinations to avoid SSRF and consider a reusable client, retries with backoff, and observability.

## 9. SQL Server — persistent data with pyodbc

Prerequisites: a reachable SQL Server instance, a database login with minimum necessary permissions, and **Microsoft ODBC Driver 18 for SQL Server** installed on the computer running Python. Driver installation is separate from `pip install pyodbc`.

Execute in SQL Server Management Studio (SSMS):

```sql
CREATE DATABASE FastAPIDemo;
GO
USE FastAPIDemo;
GO
CREATE TABLE dbo.Students (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Age INT NOT NULL CHECK (Age BETWEEN 5 AND 120),
    Grade INT NOT NULL CHECK (Grade BETWEEN 1 AND 12),
    Email NVARCHAR(255) NULL
);
INSERT INTO dbo.Students (Name, Age, Grade, Email)
VALUES (N'Sara', 14, 8, N'sara@example.com'), (N'Daniel', 12, 6, NULL);
```

Create `.env` (replace with your own values):

```dotenv
SQL_SERVER=localhost
SQL_DATABASE=FastAPIDemo
SQL_USERNAME=fastapi_app
SQL_PASSWORD=replace-with-strong-password
SQL_ENCRYPT=yes
SQL_TRUST_SERVER_CERTIFICATE=no
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5
```

For local development with a self-signed SQL Server certificate, you may temporarily set `SQL_TRUST_SERVER_CERTIFICATE=yes` after understanding the risk. In production, use a valid trusted certificate and `no`.

Create `app/db.py`:

```python
import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    required = ["SQL_SERVER", "SQL_DATABASE", "SQL_USERNAME", "SQL_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing database configuration: {', '.join(missing)}")
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.environ['SQL_SERVER']};"
        f"DATABASE={os.environ['SQL_DATABASE']};"
        f"UID={os.environ['SQL_USERNAME']};"
        f"PWD={os.environ['SQL_PASSWORD']};"
        f"Encrypt={os.getenv('SQL_ENCRYPT', 'yes')};"
        f"TrustServerCertificate={os.getenv('SQL_TRUST_SERVER_CERTIFICATE', 'no')};"
    )
    return pyodbc.connect(connection_string, timeout=5)
```

Add to `app/main.py`:

```python
from app.db import get_connection

@app.get("/db/students")
def db_list_students(grade: int | None = Query(default=None, ge=1, le=12)):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Id, Name, Age, Grade, Email FROM dbo.Students WHERE (? IS NULL OR Grade = ?) ORDER BY Id",
            grade, grade,
        )
        return [
            {"id": row.Id, "name": row.Name, "age": row.Age,
             "grade": row.Grade, "email": row.Email}
            for row in cursor.fetchall()
        ]

@app.get("/db/students/{student_id}")
def db_get_student(student_id: int = Path(ge=1)):
    with get_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT Id, Name, Age, Grade, Email FROM dbo.Students WHERE Id = ?", student_id
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"id": row.Id, "name": row.Name, "age": row.Age,
                "grade": row.Grade, "email": row.Email}

@app.post("/db/students", status_code=201)
def db_create_student(payload: StudentCreate):
    with get_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute(
            """INSERT INTO dbo.Students (Name, Age, Grade, Email)
               OUTPUT INSERTED.Id VALUES (?, ?, ?, ?)""",
            payload.name, payload.age, payload.grade, payload.email,
        ).fetchone()
        new_id = row[0]
        conn.commit()
    return {"id": new_id, **payload.model_dump()}
```

`?` parameters prevent SQL injection from values. Never construct SQL with untrusted f-strings. For larger systems use connection management, repository/service layers, migrations, structured logging, and explicit transaction handling. The examples use **synchronous** `def` endpoints because `pyodbc` is synchronous.

## 10. Optional OpenAI integration

OpenAI requires a valid key and API access. Keep the key server-side; do not put it in React code or Git. Set `OPENAI_API_KEY` in `.env` and choose a model available to your account (`OPENAI_MODEL`, e.g. `gpt-5`). Model names and access can change.

Add to `app/main.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

load_dotenv()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

@app.post("/chat")
def chat(payload: ChatRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OpenAI is not configured")
    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=30.0)
        result = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            input=payload.message,
        )
        return {"question": payload.message, "answer": result.output_text}
    except OpenAIError:
        # Do not leak provider details or credentials in public responses.
        raise HTTPException(status_code=502, detail="AI provider request failed")
```

POST `/chat`:

```json
{"message": "Explain the difference between path and query parameters"}
```

**Architecture:** Browser/React → FastAPI route → service/client → OpenAI Responses API → JSON response. Add authentication, authorization, usage limits, moderation, tracing, and cost controls before making this endpoint public.

## 11. Refactor into maintainable modules

After completing the one-file exercises, reorganize into:

```text
ai-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # app creation + include_router
│   ├── api/
│   │   ├── __init__.py
│   │   ├── students.py         # CRUD endpoints
│   │   ├── external.py         # JSONPlaceholder endpoints
│   │   └── chat.py             # AI endpoint
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── external_service.py
│   │   └── openai_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── student_repository.py
│   └── db.py
├── tests/
│   └── test_api.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

Example `app/api/hello.py`:

```python
from fastapi import APIRouter
router = APIRouter(prefix="/api", tags=["Examples"])

@router.get("/hello")
def hello():
    return {"message": "Hello from a router"}
```

Register it in `app/main.py`:

```python
from app.api.hello import router as hello_router
app.include_router(hello_router)
```

Create `app/api/__init__.py` too. Move code in stages rather than copying duplicate routes into multiple files. Typical flow: **API router → service → repository → SQL Server**.

## 12. Automated tests

Install `httpx` and `pytest` (already included). Create `tests/test_api.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_invalid_square():
    response = client.get("/square/abc")
    assert response.status_code == 422

def test_create_student():
    response = client.post("/students", json={"name": "Mina", "age": 10, "grade": 5})
    assert response.status_code == 201
    assert response.json()["name"] == "Mina"
```

Run `python -m pytest -q`. For reliable real-world tests, isolate state between tests, mock external HTTP/OpenAI calls, and use a dedicated test database.

## 13. Security and configuration

Create `.gitignore`:

```gitignore
.env
.env.*
!.env.example
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/
.vscode/
.DS_Store
Thumbs.db
```

Commit an `.env.example` with **names and nonsecret placeholders only**. If a secret was ever pushed, revoke/rotate it; removing a file from Git tracking does not erase historical commits. Never expose raw exception strings to users. Validate all inputs, parameterize SQL, use HTTPS, authenticate sensitive endpoints, restrict CORS origins, and set external HTTP timeouts.

## 14. Useful commands and troubleshooting

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
python -m pytest -q
pip freeze > requirements.txt
```

- `ModuleNotFoundError`: activate the correct venv and run from the project root.
- `Address already in use`: stop the old process or use `--port 8001`.
- `422 Unprocessable Entity`: check types, required fields, and validation rules.
- `404 Not Found`: check HTTP method and URL spelling.
- SQL Server connection error: check hostname/port, TCP connectivity, login, ODBC driver, encryption, and certificate settings.
- External API timeout: verify connectivity; do not assume the demo service is always available.
- OpenAI 401/429: verify key, model access, billing/limits; avoid returning sensitive provider error details.

## 15. Guided exercises and capstone

**Beginner:** Create `/hello/{name}`, `/multiply/{a}/{b}`, `/products?category=...&min_price=...`, and a Pydantic `ProductCreate` model with positive price validation.

**Intermediate:** Build `/tasks` CRUD; add pagination, sorting, and PATCH; implement `/external/users/{id}` using JSONPlaceholder; return 404 for missing records and 502/504 for upstream failures.

**Advanced:** Create `dbo.Products` in SQL Server; implement GET/POST/PUT/DELETE with parameterized SQL; add a service and repository layer; write tests with a test database; add a secured `/chat` endpoint that explains a product description.

**Capstone: Student Learning API:** Implement students, courses, enrollments, SQL Server persistence, JSONPlaceholder teacher-profile demo integration, OpenAI-generated learning suggestions, validation, error handling, automated tests, and API documentation. Build a React frontend as a stretch goal.

## 16. Next steps — AI engineering roadmap

FastAPI → OpenAI Responses API → Prompt Engineering → Structured Outputs → Tool/Function Calling → Embeddings → Vector Databases → RAG → AI Agents → MCP → Agentic Workflows → Evaluation/Observability → Docker → Cloud Deployment.

**Enterprise pattern:** React frontend → FastAPI AI layer → .NET enterprise services / SQL Server / external APIs. Separate concerns, secure every boundary, and add observability and deployment automation as the system grows.

## References

- [FastAPI official tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic documentation](https://docs.pydantic.dev/latest/)
- [HTTPX documentation](https://www.python-httpx.org/)
- [JSONPlaceholder](https://jsonplaceholder.typicode.com/)
- [Microsoft ODBC Driver for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [OpenAI API documentation](https://platform.openai.com/docs/)
