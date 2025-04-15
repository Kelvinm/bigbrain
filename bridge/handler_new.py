"""
Bridge handler for stdin/stdout communication.

This module handles the communication between the Python backend and the VS Code extension
via JSON messages over stdin/stdout.
"""

import sys
import json
import logging
import traceback
from typing import Dict, Any, Callable, Optional, Union, Type

from bridge.protocol import (
    Command, CommandType, UpdateFileCommand, RemoveFileCommand, 
    QueryGraphCommand, GetStatsCommand, PingCommand,
    Response, ErrorResponse, UpdateFileResponse, RemoveFileResponse,
    QueryGraphResponse, GetStatsResponse, PingResponse,
    parse_command, create_error_response
)
from core.parser import CodeParser
from core.graph_builder import GraphBuilder
from core.graph_store import GraphStore
from config import DEFAULT_COMMAND_TIMEOUT

# Configure logging
logger = logging.getLogger(__name__)


class BridgeHandler:
    """
    Handler for stdin/stdout bridge communication.
    
    Processes incoming JSON commands from stdin and sends responses via stdout.
    """
    
    def __init__(
        self, 
        graph_builder: GraphBuilder,
        parser: CodeParser,
        graph_store: GraphStore
    ):
        """
        Initialize the bridge handler with required components.
        
        Args:
            graph_builder (GraphBuilder): Graph builder instance.
            parser (CodeParser): Code parser instance.
            graph_store (GraphStore): Graph store instance.
        """
        self.graph_builder = graph_builder
        self.parser = parser
        self.graph_store = graph_store
        self.command_handlers: Dict[CommandType, Callable] = {
            CommandType.UPDATE_FILE: self._handle_update_file,
            CommandType.REMOVE_FILE: self._handle_remove_file,
            CommandType.QUERY_GRAPH: self._handle_query_graph,
            CommandType.GET_STATS: self._handle_get_stats,
            CommandType.PING: self._handle_ping,
        }
    
    def process_input(self, input_json: str) -> Optional[str]:
        """
        Process an input JSON command and return a response.
        
        Args:
            input_json (str): JSON string command.
            
        Returns:
            Optional[str]: JSON response string, or None if invalid input.
        """
        try:
            command = parse_command(input_json)
            
            if command is None:
                return create_error_response(
                    "unknown", "Invalid command format"
                )
            
            handler = self.command_handlers.get(command.command)
            
            if handler is None:
                return create_error_response(
                    command.id, f"Unsupported command: {command.command}"
                )
            
            response = handler(command)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            logger.debug(traceback.format_exc())
            return create_error_response(
                "unknown", f"Error processing command: {str(e)}"
            )
    
    def _handle_update_file(self, command: UpdateFileCommand) -> Response:
        """
        Handle an update_file command.
        
        Args:
            command (UpdateFileCommand): Command to process.
            
        Returns:
            Response: Command response.
        """
        try:
            file_path = command.file_path
            content = command.content
            language = command.language
            
            # Process the file update through parser and graph builder
            result = self.graph_builder.update_file(file_path, content, language)
            
            return UpdateFileResponse(
                id=command.id,
                nodes_added=result.get("nodes_added", 0),
                edges_added=result.get("edges_added", 0),
                parsing_time_ms=result.get("parsing_time_ms", 0.0)
            )
        except Exception as e:
            logger.error(f"Error updating file {command.file_path}: {e}")
            logger.debug(traceback.format_exc())
            return ErrorResponse(
                id=command.id,
                error_message=f"Failed to update file: {str(e)}"
            )
    
    def _handle_remove_file(self, command: RemoveFileCommand) -> Response:
        """
        Handle a remove_file command.
        
        Args:
            command (RemoveFileCommand): Command to process.
            
        Returns:
            Response: Command response.
        """
        try:
            file_path = command.file_path
            nodes_removed = self.graph_store.remove_file_nodes(file_path)
            
            return RemoveFileResponse(
                id=command.id,
                nodes_removed=nodes_removed
            )
        except Exception as e:
            logger.error(f"Error removing file {command.file_path}: {e}")
            return ErrorResponse(
                id=command.id,
                error_message=f"Failed to remove file: {str(e)}"
            )
    
    def _handle_query_graph(self, command: QueryGraphCommand) -> Response:
        """
        Handle a query_graph command.
        
        Args:
            command (QueryGraphCommand): Command to process.
            
        Returns:
            Response: Command response.
        """
        # NOTE: In Phase 3, this will be implemented with the QueryEngine
        # For now, return an error since query engine is not implemented yet
        return ErrorResponse(
            id=command.id,
            error_message="Query engine not implemented yet (planned for Phase 3)"
        )
    
    def _handle_get_stats(self, command: GetStatsCommand) -> Response:
        """
        Handle a get_stats command.
        
        Args:
            command (GetStatsCommand): Command to process.
            
        Returns:
            Response: Command response.
        """
        try:
            stats = self.graph_store.get_stats()
            return GetStatsResponse(
                id=command.id,
                stats=stats
            )
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return ErrorResponse(
                id=command.id,
                error_message=f"Failed to get stats: {str(e)}"
            )
    
    def _handle_ping(self, command: PingCommand) -> Response:
        """
        Handle a ping command.
        
        Args:
            command (PingCommand): Command to process.
            
        Returns:
            Response: Command response.
        """
        return PingResponse(id=command.id)
    
    def listen(self) -> None:
        """
        Start listening for commands on stdin.
        This method blocks indefinitely.
        """
        logger.info("Bridge handler is listening for commands on stdin")
        
        while True:
            try:
                # Read a line from stdin
                line = sys.stdin.readline()
                
                # Empty line means stdin has been closed
                if not line:
                    logger.info("Stdin closed, exiting...")
                    break
                
                # Process the command and send response to stdout
                response = self.process_input(line.strip())
                if response:
                    print(response, flush=True)
                    
            except KeyboardInterrupt:
                logger.info("Interrupted, exiting...")
                break
            except Exception as e:
                logger.error(f"Error in bridge handler: {e}")
                logger.debug(traceback.format_exc())
                error_response = create_error_response(
                    "unknown", f"Internal error: {str(e)}"
                )
                print(error_response, flush=True)
