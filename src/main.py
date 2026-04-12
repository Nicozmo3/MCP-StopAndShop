import sys
from mcp_adapter_http import MCPHttpAdapter
from mcp_adapter_stdio import MCPStdioAdapter
from mcp_server import MCPServer
import mysql.connector
import os
from datetime import datetime, timedelta, timezone

DEFAULT_LISTENING_PORT: int = 8080
DEFAULT_LISTENING_INTF: str = '0.0.0.0'
DEFAULT_TRANSPORT: str = 'http'

mcp = MCPServer('stopandshop-moderation', 'A moderation server for Stop and Shop')

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "stopandshop"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

@mcp.tool(
    name="get_comments_since",
    description="Retrieve comments posted after a given date with brand and belief context",
    input_schema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "default": 50
            }
        },
        "required": []
    },
    #output_schema={
    #    "type": "object",
    #    "properties": {
    #        "comments": {
    #        "type": "array",
    #        "items": {
    #            "type": "object",
    #            "properties": {
    #                "comment_id": {"type": "integer"},
    #                "text": {"type": "string"},
    #                "note": {"type": "integer"},
    #                "created_at": {"type": "string"},
    #                "upvote_count": {"type": "integer"},
    #                "downvote_count": {"type": "integer"},
    #                "is_anonymous": {"type": "boolean"},
    #                "brand_name": {"type": "string"},
    #                "belief_title": {"type": "string"},
    #                "belief_description": {"type": "string"}
    #            }
    #        }
    #    }
    #}}
)
def get_comments_since(limit: int = 50):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            c.comment_id,
            c.text,
            c.note,
            b.name AS brand_name,
            bl.title AS belief_title,
            bl.description AS belief_description

        FROM comment c
        JOIN brand b ON c.concerned_brand_id = b.brand_id
        JOIN belief bl ON c.concerned_belief_id = bl.belief_id

        WHERE c.is_moderation_pertinent IS NULL

        ORDER BY c.created_at ASC
        LIMIT %s
    """

    cursor.execute(query, (limit,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return { "comments": results }


@mcp.tool(
    name="mark_comments_not_pertinent",
    description="Mark multiple comments as not pertinent after LLM classification",
    input_schema={
        "type": "object",
        "properties": {
            "comment_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of comment IDs to mark as not pertinent"
            }
        },
        "required": ["comment_ids"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "updated_count": {
                "type": "integer"
            },
            "updated_ids": {
                "type": "array",
                "items": {"type": "integer"}
            }
        }
    }
)
def mark_comments_not_pertinent(comment_ids: list[int], reason: str = None):
    conn = get_conn()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(comment_ids))

    query = f"""
        UPDATE comment
        SET is_moderation_pertinent = FALSE
        WHERE comment_id IN ({placeholders})
    """

    cursor.execute(query, comment_ids)
    conn.commit()

    updated_count = cursor.rowcount

    cursor.close()
    conn.close()

    return {
        "updated_count": updated_count,
        "updated_ids": comment_ids
    }


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
