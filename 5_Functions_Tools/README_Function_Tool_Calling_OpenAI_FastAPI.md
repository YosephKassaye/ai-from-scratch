# Function / Tool Calling with OpenAI API — Step-by-Step Practice Guide

This project continues the AI learning path:

```text
FastAPI
   ↓
OpenAI API
   ↓
Prompt Engineering
   ↓
Structured Output
   ↓
Function / Tool Calling   ← YOU ARE HERE
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

The goal of this README is to learn how an AI model can decide when it needs an external function, ask your application to execute that function, receive the result, and then continue generating the final answer.

---

# 1. What is Function / Tool Calling?

A language model can generate text, but your application may need access to external data or actions.

Examples:

```text
Get current weather
Look up a customer
Query a database
Calculate shipping cost
Create a support ticket
Check an order
Call another API
```

Tool calling lets you describe these capabilities to the model.

The model can then request a tool call.

Important:

```text
The model does not directly execute your Python function.
Your application executes it.
```

---

# 2. Tool Calling Mental Model

```text
User
  ↓
FastAPI
  ↓
OpenAI API
  ↓
Model sees available tools
  ↓
Model requests a tool
  ↓
Your Python application executes it
  ↓
Application sends the result back
  ↓
Model reads the tool result
  ↓
Model generates the final answer
```

---

# 3. The Five-Step Flow

```text
1. Send prompt + tools
2. Receive function call
3. Execute the function
4. Send function result back
5. Receive final response
```

The model may request zero, one, or multiple tools.

---

# 4. Create a Simple Python Function

```python
def get_weather(location: str):
    return {
        "location": location,
        "temperature": 72,
        "unit": "fahrenheit",
        "condition": "Sunny"
    }
```

For learning, this returns sample data.

Later, you can replace it with a real external API.

---

# 5. Define the Tool

```python
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state or city and country."
                }
            },
            "required": ["location"],
            "additionalProperties": False
        },
        "strict": True
    }
]
```

Important properties:

```text
type
name
description
parameters
strict
```

---

# 6. First Tool Calling Request

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-astra",
    input="What is the weather in Los Angeles?",
    tools=tools
)
```

The model may return a function request instead of a final text answer.

---

# 7. Inspect Function Calls

Function calls are returned in:

```python
response.output
```

Example:

```python
for item in response.output:

    if item.type == "function_call":

        print(item.name)
        print(item.arguments)
        print(item.call_id)
```

Conceptually, a function call contains:

```json
{
  "type": "function_call",
  "name": "get_weather",
  "arguments": "{\"location\":\"Los Angeles\"}",
  "call_id": "call_123"
}
```

---

# 8. Parse the Arguments

```python
import json

args = json.loads(item.arguments)
```

Now:

```python
args["location"]
```

might contain:

```text
Los Angeles
```

---

# 9. Execute the Function

```python
result = get_weather(
    location=args["location"]
)
```

Example result:

```json
{
  "location": "Los Angeles",
  "temperature": 72,
  "unit": "fahrenheit",
  "condition": "Sunny"
}
```

---

# 10. Send the Tool Result Back

Create a `function_call_output` item:

```python
tool_output = {
    "type": "function_call_output",
    "call_id": item.call_id,
    "output": json.dumps(result)
}
```

The `call_id` connects the function result to the correct tool request.

---

# 11. Multi-Tool Implementation + Project Structure (Current)

The project now supports multiple tools (`get_weather`, `get_customer`) and uses a safer continuation pattern with `previous_response_id`.

Why this matters:

```text
When the model emits function_call items, do not replay raw response.output items
back as-is in a new request. Instead, send function_call_output items and continue
from previous_response_id.
```

Current structure used in this project:

```text
5_Functions_Tools/
├── README_Function_Tool_Calling_OpenAI_FastAPI.md
└── app/
    ├── __init__.py
    ├── main.py
    ├── models/
    │   └── models.py
    ├── services/
    │   └── ai_service.py
    └── tools/
        ├── tools.py
        └── tool_executor.py
```

