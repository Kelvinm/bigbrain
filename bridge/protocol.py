"""
Protocol definition for bridge communication.

This module defines the JSON protocol structure for communication between
the backend and the VS Code extension via stdin/stdout.
"""

import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class CommandType(str, Enum):
    """Command types for the JSON protocol."""
    UPDATE_FILE = "update_file"
    REMOVE_FILE = "remove_file"
    QUERY_GRAPH = "query_graph"
    GET_STATS = "get_stats"
    PING = "ping"


class QueryType(str, Enum):
    """Types of graph queries supported."""
    FIND_DEFINITION = "find_definition"
    FIND_REFERENCES = "find_references"
    FIND_CALLERS = "find_callers"
    FIND_CALLEES = "find_callees"
    FIND_IMPLEMENTATIONS = "find_implementations"
    GET_DOCUMENTATION = "get_documentation"
    GET_FILE_SYMBOLS = "get_file_symbols"


class Command(BaseModel):
    """Base model for all commands."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    command: CommandType
    version: str = "1.0.0"


class UpdateFileCommand(Command):
    """Command to update a file in the graph."""
    command: CommandType = CommandType.UPDATE_FILE
    file_path: str
    content: str
    language: Optional[str] = None  # If None, inferred from extension


class RemoveFileCommand(Command):
    """Command to remove a file from the graph."""
    command: CommandType = CommandType.REMOVE_FILE
    file_path: str


class QueryGraphCommand(Command):
    """Command to query the graph."""
    command: CommandType = CommandType.QUERY_GRAPH
    query_type: QueryType
    query_params: Dict[str, Any]
    limit: Optional[int] = 50


class GetStatsCommand(Command):
    """Command to get graph statistics."""
    command: CommandType = CommandType.GET_STATS
    detailed: bool = False


class PingCommand(Command):
    """Command to check if the bridge is alive."""
    command: CommandType = CommandType.PING


class ResponseStatus(str, Enum):
    """Status of the response."""
    SUCCESS = "success"
    ERROR = "error"


class Response(BaseModel):
    """Base model for all responses."""
    id: str  # Should match the command ID
    status: ResponseStatus
    version: str = "1.0.0"


class ErrorResponse(Response):
    """Error response."""
    status: ResponseStatus = ResponseStatus.ERROR
    error_message: str
    error_code: Optional[int] = None


class UpdateFileResponse(Response):
    """Response to an update file command."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    nodes_added: int
    edges_added: int
    parsing_time_ms: float


class RemoveFileResponse(Response):
    """Response to a remove file command."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    nodes_removed: int


class QueryGraphResponse(Response):
    """Response to a graph query command."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    results: List[Dict[str, Any]]
    query_time_ms: float


class GetStatsResponse(Response):
    """Response to a get stats command."""
    status: ResponseStatus = ResponseStatus.SUCCESS
    stats: Dict[str, Any]


class PingResponse(Response):
    """Response to a ping command."""
    status: ResponseStatus = ResponseStatus.SUCCESS


def parse_command(json_str: str) -> Union[Command, None]:
    """
    Parse a JSON string into a Command object.
    
    Args:
        json_str (str): JSON string to parse
        
    Returns:
        Command or None: Parsed command or None if parsing failed
    """
    try:
        data = json.loads(json_str)
        command_type = data.get("command")
        
        if not command_type:
            return None
            
        if command_type == CommandType.UPDATE_FILE:
            return UpdateFileCommand(**data)
        elif command_type == CommandType.REMOVE_FILE:
            return RemoveFileCommand(**data)
        elif command_type == CommandType.QUERY_GRAPH:
            return QueryGraphCommand(**data)
        elif command_type == CommandType.GET_STATS:
            return GetStatsCommand(**data)
        elif command_type == CommandType.PING:
            return PingCommand(**data)
        else:
            return None
    except Exception:
        return None


def create_error_response(command_id: str, message: str, code: Optional[int] = None) -> str:
    """
    Create an error response JSON string.
    
    Args:
        command_id (str): ID of the original command
        message (str): Error message
        code (int, optional): Error code
        
    Returns:
        str: JSON string for the error response
    """
    response = ErrorResponse(
        id=command_id,
        error_message=message,
        error_code=code
    )
    return response.json()
