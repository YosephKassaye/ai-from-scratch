# Structured Output with OpenAI API — Step-by-Step Practice Guide

This project continues the AI learning path:

```text
FastAPI
   ↓
OpenAI API
   ↓
Prompt Engineering
   ↓
Structured Output   ← YOU ARE HERE
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

The goal of this README is to learn how to make AI responses predictable, typed, validated, and easy for your FastAPI application to consume.

---

# 1. What is Structured Output?

Without structured output, an AI model may return free-form text like:

```text
The customer's name is John Smith.
His risk level is low.
He is approved.
```

That may be easy for a human to read, but it is harder for software to process reliably.

Applications usually prefer data like:

```json
{
  "customer_name": "John Smith",
  "risk_level": "Low",
  "approved": true
}
```

Structured Output lets you define the exact shape of the response.

---

# 2. Why Structured Output Matters

Structured Output is important because applications need predictable data.

It helps with:

```text
Validation
Database inserts
API responses
Business rules
UI rendering
Workflow automation
Tool calling
Testing
Logging
Analytics
```

Instead of guessing how the model formatted the answer, your application knows what fields to expect.

---

# 3. Plain Text vs JSON vs Structured Output

There are three useful levels to understand.

## Plain Text

Example:

```text
John Smith is approved and has a low risk level.
```

Easy for humans.

Harder for software.

## JSON Requested by Prompt

You can ask:

```text
Return JSON with:
customer_name
risk_level
approved
```

The model may produce:

```json
{
  "customer_name": "John Smith",
  "risk_level": "Low",
  "approved": true
}
```

This is better, but your application is still depending mostly on prompt instructions.

## Structured Output

Structured Output defines a schema.

For example:

```text
customer_name → string
risk_level    → enum
approved      → boolean
```

The model response is constrained to match that schema.

This is much stronger than simply saying:

```text
Please return JSON.
```

---

# 4. Structured Output Mental Model

```text
User Input
    ↓
FastAPI
    ↓
OpenAI API
    ↓
Structured Output Schema
    ↓
AI Model
    ↓
Validated Structured Data
    ↓
Python Object
    ↓
FastAPI JSON Response
```

---

# 5. Pydantic and Structured Output

Since you are already using FastAPI, Pydantic is a natural fit.

Example:

```python
from pydantic import BaseModel


class CustomerDecision(BaseModel):
    customer_name: str
    risk_level: str
    approved: bool
```

This model defines the expected structure.

Conceptually:

```text
CustomerDecision
   │
   ├── customer_name: string
   ├── risk_level: string
   └── approved: boolean
```

---

# 6. First Structured Output Example

```python
from pydantic import BaseModel
from openai import OpenAI


client = OpenAI()


class CustomerDecision(BaseModel):
    customer_name: str
    risk_level: str
    approved: bool


response = client.responses.parse(
    model="gpt-6-luna",
    input="""
    Customer: John Smith
    Credit score: 780
    Debt level: Low

    Determine the customer's risk level
    and whether the application should be approved.
    """,
    text_format=CustomerDecision
)


result = response.output_parsed

print(result)
```

The SDK converts the response into a typed Pydantic object.

---

# 7. What `client.responses.parse()` Does

This is important:

```python
response = client.responses.parse(
    model="gpt-6-luna",
    input="...",
    text_format=CustomerDecision
)
```

Think of it as:

```text
Pydantic Model
      ↓
JSON Schema
      ↓
OpenAI API
      ↓
Model produces matching output
      ↓
OpenAI SDK
      ↓
Pydantic Object
```

The Python SDK can automatically convert a Pydantic model into a schema and parse the response back into that model.

---

# 8. Read the Parsed Result

Use:

```python
result = response.output_parsed
```

Then access strongly typed fields:

```python
print(result.customer_name)
print(result.risk_level)
print(result.approved)
```

This is much cleaner than parsing strings manually.

---

# 9. Full  Example

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

class CustomerDecision(BaseModel):
    customer_name: str
    risk_level: str
    approved: bool


@app.post("/customer_decision")
def customer_decision(decision: CustomerDecision):
    prompt = f"""
    Customer Name: {decision.customer_name}
    Risk Level: {decision.risk_level}
    Approved: {decision.approved}

    Please provide a brief summary of the customer's decision.
    """

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return {
            "customer_name": decision.customer_name,
            "risk_level": decision.risk_level,
            "approved": decision.approved,
            "summary": response.output_text
        }    
```