Section responsibilities:

```text
app/main.py
  FastAPI routes and request/response wiring

app/models/models.py
  Pydantic request models (for example, ChatRequest)

app/tools/tools.py
  Tool functions + OpenAI tool schemas + TOOL_FUNCTIONS registry

app/tools/tool_executor.py
  Executes requested tools from tool name + JSON arguments

app/services/ai_service.py
  Orchestrates OpenAI calls, tool detection, and continuation
```

Updated multi-tool orchestration pattern:

```python
import json
from dotenv import load_dotenv
from openai import OpenAI

from app.tools.tools import TOOLS
from app.tools.tool_executor import execute_tool


load_dotenv()
client = OpenAI()


def process_message(message: str) -> str:
    response = client.responses.create(
        model="gpt-5",
        instructions="""
        You are a helpful AI assistant.
        Use available tools when necessary.
        If the user asks about weather, use get_weather.
        If the user asks about a customer, use get_customer.
        """,
        input=message,
        tools=TOOLS
    )

    tool_outputs = []

    for item in response.output:
        if item.type == "function_call":
            result = execute_tool(item.name, item.arguments)
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                }
            )

    if tool_outputs:
        follow_up = client.responses.create(
            model="gpt-5",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS
        )
        return follow_up.output_text

    return response.output_text
```

Benefits of this approach:

```text
Supports multiple tools in one request
Keeps tool dispatch logic reusable
Avoids function_call/reasoning mismatch errors
Matches a clean service-first project layout
```

---

# 12. Understand the Full Flow

```text
User asks:
"What is the weather in Los Angeles?"

        ↓

Model sees:
get_weather tool

        ↓

Model returns:
get_weather("Los Angeles")

        ↓

Python executes:
get_weather()

        ↓

Tool returns:
{
  "temperature": 72,
  "condition": "Sunny"
}

        ↓

Application sends:
function_call_output

        ↓

Model returns:
"The weather is sunny and 72°F."
```

---

# 13. Why Send `response.output` Back?

This line:

```python
input_items += response.output
```

preserves the model's tool request in the conversation history.

Then your application adds the corresponding result:

```python
input_items.append(
    {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result)
    }
)
```

The next request gives the model both:

```text
Tool request
Tool result
```

---

# 14. Add a Second Tool

```python
def get_customer(customer_id: int):

    customers = {
        1: {
            "customer_id": 1,
            "name": "John Smith",
            "status": "Active"
        },
        2: {
            "customer_id": 2,
            "name": "Sarah Johnson",
            "status": "Inactive"
        }
    }

    return customers.get(
        customer_id,
        {
            "error": "Customer not found"
        }
    )
```

Tool definition:

```python
customer_tool = {
    "type": "function",
    "name": "get_customer",
    "description": "Retrieve customer information using a customer ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "Unique customer ID."
            }
        },
        "required": ["customer_id"],
        "additionalProperties": False
    },
    "strict": True
}
```

---

# 15. Multiple Tools

```python
tools = [
    weather_tool,
    customer_tool
]
```

Now the model can choose the correct tool.

Examples:

```text
"What is the weather in Chicago?"
        ↓
get_weather

"What is the status of customer 1?"
        ↓
get_customer
```

---

# 16. Better Tool Registry

```python
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_customer": get_customer
}
```

Then:

```python
function = TOOL_FUNCTIONS.get(item.name)

if function is None:

    result = {
        "error": "Unknown tool"
    }

else:

    result = function(**args)
```

---

# 17. Reusable Tool Loop

A model may need more than one round of tool calls.

```python
import json


def run_agent(user_message: str):

    input_items = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    max_iterations = 5

    for _ in range(max_iterations):

        response = client.responses.create(
            model="gpt-6-astra",
            input=input_items,
            tools=tools
        )

        input_items += response.output

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text

        for call in function_calls:

            args = json.loads(call.arguments)

            function = TOOL_FUNCTIONS.get(
                call.name
            )

            if function is None:

                result = {
                    "error": f"Unknown tool: {call.name}"
                }

            else:

                result = function(**args)

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result)
                }
            )

    return "Maximum tool iterations reached."
```

