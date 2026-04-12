import sys
from mcp_adapter_http import MCPHttpAdapter
from mcp_adapter_stdio import MCPStdioAdapter
from mcp_server import MCPServer
import mysql.connector
import os


DEFAULT_LISTENING_PORT: int = 8080
DEFAULT_LISTENING_INTF: str = 'localhost'
DEFAULT_TRANSPORT: str = 'http'

mcp = MCPServer('stopandshop-moderation', 'A moderation server for Stop and Shop')

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "password"),
        database=os.getenv("DB_NAME", "reviews_db"),
    )

@mcp.tool(
    name="get_comments_since",
    description="Retrieve comments posted after a given date with brand and belief context",
    input_schema={
        "type": "object",
        "properties": {
            "since": {
                "type": "string",
                "format": "date-time",
                "description": "ISO datetime (e.g. 2026-04-01T00:00:00)"
            },
            "limit": {
                "type": "integer",
                "default": 50
            }
        },
        "required": ["since"]
    },
    output_schema={
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "comment_id": {"type": "integer"},
                "text": {"type": "string"},
                "note": {"type": "integer"},
                "created_at": {"type": "string"},
                "upvote_count": {"type": "integer"},
                "downvote_count": {"type": "integer"},
                "is_anonymous": {"type": "boolean"},

                "brand_name": {"type": "string"},

                "belief_title": {"type": "string"},
                "belief_description": {"type": "string"}
            }
        }
    }
)
def get_comments_since(since: str, limit: int = 50):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.comment_id,
            c.text,
            c.note,
            c.created_at,
            c.upvote_count,
            c.downvote_count,
            c.is_anonymous,

            b.name AS brand_name,

            bl.title AS belief_title,
            bl.description AS belief_description

        FROM comment c
        JOIN brand b ON c.concerned_brand_id = b.brand_id
        JOIN belief bl ON c.concerned_belief_id = bl.belief_id

        WHERE c.created_at > %s

        ORDER BY c.created_at ASC
        LIMIT %s
    """

    cursor.execute(query, (since, limit))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

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