Possible structured result:

```json
{
  "name": "Retrieval-Augmented Generation",
  "definition": "A technique that combines retrieval with language generation.",
  "example": "A chatbot searches company documents before answering."
}
```

---

# 10. Connect Structured Output to FastAPI

Create request and response models.

```python
from pydantic import BaseModel


class ConceptRequest(BaseModel):
    topic: str


class ConceptResponse(BaseModel):
    name: str
    definition: str
    example: str
```

Then:

```python
@app.post("/concept", response_model=ConceptResponse)
def explain_concept(request: ConceptRequest):

    response = client.responses.parse(
        model="gpt-6-luna",
        input=f"Explain this AI topic: {request.topic}",
        text_format=ConceptResponse
    )

    return response.output_parsed
```

Now FastAPI and OpenAI both work with the same schema.

---

# 11. End-to-End Flow

Request:

```json
{
  "topic": "Embeddings"
}
```

Flow:

```text
POST /concept
      ↓
ConceptRequest
      ↓
OpenAI Responses API
      ↓
ConceptResponse schema
      ↓
AI Model
      ↓
Parsed ConceptResponse
      ↓
FastAPI
      ↓
JSON
```

Response:

```json
{
  "name": "Embeddings",
  "definition": "Numerical representations of meaning.",
  "example": "Two similar sentences have similar embedding vectors."
}
```

---

# 12. Use Enums for Controlled Values

Suppose risk level must be one of:

```text
Low
Medium
High
```

Use an enum:

```python
from enum import Enum
from pydantic import BaseModel


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class CustomerDecision(BaseModel):
    customer_name: str
    risk_level: RiskLevel
    approved: bool
```

Now `risk_level` must match one of the allowed values.

---

# 13. FastAPI Example with Enum

```python
from enum import Enum
from pydantic import BaseModel


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class LoanRequest(BaseModel):
    customer_name: str
    income: float
    credit_score: int
    debt: float


class LoanDecision(BaseModel):
    customer_name: str
    risk_level: RiskLevel
    approved: bool
    reason: str
```

Endpoint:

```python
@app.post("/loan-decision", response_model=LoanDecision)
def loan_decision(request: LoanRequest):

    response = client.responses.parse(
        model="gpt-6-luna",
        instructions="""
        Evaluate the application conservatively.

        Consider:
        - Income
        - Credit score
        - Existing debt
        """,
        input=f"""
        Customer: {request.customer_name}
        Income: {request.income}
        Credit Score: {request.credit_score}
        Debt: {request.debt}
        """,
        text_format=LoanDecision
    )

    return response.output_parsed
```

---

# 14. Structured Output with Lists

```python
from pydantic import BaseModel


class Concept(BaseModel):
    name: str
    definition: str


class LearningPlan(BaseModel):
    title: str
    concepts: list[Concept]
```

Call:

```python
response = client.responses.parse(
    model="gpt-6-luna",
    input="Create a beginner learning plan for RAG.",
    text_format=LearningPlan
)
```

---

# 15. Example Result with a List

```json
{
  "title": "Introduction to RAG",
  "concepts": [
    {
      "name": "Embeddings",
      "definition": "Numeric representations of semantic meaning."
    },
    {
      "name": "Vector Database",
      "definition": "A database optimized for similarity search."
    },
    {
      "name": "Retrieval",
      "definition": "Finding relevant information before generation."
    }
  ]
}
```

Python:

```python
result = response.output_parsed

for concept in result.concepts:
    print(concept.name)
    print(concept.definition)
```

---

# 16. Nested Structured Output

```python
from pydantic import BaseModel


class Address(BaseModel):
    city: str
    state: str
    country: str


class CustomerProfile(BaseModel):
    name: str
    email: str
    address: Address
```

Example output:

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "address": {
    "city": "Los Angeles",
    "state": "California",
    "country": "United States"
  }
}
```

---

# 17. Nested List Example

```python
class Task(BaseModel):
    title: str
    priority: str


class ProjectPlan(BaseModel):
    project_name: str
    tasks: list[Task]
```

Useful for:

```text
Project plans
Requirements
Risk analysis
Learning plans
Action items
Workflow steps
```

---

# 18. Optional Fields

```python
from typing import Optional
from pydantic import BaseModel


class ContactInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
```

Now email and phone can be missing.

---

# 19. Use `Literal` for Fixed Choices

```python
from typing import Literal
from pydantic import BaseModel


