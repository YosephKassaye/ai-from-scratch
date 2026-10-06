# tools.py

# --------------------------------
# Tool Functions
# --------------------------------

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


# --------------------------------
# OpenAI Tool Definitions
# --------------------------------

weather_tool = {
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


TOOLS = [
    weather_tool,
    customer_tool
]


# Map tool name -> Python function
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_customer": get_customer
}