This is the beginning of an agent-style tool loop.

---

# 18. Why Limit Iterations?

Do not allow an unlimited loop.

```python
max_iterations = 5
```

Production systems may also add:

```text
Timeouts
Token limits
Tool-call limits
Cost limits
Retries
Audit logs
```

---

# 19. FastAPI Integration

```python
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
```

Endpoint:

```python
@app.post("/chat")
def chat(request: ChatRequest):

    answer = run_agent(
        request.message
    )

    return {
        "question": request.message,
        "answer": answer
    }
```

---

# 20. Complete FastAPI Example

```python
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


app = FastAPI(
    title="Tool Calling Learning API",
    version="1.0.0"
)


client = OpenAI()


class ChatRequest(BaseModel):
    message: str


def get_weather(location: str):

    return {
        "location": location,
        "temperature": 72,
        "unit": "fahrenheit",
        "condition": "Sunny"
    }


def get_customer(customer_id: int):

    customers = {
        1: {
            "customer_id": 1,
            "name": "John Smith",
            "status": "Active"
        },
        2: {
            "customer_id": 2,
            "name": "Sarah Johnson",
            "status": "Inactive"
        }
    }

    return customers.get(
        customer_id,
        {
            "error": "Customer not found"
        }
    )


tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get current weather information for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state or city and country."
                }
            },
            "required": ["location"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "get_customer",
        "description": "Retrieve customer information by customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "Unique customer ID."
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False
        },
        "strict": True
    }
]


TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_customer": get_customer
}


def run_agent(user_message: str):

    input_items = [
        {
            "role": "user",
            "content": user_message
        }
    ]

    max_iterations = 5

    for _ in range(max_iterations):

        response = client.responses.create(
            model="gpt-6-astra",
            instructions=(
                "You are a helpful application assistant. "
                "Use available tools when external application data is required. "
                "Do not invent tool results."
            ),
            input=input_items,
            tools=tools
        )

        input_items += response.output

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            return response.output_text

        for call in function_calls:

            try:

                args = json.loads(
                    call.arguments
                )

                function = TOOL_FUNCTIONS.get(
                    call.name
                )

                if function is None:

                    result = {
                        "error": "Unknown tool"
                    }

                else:

                    result = function(**args)

            except Exception as ex:

                result = {
                    "error": str(ex)
                }

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result)
                }
            )

    return "Maximum tool iterations reached."


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    try:

        answer = run_agent(
            request.message
        )

        return {
            "question": request.message,
            "answer": answer
        }

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Unable to process AI request."
        )
```

---

# 21. Test with Swagger

Run:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Try:

```json
{
  "message": "What is the weather in Los Angeles?"
}
```

Then:

```json
{
  "message": "What is the status of customer 1?"
}
```

---

# 22. Multiple Calls in One Response

The model may request several function calls.

Example:

```text
What is the weather in Los Angeles and Chicago?
```

The model may request:

```text
get_weather("Los Angeles")
get_weather("Chicago")
```

That is why the application loops through all function calls.

---

# 23. Tool Calling with a Calculator

```python
def calculate_total(
    price: float,
    quantity: int
):

    return {
        "price": price,
        "quantity": quantity,
        "total": price * quantity
    }
```

Tool definition:

```python
{
    "type": "function",
    "name": "calculate_total",
    "description": "Calculate total cost from price and quantity.",
    "parameters": {
        "type": "object",
        "properties": {
            "price": {
                "type": "number"
            },
            "quantity": {
                "type": "integer"
            }
        },
        "required": [
            "price",
            "quantity"
        ],
        "additionalProperties": False
    },
    "strict": True
}
```

---

# 24. Tool Calling with a Database

```python
def get_order(order_id: int):

    # Database query would happen here.

    return {
        "order_id": order_id,
        "status": "Shipped",
        "tracking_number": "TRK123456"
    }
```