class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
```

This is useful when the valid options are simple and fixed.

---

# 20. Classification Example

```python
class MessageRequest(BaseModel):
    message: str
```

Response:

```python
from typing import Literal


class ClassificationResult(BaseModel):
    category: Literal[
        "Billing",
        "Technical",
        "Account",
        "Other"
    ]
    reason: str
```

Endpoint:

```python
@app.post("/classify", response_model=ClassificationResult)
def classify(request: MessageRequest):

    response = client.responses.parse(
        model="gpt-6-luna",
        instructions="""
        Classify the customer message.

        Available categories:
        Billing
        Technical
        Account
        Other
        """,
        input=request.message,
        text_format=ClassificationResult
    )

    return response.output_parsed
```

---

# 21. Example Classification Request

```json
{
  "message": "I cannot reset my password."
}
```

Response:

```json
{
  "category": "Account",
  "reason": "The issue concerns access to the user's account."
}
```

---

# 22. Information Extraction Example

Input:

```text
My name is Sarah Johnson.
I work at ABC Bank.
My email is sarah@example.com.
```

Schema:

```python
class PersonInfo(BaseModel):
    name: str
    company: str
    email: str
```

Call:

```python
response = client.responses.parse(
    model="gpt-6-luna",
    instructions="Extract the requested information from the user's text.",
    input=request.text,
    text_format=PersonInfo
)
```

---

# 23. Meeting Notes Example

```python
class ActionItem(BaseModel):
    task: str
    owner: str
    due_date: str | None = None


class MeetingSummary(BaseModel):
    summary: str
    decisions: list[str]
    action_items: list[ActionItem]
```

Call:

```python
response = client.responses.parse(
    model="gpt-6-luna",
    instructions="""
    Analyze the meeting notes.

    Extract:
    - Summary
    - Decisions
    - Action items
    """,
    input=request.notes,
    text_format=MeetingSummary
)
```

---

# 24. Example Meeting Output

```json
{
  "summary": "The team agreed to begin the AI pilot next month.",
  "decisions": [
    "Use FastAPI for the backend",
    "Begin with one business use case"
  ],
  "action_items": [
    {
      "task": "Prepare architecture diagram",
      "owner": "Project Lead",
      "due_date": "2026-10-10"
    }
  ]
}
```

---

# 25. Support Ticket Example

```python
class SupportTicketResult(BaseModel):
    category: str
    priority: Literal["Low", "Medium", "High", "Critical"]
    summary: str
    requires_human: bool
```

Then:

```python
response = client.responses.parse(
    model="gpt-6-luna",
    input=request.message,
    text_format=SupportTicketResult
)
```

---

# 26. Structured Output for Document Analysis

```python
class DocumentAnalysis(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    risks: list[str]
    recommendations: list[str]
```

Call:

```python
response = client.responses.parse(
    model="gpt-6-luna",
    input=request.document,
    text_format=DocumentAnalysis
)
```

---

# 27. Why Not Just Use `response.output_text`?

Normal text generation:

```python
response = client.responses.create(...)
answer = response.output_text
```

Structured parsing:

```python
response = client.responses.parse(
    ...,
    text_format=MyModel
)

result = response.output_parsed
```

Compare:

```text
output_text
   ↓
string
```

versus:

```text
output_parsed
   ↓
Pydantic object
```

---

# 28. JSON Schema Approach

You can also define Structured Output using JSON Schema directly.

Conceptually:

```python
response = client.responses.create(
    model="gpt-6-luna",
    input="...",
    text={
        "format": {
            "type": "json_schema",
            "name": "customer_decision",
            "schema": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string"
                    },
                    "approved": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "customer_name",
                    "approved"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
)
```

For Python developers using FastAPI, the Pydantic parsing approach is usually easier to learn and maintain.

---

# 29. Pydantic vs Manual JSON Schema

## Pydantic

```python
class CustomerDecision(BaseModel):
    customer_name: str
    approved: bool
```

Benefits:

```text
Shorter
Python-native
Type-safe
Works well with FastAPI
Easy validation
Easy IDE support
```

## Manual JSON Schema

Useful when:

```text
Schema comes from another system
You need language-neutral schema definitions
You generate schemas dynamically
You are integrating with non-Python services
```

---

# 30. Structured Output Error Handling

```python
@app.post("/concept", response_model=ConceptResponse)
def concept(request: ConceptRequest):

    try:
        response = client.responses.parse(
            model="gpt-6-luna",
            input=request.topic,
            text_format=ConceptResponse
        )

        result = response.output_parsed

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="The AI response could not be parsed."
            )

        return result

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate structured response."
        )
