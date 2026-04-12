import json
import sys
from mcp_transport_adapter import MCPTransportAdapter


class MCPStdioAdapter(MCPTransportAdapter):

    def __init__(self, server_impl) -> None:
        self.server_impl = server_impl

    def serve(self) -> None:
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue

            try:
                request_payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            response_payload = self.server_impl.handle_request(request_payload)
            sys.stdout.write(json.dumps(response_payload))
            sys.stdout.write("\n")
            sys.stdout.flush()
