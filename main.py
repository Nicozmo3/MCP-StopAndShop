import sys
from mcp_adapter_http import MCPHttpAdapter
from mcp_adapter_stdio import MCPStdioAdapter
from mcp_server import MCPServer


DEFAULT_LISTENING_PORT: int = 8080
DEFAULT_LISTENING_INTF: str = 'localhost'
DEFAULT_TRANSPORT: str = 'http'

mcp = MCPServer('stopandshop-moderation', 'A moderation server for Stop and Shop')


@mcp.tool(name="get_reviews", description="Get user reviews for a product", output_schema={
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "review_id": {"type": "integer"},
            "content": {"type": "string"},
            "rating": {"type": "integer"}
        },
        "required": ["review_id", "content", "rating"]
    }
})
def get_reviews():
    print("User reviews requested")
    return [
        {"review_id": 1, "content": "Truc1", "rating": 5},
        {"review_id": 2, "content": "Truc2", "rating": 3},
        {"review_id": 3, "content": "Truc3", "rating": 1}
    ]

@mcp.tool(name="mark_review_as_inappropriate", description="Mark a review as inappropriate")
def mark_review_as_inappropriate(review_id: int):
    print(f"Marking review {review_id} as inappropriate")

    return {"status": "success", "review_id": review_id}


def main(argv: list[str]) -> int:
    transport = argv[1] if len(argv) > 1 else DEFAULT_TRANSPORT

    if transport == 'stdio':
        adapter = MCPStdioAdapter(mcp)
    else:
        listening_intf = argv[2] if len(argv) > 2 else DEFAULT_LISTENING_INTF
        listening_port = int(argv[3]) if len(argv) > 3 else DEFAULT_LISTENING_PORT
        adapter = MCPHttpAdapter(mcp, listening_intf, listening_port)

    adapter.serve()
    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