```

---

# 31. Refusals and Missing Parsed Output

Structured output does not mean every response will always become a successful business result.

Possible reasons:

```text
Safety refusal
Incomplete response
API error
Network problem
Application error
```

Always check:

```python
result = response.output_parsed

if result is None:
    raise HTTPException(
        status_code=500,
        detail="No structured result was returned."
    )
```

---

# 32. Add Business Validation

Structured Output validates shape.

Your application may still need business rules.

Example:

```python
from pydantic import BaseModel, Field


class SentimentResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)
```

Now confidence must be between 0 and 1.

---

# 33. Useful Pydantic Validation

```python
from pydantic import BaseModel, Field


class ProductReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=300)
```

Now:

```text
rating must be 1–5
summary cannot be empty
summary cannot exceed 300 characters
```

---

# 34. Complete FastAPI Structured Output Example

```python
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

app = FastAPI(
    title="Structured Output Learning API",
    version="1.0.0"
)

client = OpenAI()


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class LoanRequest(BaseModel):
    customer_name: str
    income: float = Field(gt=0)
    credit_score: int = Field(ge=300, le=850)
    existing_debt: float = Field(ge=0)


class LoanDecision(BaseModel):
    customer_name: str
    risk_level: RiskLevel
    approved: bool
    reason: str
    confidence: float = Field(ge=0, le=1)


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/loan-decision", response_model=LoanDecision)
def loan_decision(request: LoanRequest):

    try:
        response = client.responses.parse(
            model="gpt-6-luna",
            instructions="""
            You are a loan-risk analysis assistant.

            Evaluate the application using:
            - Income
            - Credit score
            - Existing debt

            Return a conservative risk assessment.
            """,
            input=f"""
            Customer Name: {request.customer_name}
            Income: {request.income}
            Credit Score: {request.credit_score}
            Existing Debt: {request.existing_debt}
            """,
            text_format=LoanDecision
        )

        result = response.output_parsed

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="No structured result was returned."
            )

        return result

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate loan decision."
        )
```

---

# 35. Test in Swagger

Run:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Test:

```text
POST /loan-decision
```

Request:

```json
{
  "customer_name": "John Smith",
  "income": 95000,
  "credit_score": 760,
  "existing_debt": 15000
}
```

Possible response:

```json
{
  "customer_name": "John Smith",
  "risk_level": "Low",
  "approved": true,
  "reason": "Strong credit score and manageable debt relative to income.",
  "confidence": 0.91
}
```

---

# 36. Practice Exercise 1 — AI Concept

Create:

```text
POST /concept
```

Request:

```json
{
  "topic": "Vector Database"
}
```

Structured response:

```json
{
  "name": "Vector Database",
  "definition": "...",
  "example": "...",
  "why_it_matters": "..."
}
```

---

# 37. Practice Exercise 2 — Sentiment Analysis

Create:

```text
POST /sentiment
```

Request:

```json
{
  "text": "The new application is very easy to use."
}
```

Response schema:

```json
{
  "sentiment": "positive",
  "confidence": 0.95,
  "reason": "..."
}
```

---

# 38. Practice Exercise 3 — Support Ticket

Create:

```text
POST /support-ticket
```

Request:

```json
{
  "message": "Our production API has been down for 30 minutes."
}
```

Return:

```json
{
  "category": "Technical",
  "priority": "Critical",
  "summary": "...",
  "requires_human": true
}
```

---

# 39. Practice Exercise 4 — Resume Extraction

Request:

```json
{
  "text": "Senior software engineer with 10 years..."
}
```

Structured result:

```json
{
  "candidate_name": "...",
  "skills": [
    "...",
    "..."
  ],
  "years_experience": 10,
  "current_role": "..."
}
```

---

# 40. Practice Exercise 5 — Meeting Analysis

Create:

```text
POST /meeting-analysis
```

Return:

```json
{
  "summary": "...",
  "decisions": [
    "..."
  ],
  "action_items": [
    {
      "task": "...",
      "owner": "...",
      "due_date": "..."
    }
  ]
}
```

Use nested Pydantic models.

---

# 41. Practice Exercise 6 — Course Generator

Input:

```json
{
  "topic": "RAG",
  "level": "beginner"
}
```

Output:

```json
{
  "course_title": "...",
  "description": "...",
  "lessons": [
    {
      "lesson_number": 1,
      "title": "...",
      "objective": "..."
    }
  ]
}
```

---

# 42. Practice Exercise 7 — Risk Analysis

Input:

```json
{
  "text": "The application depends on one external API..."
}
```

Return:

```json
{
  "overall_risk": "Medium",
  "risks": [
    {
      "name": "External API dependency",
      "severity": "Medium",
      "mitigation": "Add retries and fallback behavior"
    }
  ]
}
```

---

# 43. Good Structured Output Design

Good schemas are:

```text
Simple
Specific
Small enough to understand
Typed
Validated
Business-oriented
```

Avoid giant schemas until you actually need them.

---

# 44. Common Mistakes

Avoid:

```text
Using free-form strings for fixed categories
Making every field optional
Creating overly complicated nested schemas
Mixing unrelated concerns in one response model
Trusting structured output as business authorization
Skipping application-level validation
Ignoring missing parsed results
```

---

# 45. Structured Output Does Not Replace Business Logic

Structured Output controls format.

It does not automatically make AI decisions authoritative.

Important decisions may still require:

```text
Rules engine
Database validation
Human approval
Regulatory controls
Audit logging
Authorization
Threshold checks
```

---

# 46. Structured Output and Prompt Engineering Together

Prompt Engineering defines behavior:

```text
What should the model do?
```

Structured Output defines shape:

```text
What exact data should the model return?
```

Together:

```text
Prompt Engineering
      ↓