User:

```text
Where is order 100?
```

The model can request:

```text
get_order(order_id=100)
```

Your application performs the database lookup.

---

# 25. Tool Calling with External APIs

Your function could call:

```text
Weather API
Payment API
Shipping API
CRM API
Microsoft Graph
Salesforce
ServiceNow
Internal enterprise API
```

Architecture:

```text
User
  ↓
AI
  ↓
Tool Call
  ↓
FastAPI
  ↓
External API
  ↓
FastAPI
  ↓
Tool Output
  ↓
AI
  ↓
User
```

---

# 26. Tool Calling vs Structured Output

## Structured Output

Use when the model should return predictable data.

```json
{
  "category": "Billing",
  "priority": "High"
}
```

## Tool Calling

Use when the model needs your application to retrieve data or perform an action.

```text
get_customer(customer_id=10)
```

---

# 27. Structured Output + Tool Calling

They can work together.

```text
User asks about customer risk
        ↓
AI calls get_customer()
        ↓
Application returns customer information
        ↓
AI analyzes information
        ↓
AI returns structured risk assessment
```

This pattern is common in enterprise AI applications.

---

# 28. Read Tools vs Write Tools

## Read tools

Examples:

```text
get_customer
get_order
search_products
get_weather
```

## Write tools

Examples:

```text
send_email
issue_refund
cancel_order
create_ticket
update_customer
```

Write tools are higher risk.

---

# 29. Tool Security

Never treat the model as your security system.

Your application must enforce:

```text
Authentication
Authorization
Resource ownership
Business rules
Data permissions
Approval requirements
Audit logging
```

Example:

```python
if not current_user.is_admin:
    raise PermissionError(
        "User is not authorized."
    )
```

---

# 30. Human-in-the-Loop

For important write operations:

```text
AI suggests action
      ↓
Human reviews
      ↓
Human approves
      ↓
Application executes tool
```

Example:

```text
AI suggests a $500 refund
      ↓
User clicks "Approve"
      ↓
issue_refund()
```

---

# 31. Minimum Tool Access

Do not expose unnecessary tools.

If the application only needs:

```text
get_customer
```

do not also expose:

```text
delete_customer
transfer_money
reset_production
```

Principle:

```text
Give the model the minimum tools required.
```

---

# 32. Validate Tool Arguments

Even with strict schemas, important inputs should also be validated by your application.

```python
def get_customer(customer_id: int):

    if customer_id <= 0:

        return {
            "error": "Invalid customer ID."
        }
```

---

# 33. Tool Error Handling

```python
try:

    result = function(**args)

except Exception as ex:

    result = {
        "success": False,
        "error": str(ex)
    }
```

Then send the error result back to the model.

---

# 34. Better Error Results

Prefer:

```json
{
  "success": false,
  "error_code": "CUSTOMER_NOT_FOUND",
  "message": "Customer 100 was not found."
}
```

over vague errors such as:

```text
Something went wrong
```

---

# 35. Recommended Project Structure

