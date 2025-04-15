"""
Tests for the bridge protocol module.

This module tests the JSON protocol definitions and helpers used for
communication between the Python backend and the VS Code extension.
"""

import json
import unittest
import pytest

from bridge.protocol import (
    CommandType, QueryType, ResponseStatus,
    Command, UpdateFileCommand, RemoveFileCommand, QueryGraphCommand,
    GetStatsCommand, PingCommand, Response, ErrorResponse, 
    UpdateFileResponse, RemoveFileResponse, QueryGraphResponse,
    GetStatsResponse, PingResponse, parse_command, create_error_response
)


class TestProtocolModels:
    """Test cases for the protocol models."""
    
    def test_command_serialization(self):
        """Test serializing a Command to JSON (expected use case)."""
        # Create a basic command
        cmd = Command(id="test-id", command=CommandType.PING)
        
        # Serialize to JSON
        json_str = cmd.json()
        data = json.loads(json_str)
        
        # Check serialized data
        assert data["id"] == "test-id"
        assert data["command"] == "ping"
        assert data["version"] == "1.0.0"
    
    def test_update_file_command(self):
        """Test creating and serializing an UpdateFileCommand (expected use case)."""
        # Create update file command
        cmd = UpdateFileCommand(
            id="cmd-1",
            file_path="/path/to/file.py",
            content="def hello():\n    pass\n"
        )
        
        # Serialize and deserialize
        json_str = cmd.json()
        data = json.loads(json_str)
        
        # Check fields
        assert data["id"] == "cmd-1"
        assert data["command"] == "update_file"
        assert data["file_path"] == "/path/to/file.py"
        assert data["content"] == "def hello():\n    pass\n"
    
    def test_response_serialization(self):
        """Test serializing a Response to JSON (expected use case)."""
        # Create a basic response
        resp = Response(id="test-id", status=ResponseStatus.SUCCESS)
        
        # Serialize to JSON
        json_str = resp.json()
        data = json.loads(json_str)
        
        # Check serialized data
        assert data["id"] == "test-id"
        assert data["status"] == "success"
        assert data["version"] == "1.0.0"
    
    def test_error_response(self):
        """Test creating and serializing an ErrorResponse (expected use case)."""
        # Create error response
        resp = ErrorResponse(
            id="cmd-1",
            error_message="Something went wrong",
            error_code=500
        )
        
        # Serialize and deserialize
        json_str = resp.json()
        data = json.loads(json_str)
        
        # Check fields
        assert data["id"] == "cmd-1"
        assert data["status"] == "error"
        assert data["error_message"] == "Something went wrong"
        assert data["error_code"] == 500
    
    def test_parse_command_update_file(self):
        """Test parsing an UpdateFileCommand from JSON (expected use case)."""
        # Create JSON string for an UpdateFileCommand
        json_str = json.dumps({
            "id": "cmd-1",
            "command": "update_file",
            "file_path": "/path/to/file.py",
            "content": "def hello():\n    pass\n"
        })
        
        # Parse command
        cmd = parse_command(json_str)
        
        # Check type and fields
        assert isinstance(cmd, UpdateFileCommand)
        assert cmd.id == "cmd-1"
        assert cmd.file_path == "/path/to/file.py"
        assert cmd.content == "def hello():\n    pass\n"
    
    def test_parse_command_remove_file(self):
        """Test parsing a RemoveFileCommand from JSON (expected use case)."""
        # Create JSON string for a RemoveFileCommand
        json_str = json.dumps({
            "id": "cmd-2",
            "command": "remove_file",
            "file_path": "/path/to/file.py"
        })
        
        # Parse command
        cmd = parse_command(json_str)
        
        # Check type and fields
        assert isinstance(cmd, RemoveFileCommand)
        assert cmd.id == "cmd-2"
        assert cmd.file_path == "/path/to/file.py"
    
    def test_parse_command_query_graph(self):
        """Test parsing a QueryGraphCommand from JSON (expected use case)."""
        # Create JSON string for a QueryGraphCommand
        json_str = json.dumps({
            "id": "cmd-3",
            "command": "query_graph",
            "query_type": "find_definition",
            "query_params": {"name": "hello", "file_path": "/path/to/file.py"},
            "limit": 10
        })
        
        # Parse command
        cmd = parse_command(json_str)
        
        # Check type and fields
        assert isinstance(cmd, QueryGraphCommand)
        assert cmd.id == "cmd-3"
        assert cmd.query_type == QueryType.FIND_DEFINITION
        assert cmd.query_params == {"name": "hello", "file_path": "/path/to/file.py"}
        assert cmd.limit == 10
    
    def test_parse_command_get_stats(self):
        """Test parsing a GetStatsCommand from JSON (expected use case)."""
        # Create JSON string for a GetStatsCommand
        json_str = json.dumps({
            "id": "cmd-4",
            "command": "get_stats",
            "detailed": True
        })
        
        # Parse command
        cmd = parse_command(json_str)
        
        # Check type and fields
        assert isinstance(cmd, GetStatsCommand)
        assert cmd.id == "cmd-4"
        assert cmd.detailed is True
    
    def test_parse_command_ping(self):
        """Test parsing a PingCommand from JSON (expected use case)."""
        # Create JSON string for a PingCommand
        json_str = json.dumps({
            "id": "cmd-5",
            "command": "ping"
        })
        
        # Parse command
        cmd = parse_command(json_str)
        
        # Check type and fields
        assert isinstance(cmd, PingCommand)
        assert cmd.id == "cmd-5"
    
    def test_parse_command_invalid_json(self):
        """Test parsing invalid JSON (failure case)."""
        # Create invalid JSON string
        json_str = "not a valid json"
        
        # Parse command should return None
        cmd = parse_command(json_str)
        assert cmd is None
    
    def test_parse_command_missing_command_type(self):
        """Test parsing JSON with missing command type (edge case)."""
        # Create JSON string with missing command field
        json_str = json.dumps({
            "id": "cmd-6"
        })
        
        # Parse command should return None
        cmd = parse_command(json_str)
        assert cmd is None
    
    def test_parse_command_unknown_type(self):
        """Test parsing JSON with unknown command type (edge case)."""
        # Create JSON string with unknown command type
        json_str = json.dumps({
            "id": "cmd-7",
            "command": "unknown_command"
        })
        
        # Parse command should return None
        cmd = parse_command(json_str)
        assert cmd is None
    
    def test_create_error_response(self):
        """Test creating an error response (expected use case)."""
        # Create error response using helper function
        json_str = create_error_response("cmd-8", "Something went wrong", 500)
        
        # Parse response
        data = json.loads(json_str)
        
        # Check fields
        assert data["id"] == "cmd-8"
        assert data["status"] == "error"
        assert data["error_message"] == "Something went wrong"
        assert data["error_code"] == 500
    
    def test_response_inheritance(self):
        """Test response inheritance and polymorphism (edge case)."""
        # Create different response types with same id
        responses = [
            UpdateFileResponse(id="test-id", nodes_added=5, edges_added=10, parsing_time_ms=15.5),
            RemoveFileResponse(id="test-id", nodes_removed=3),
            QueryGraphResponse(id="test-id", results=[{"name": "test"}], query_time_ms=5.2),
            GetStatsResponse(id="test-id", stats={"nodes": 10}),
            PingResponse(id="test-id"),
            ErrorResponse(id="test-id", error_message="Error")
        ]
        
        # All should be instances of Response
        for resp in responses:
            assert isinstance(resp, Response)
            assert resp.id == "test-id"
        
        # Success responses should have status=success
        for resp in responses[:-1]:  # All except the error response
            assert resp.status == ResponseStatus.SUCCESS
        
        # Error response should have status=error
        assert responses[-1].status == ResponseStatus.ERROR