Meaning and instructions

Structured Output
      ↓
Schema and data contract
```

---

# 47. Structured Output and FastAPI Together

FastAPI:

```python
response_model=LoanDecision
```

OpenAI:

```python
text_format=LoanDecision
```

This creates a shared contract:

```text
OpenAI
   ↓
LoanDecision
   ↓
FastAPI
   ↓
Client
```

---

# 48. When to Use Structured Output

Use Structured Output when your application needs:

```text
Classification
Extraction
Database-ready fields
Form population
Workflow routing
Risk analysis
Action items
Metadata
Entity extraction
UI cards
API responses
Decision-support data
```

Use normal text when the user simply wants:

```text
Explanation
Essay
Conversation
Creative writing
Open-ended answer
```

---

# 49. Structured Output Mental Checklist

Before creating a schema, ask:

```text
What fields does my application actually need?

Which fields are required?

Which fields can be optional?

Which values should be enums?

Do I need lists?

Do I need nested objects?

Do I need numeric ranges?

What business validation happens after the AI response?
```

---

# 50. Recommended Project Structure

```text
ai-fastapi-learning/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py
│   │   └── responses.py
│   │
│   └── prompts/
│       ├── __init__.py
│       └── prompts.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 51. Example Model File

```python
# app/models/responses.py

from enum import Enum
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class LoanDecision(BaseModel):
    customer_name: str
    risk_level: RiskLevel
    approved: bool
    reason: str
    confidence: float = Field(ge=0, le=1)
```

Then:

```python
from app.models.responses import LoanDecision
```

---

# 52. Current Learning Progress

```text
✅ FastAPI
✅ OpenAI API
✅ Prompt Engineering
✅ Structured Output

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

---

# 53. Next Step — Function / Tool Calling

The next topic is:

```text
FastAPI
   ↓
OpenAI API
   ↓
Prompt Engineering
   ↓
Structured Output
   ↓
Function / Tool Calling   ← NEXT
```

Structured Output tells the model:

```text
Return data in this shape.
```

Tool Calling lets the model say:

```text
I need your application to call this function.
```

Example:

```text
User:
"What is the weather in Los Angeles?"

AI:
"I need the weather tool."

Application:
Calls weather API

Weather API:
Returns 72°F

AI:
"The current temperature is 72°F."
```

This is one of the major steps toward AI Agents.

---

# 54. Recommended Practice Strategy

For each structured-output exercise:

```text
Define the business problem
        ↓
Design the Pydantic model
        ↓
Call responses.parse()
        ↓
Inspect output_parsed
        ↓
Test valid data
        ↓
Test missing data
        ↓
Test unexpected input
        ↓
Add validation
        ↓
Return through FastAPI
```

The most important learning goal is this:

```text
Do not think only in prompts.

Think in:

Prompt
+
Schema
+
Validation
+
Business Logic
```

That is how AI features become real application components.
