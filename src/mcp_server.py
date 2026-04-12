from json_rpc import build_json_rpc_error_response, build_json_rpc_success_response, validate_json_rpc_request
import inspect
from tool import Tool

MCP_METHOD_INITIALIZE = "initialize"
MCP_METHOD_LIST_TOOLS = "tools/list"
MCP_METHOD_CALL_TOOL = "tools/call"


class MCPServer:

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self._tools = {}

    def tool(self, name: str, description: str, input_schema: dict | None = None, output_schema: dict | None = None):
        def decorator(func):
            tool_name = name or func.__name__
            tool_description = description or func.__doc__ or ""

            self._tools[tool_name] = Tool(name, tool_description, func, input_schema, output_schema)

            return func

        return decorator

    def initialize(self) -> dict:
        return {
            "protocolVersion": "2025-11-25",
            "capabilities": {
                "tools": {
                    # Need notification support
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": self.name,
                "title": self.name,
                "version": "1.0.0",
                "description": self.description,
            }
        }

    def list_tools(self) -> dict:
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema,
                    "outputSchema": tool.output_schema or {"type": "object"}
                }
                for tool in self._tools.values()
            ]
        }

    def call_tool(self, params: dict) -> dict:
        name = params.get("name")
        args = params.get("arguments", {})        

        tool = self._tools.get(name)

        if not tool:
            raise ValueError(f"Tool not found: {name}")

        result = tool.execute(**args)

        return {
            "content": [
                {
                    "type": "json",
                    "json": result
                }
            ]
        }

    def handle_request(self, request: dict) -> dict:
        if not validate_json_rpc_request(request):
            return build_json_rpc_error_response(request.get("id"), -32600, "Invalid JSON-RPC request")

        method = request["method"]
        request_id = request["id"]

        try:
            if method == MCP_METHOD_INITIALIZE:
                result = self.initialize()
            elif method == MCP_METHOD_LIST_TOOLS:
                result = self.list_tools()
            elif method == MCP_METHOD_CALL_TOOL:
                result = self.call_tool(request.get("params", {}))
            else:
                return build_json_rpc_error_response(request_id, -32601, f"Method not found: {method}")
        except ValueError as e:
            return build_json_rpc_error_response(request_id, -32601, str(e))
        except Exception as e:
            return build_json_rpc_error_response(request_id, -32601, f"Error executing method: {str(e)}")

        return build_json_rpc_success_response(request_id, result)