```text
ai-fastapi-learning/
│
├── app/
│   ├── main.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── weather.py
│   │   ├── customers.py
│   │   ├── orders.py
│   │   └── schemas.py
│   │
│   ├── models/
│   │   ├── requests.py
│   │   └── responses.py
│   │
│   └── prompts/
│       └── assistant.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 36. Practice Exercise 1 — Calculator Tool

Create:

```text
calculate_total
```

Parameters:

```text
price
quantity
```

Ask:

```text
What is the total for 5 items costing $19.99 each?
```

---

# 37. Practice Exercise 2 — Customer Lookup

Create:

```text
get_customer
```

Ask:

```text
Tell me the status of customer 2.
```

Return data from a Python dictionary.

---

# 38. Practice Exercise 3 — Order Lookup

Create:

```text
get_order
```

Return:

```json
{
  "order_id": 100,
  "status": "Shipped",
  "tracking_number": "TRK123"
}
```

Ask:

```text
Where is order 100?
```

---

# 39. Practice Exercise 4 — Multiple Tools

Create:

```text
get_customer
get_order
```

Ask:

```text
Show me customer 1 and order 100.
```

Allow the model to use both tools.

---

# 40. Practice Exercise 5 — Support Ticket

Create:

```text
create_support_ticket
```

Arguments:

```text
title
description
priority
```

For practice, return:

```json
{
  "ticket_id": 5001,
  "status": "Created"
}
```

Before using a real write operation, consider:

```text
Authorization
Confirmation
Audit logging
```

---

# 41. Practice Exercise 6 — Tool Failure

Ask:

```text
Find customer 999.
```

Return:

```json
{
  "error": "Customer not found"
}
```

Observe how the model explains the error.

---

# 42. Practice Exercise 7 — Tool Loop

Set:

```python
max_iterations = 5
```

Test the loop and verify that the application stops if the model repeatedly requests tools.

---

# 43. Common Mistakes

Avoid:

```text
Assuming the model executes your Python function
Ignoring call_id
Assuming there is only one tool call
Skipping argument validation
Giving the model too many tools
Allowing unlimited tool loops
Using write tools without authorization
Returning unclear error messages
Putting every tool in main.py
Trusting model-generated arguments blindly
```

---

# 44. Tool Calling Mental Checklist

Before exposing a tool, ask:

```text
What does the tool do?
Is it read-only or a write action?
What arguments are required?
Are the argument types constrained?
Does the user have permission?
Could the action cause harm?
Should a human approve it?
What happens if it fails?
What data should be returned?
Should the action be logged?
```

---

# 45. Function Calling and Agents

Tool calling is one of the foundations of AI agents.

Without tools:

```text
AI
 ↓
Generate text
```

With tools:

```text
AI
 ↓
Decide
 ↓
Use tool
 ↓
Observe
 ↓
Decide again
 ↓
Use another tool
 ↓
Final answer
```

This becomes an agent-style loop.

---

# 46. Built-in Tools vs Your Functions

## Your functions

```text
get_customer
calculate_shipping
create_ticket
query_database
```

You define and execute them.

## Built-in / hosted tools

OpenAI also provides capabilities such as:

```text
Web search
File search
Code execution
MCP-connected tools
```

These are separate from the custom function tools in this lesson.

---

# 47. Current AI Learning Progress

```text
✅ FastAPI
✅ OpenAI API
✅ Prompt Engineering
✅ Structured Output
✅ Function / Tool Calling

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

# 48. Next Step — Embeddings

Next:

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
Embeddings   ← NEXT
```

Embeddings convert meaning into numerical vectors.

Example:

```text
"How do I reset my password?"
       ↓
Embedding
       ↓
[0.021, -0.145, 0.832, ...]
```

Similar meanings tend to have similar vector representations.

This leads to:

```text
Embeddings
   ↓
Vector Database
   ↓
Semantic Search
   ↓
RAG
```

---

# 49. Recommended Practice Strategy

```text
Create one Python function
        ↓
Define its tool schema
        ↓
Send the tool to the model
        ↓
Inspect function_call
        ↓
Parse arguments
        ↓
Execute the function
        ↓
Send function_call_output
        ↓
Receive final answer
        ↓
Add a second tool
        ↓
Build a tool registry
        ↓
Add a tool loop
        ↓
Add security and validation
        ↓
Integrate with FastAPI
```

The most important concept is:

```text
The model decides WHEN a tool may be useful.

Your application decides WHETHER and HOW it is executed.
```

---

# 50. Current API Note

OpenAI's current guidance uses the Responses API for modern function/tool calling.

For function tools:

```text
type = function
parameters = JSON Schema
strict = true
```

Tool requests are returned as:

```text
function_call
```

Tool results are sent back as:

```text
function_call_output
```

and connected using:

```text
call_id
```

Always check the current OpenAI API documentation when changing SDK versions or models, because capabilities can evolve over time.
