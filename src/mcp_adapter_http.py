import http.server
import json
import os
import ssl
import socket
from http.server import HTTPServer
from typing import Any, Optional
from mcp_transport_adapter import MCPTransportAdapter
from mcp_server import MCPServer


class MCPHttpRequestHandler(http.server.BaseHTTPRequestHandler):

    server_impl: MCPServer = None
    timeout = 5.0  # Timeout in seconds for reading request body

    """
    https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#sending-messages-to-the-server
    """
    def do_POST(self):
        # Read body - try Content-Length first, then read all available data
        content_length = self.headers.get("Content-Length")
        
        try:
            if content_length:
                content_length = int(content_length)
                body = self.rfile.read(content_length).decode("utf-8")
            else:
                # No Content-Length header - this should not happen with proper clients
                # Read all available data
                body = self.rfile.read().decode("utf-8")
            
            # Log the received body for debugging
            print(f"DEBUG: Received POST request, Content-Length: {content_length}, Body: {body[:500]}")
            
            # Handle empty body
            if not body or not body.strip():
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Empty request body"}).encode("utf-8"))
                return
            
            try:
                request_payload = json.loads(body)
            except json.JSONDecodeError as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON: {str(e)}"}).encode("utf-8"))
                return
            
            response_payload = self.server_impl.handle_request(request_payload)
            response_body = json.dumps(response_payload).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            
        except ValueError as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Invalid Content-Length: {str(e)}"}).encode("utf-8"))
        except Exception as e:
            import traceback
            print(f"ERROR in do_POST: {e}")
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Internal server error: {str(e)}"}).encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        return


class MCPHttpAdapter(MCPTransportAdapter):

    def __init__(self, server_impl: MCPServer, listening_intf: str = "localhost", listening_port: int = 8080, use_https: bool = False, certfile: Optional[str] = None, keyfile: Optional[str] = None) -> None:
        self.server_impl = server_impl
        self.listening_intf = listening_intf
        self.listening_port = listening_port
        self.use_https = use_https or os.getenv("TRANSPORT", "http").lower() == "https"
        
        # Détecter le répertoire racine du projet
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Chemins par défaut relatifs à la racine du projet
        default_cert = os.path.join(project_root, "certs", "server.crt")
        default_key = os.path.join(project_root, "certs", "server.key")
        
        self.certfile = certfile or os.getenv("SSL_CERTFILE", default_cert)
        self.keyfile = keyfile or os.getenv("SSL_KEYFILE", default_key)
        
        # Si les chemins par défaut n'existent pas, essayer les anciens noms
        if not os.path.exists(self.certfile):
            self.certfile = os.path.join(project_root, "cert.pem")
        if not os.path.exists(self.keyfile):
            self.keyfile = os.path.join(project_root, "key.pem")

    def serve(self) -> None:
        MCPHttpRequestHandler.server_impl = self.server_impl
        
        if self.use_https:
            # Vérifier que les fichiers de certificats existent
            if not os.path.exists(self.certfile):
                raise FileNotFoundError(f"SSL certificate file not found: {self.certfile}. Please generate certificates with: bash certs/generate_certs.sh")
            if not os.path.exists(self.keyfile):
                raise FileNotFoundError(f"SSL key file not found: {self.keyfile}. Please generate certificates with: bash certs/generate_certs.sh")
            
            # Use HTTPS with SSL
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            httpd = HTTPServer((self.listening_intf, self.listening_port), MCPHttpRequestHandler)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            protocol = "HTTPS"
        else:
            httpd = HTTPServer((self.listening_intf, self.listening_port), MCPHttpRequestHandler)
            protocol = "HTTP"
        
        print(f"MCP {protocol} Adapter listening on {self.listening_intf}:{self.listening_port}")
        if self.use_https:
            print(f"  SSL cert: {self.certfile}")
            print(f"  SSL key:  {self.keyfile}")
        httpd.serve_forever()
