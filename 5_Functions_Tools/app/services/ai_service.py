# ai_service.py

import json

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.tools import TOOLS
from app.tools.tool_executor import execute_tool


load_dotenv()

client = OpenAI()


def process_message(message: str):

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

    # Gather tool outputs and continue from the previous response state.
    tool_outputs = []

    for item in response.output:
        if item.type == "function_call":
            tool_result = execute_tool(item.name, item.arguments)
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(tool_result)
                }
            )

    if tool_outputs:
        second_response = client.responses.create(
            model="gpt-5",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS
        )

        return second_response.output_text

    # No tool was required
    return response.output_text