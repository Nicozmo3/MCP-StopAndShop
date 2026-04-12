import http.server
import json
from http.server import HTTPServer
from typing import Any
from mcp_transport_adapter import MCPTransportAdapter
from mcp_server import MCPServer


class MCPHttpRequestHandler(http.server.BaseHTTPRequestHandler):

    server_impl: MCPServer = None

    """
    https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#sending-messages-to-the-server
    """
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        request_payload = json.loads(body)
        response_payload = self.server_impl.handle_request(request_payload)
        response_body = json.dumps(response_payload).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format: str, *args: object) -> None:
        return


class MCPHttpAdapter(MCPTransportAdapter):

    def __init__(self, server_impl: MCPServer, listening_intf: str = "localhost", listening_port: int = 8080) -> None:
        self.server_impl = server_impl
        self.listening_intf = listening_intf
        self.listening_port = listening_port

    def serve(self) -> None:
        MCPHttpRequestHandler.server_impl = self.server_impl
        httpd = HTTPServer((self.listening_intf, self.listening_port), MCPHttpRequestHandler)
        httpd.serve_forever()
