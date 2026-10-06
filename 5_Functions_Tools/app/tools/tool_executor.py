# tool_executor.py

import json
from app.tools.tools import TOOL_FUNCTIONS


def execute_tool(tool_name: str, arguments: str):

    function = TOOL_FUNCTIONS.get(tool_name)

    if not function:
        return {
            "error": f"Tool '{tool_name}' does not exist."
        }

    args = json.loads(arguments)

    result = function(**args)

    return result