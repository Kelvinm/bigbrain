"""
Tests for the bridge handler module.

This module tests the BridgeHandler class which processes JSON commands
from stdin and returns responses via stdout.
"""

import json
from unittest import mock
import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path to ensure imports work correctly
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import directly from the absolute module path
from bridge.protocol import (
    CommandType, UpdateFileCommand, RemoveFileCommand, 
    QueryGraphCommand, GetStatsCommand, PingCommand,
    ResponseStatus
)

# Import the handler module directly to avoid import issues
import bridge.handler
# Get the BridgeHandler class from the module
BridgeHandler = bridge.handler.BridgeHandler


class TestBridgeHandler:
    """Test cases for the BridgeHandler class."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        # Create mocks for dependencies
        self.mock_parser = mock.MagicMock()
        self.mock_graph_store = mock.MagicMock()
        self.mock_graph_builder = mock.MagicMock()
        
        # Initialize handler with mocks
        self.handler = BridgeHandler(
            self.mock_graph_builder,
            self.mock_parser,
            self.mock_graph_store
        )
    
    def test_process_update_file_command(self):
        """Test processing an update_file command (expected use case)."""
        # Create an update_file command JSON
        command_json = json.dumps({
            "id": "cmd-1",
            "command": "update_file",
            "file_path": "/path/to/file.py",
            "content": "def hello():\n    pass\n"
        })
        
        # Mock the graph builder's update_file method to return a result
        self.mock_graph_builder.update_file.return_value = {
            "nodes_added": 5,
            "edges_added": 10,
            "parsing_time_ms": 15.5
        }
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the graph builder was called with correct arguments
        self.mock_graph_builder.update_file.assert_called_once_with(
            "/path/to/file.py",
            "def hello():\n    pass\n",
            None
        )
        
        # Verify the response
        assert response["id"] == "cmd-1"
        assert response["status"] == "success"
        assert response["nodes_added"] == 5
        assert response["edges_added"] == 10
        assert response["parsing_time_ms"] == 15.5
    
    def test_process_remove_file_command(self):
        """Test processing a remove_file command (expected use case)."""
        # Create a remove_file command JSON
        command_json = json.dumps({
            "id": "cmd-2",
            "command": "remove_file",
            "file_path": "/path/to/file.py"
        })
        
        # Mock the graph store's remove_file_nodes method to return a count
        self.mock_graph_store.remove_file_nodes.return_value = 3
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the graph store was called with correct arguments
        self.mock_graph_store.remove_file_nodes.assert_called_once_with("/path/to/file.py")
        
        # Verify the response
        assert response["id"] == "cmd-2"
        assert response["status"] == "success"
        assert response["nodes_removed"] == 3
    
    def test_process_get_stats_command(self):
        """Test processing a get_stats command (expected use case)."""
        # Create a get_stats command JSON
        command_json = json.dumps({
            "id": "cmd-3",
            "command": "get_stats",
            "detailed": True
        })
        
        # Mock the graph store's get_stats method to return stats
        self.mock_graph_store.get_stats.return_value = {
            "nodes": 10,
            "edges": 15,
            "files": 2,
            "edge_types": {"CONTAINS": 8, "CALLS": 7}
        }
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the graph store was called
        self.mock_graph_store.get_stats.assert_called_once()
        
        # Verify the response
        assert response["id"] == "cmd-3"
        assert response["status"] == "success"
        assert response["stats"]["nodes"] == 10
        assert response["stats"]["edges"] == 15
        assert response["stats"]["files"] == 2
        assert response["stats"]["edge_types"]["CONTAINS"] == 8
        assert response["stats"]["edge_types"]["CALLS"] == 7
    
    def test_process_ping_command(self):
        """Test processing a ping command (expected use case)."""
        # Create a ping command JSON
        command_json = json.dumps({
            "id": "cmd-4",
            "command": "ping"
        })
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the response
        assert response["id"] == "cmd-4"
        assert response["status"] == "success"
    
    def test_process_query_graph_command(self):
        """Test processing a query_graph command (expected use case - currently unimplemented)."""
        # Create a query_graph command JSON
        command_json = json.dumps({
            "id": "cmd-5",
            "command": "query_graph",
            "query_type": "find_definition",
            "query_params": {"name": "hello", "file_path": "/path/to/file.py"}
        })
        
        # Process the command - should return error since query engine is not implemented yet
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the response is an error since query engine is not implemented yet
        assert response["id"] == "cmd-5"
        assert response["status"] == "error"
        assert "not implemented yet" in response["error_message"]
    
    def test_process_invalid_command_json(self):
        """Test processing invalid JSON (failure case)."""
        # Create invalid JSON
        command_json = "not valid json"
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the response is an error
        assert response["status"] == "error"
        assert "Invalid command format" in response["error_message"]
    
    def test_process_unsupported_command(self):
        """Test processing an unsupported command type (edge case)."""
        # Create a command with unsupported type
        command_json = json.dumps({
            "id": "cmd-6",
            "command": "unsupported_command"
        })
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the response is an error
        assert response["id"] == "cmd-6"
        assert response["status"] == "error"
        assert "Unsupported command" in response["error_message"]
    
    def test_error_in_command_processing(self):
        """Test error handling during command processing (failure case)."""
        # Create an update_file command JSON
        command_json = json.dumps({
            "id": "cmd-7",
            "command": "update_file",
            "file_path": "/path/to/file.py",
            "content": "def hello():\n    pass\n"
        })
        
        # Make the graph builder raise an exception
        self.mock_graph_builder.update_file.side_effect = Exception("Test error")
        
        # Process the command
        response_json = self.handler.process_input(command_json)
        response = json.loads(response_json)
        
        # Verify the response is an error
        assert response["id"] == "cmd-7"
        assert response["status"] == "error"
        assert "Failed to update file" in response["error_message"]
    
    @mock.patch('sys.stdin')
    @mock.patch('builtins.print')
    def test_listen_method(self, mock_print, mock_stdin):
        """Test the listen method processing stdin commands (expected use case)."""
        # Set up mock stdin to return two commands then empty line to stop loop
        mock_stdin.readline.side_effect = [
            '{"id": "cmd-8", "command": "ping"}\n',
            '{"id": "cmd-9", "command": "get_stats"}\n',
            ''
        ]
        
        # Mock get_stats for second command
        self.mock_graph_store.get_stats.return_value = {"nodes": 5}
        
        # Call listen method - should process both commands then exit on empty line
        self.handler.listen()
        
        # Verify print was called twice with responses
        assert mock_print.call_count == 2
        
        # First call should be a ping response
        first_call_args = mock_print.call_args_list[0][0][0]
        first_response = json.loads(first_call_args)
        assert first_response["id"] == "cmd-8"
        assert first_response["status"] == "success"
        
        # Second call should be a get_stats response
        second_call_args = mock_print.call_args_list[1][0][0]
        second_response = json.loads(second_call_args)
        assert second_response["id"] == "cmd-9"
        assert second_response["status"] == "success"
        assert second_response["stats"] == {"nodes": 5}
    
    @mock.patch('sys.stdin')
    @mock.patch('builtins.print')
    def test_listen_with_exception(self, mock_print, mock_stdin):
        """Test the listen method handling errors (failure case)."""
        # Set up mock stdin to return an invalid command
        mock_stdin.readline.side_effect = [
            'invalid json\n',
            ''
        ]
        
        # Call listen method
        self.handler.listen()
        
        # Verify print was called once with error response
        mock_print.assert_called_once()
        response_str = mock_print.call_args[0][0]
        response = json.loads(response_str)
        assert response["status"] == "error"
        assert "Invalid command format" in response["error_message"]
