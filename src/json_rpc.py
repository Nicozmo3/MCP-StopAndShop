from typing import Union, Optional

FIELD_JSONRPC = "jsonrpc"
FIELD_ID = "id"
FIELD_METHOD = "method"
FIELD_RESULT = "result"
FIELD_ERROR = "error"

EXPECTED_FIELD_JSONRPC_VALUE = "2.0"

def build_json_rpc_success_response(request_id: Union[int, str], result: dict):
    return {
        FIELD_JSONRPC: EXPECTED_FIELD_JSONRPC_VALUE,
        FIELD_ID: request_id,
        FIELD_RESULT: result
    }

def build_json_rpc_error_response(request_id: Union[int, str, None], code: int, message: str):
    return {
        FIELD_JSONRPC: EXPECTED_FIELD_JSONRPC_VALUE,
        FIELD_ID: request_id,
        FIELD_ERROR: {
            "code": code,
            "message": message
        }
    }

def validate_json_rpc_request(request: dict) -> bool:
    return all(field in request for field in (FIELD_JSONRPC, FIELD_ID, FIELD_METHOD)) and request[FIELD_JSONRPC] == EXPECTED_FIELD_JSONRPC_VALUE and request[FIELD_ID] is not None
