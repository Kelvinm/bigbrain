"""
Graph builder module for constructing knowledge graph from parsed code data.

This module converts parsed code structures from the parser module into nodes and edges
in the graph store, building a connected knowledge graph of code entities and relationships.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union

from core.parser import CodeParser
from core.graph_store import GraphStore

# Configure logging
logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Builds and updates the code knowledge graph from parsed code structures.
    
    The GraphBuilder acts as an intermediary between the CodeParser and GraphStore,
    converting parsed code structures into graph nodes and relationships, and handling
    updates when files change.
    """
    
    def __init__(self, graph_store: GraphStore):
        """
        Initialize the graph builder with a graph store.
        
        Args:
            graph_store: The graph store to populate with code structures.
        """
        self.graph_store = graph_store
        self.parser = CodeParser()
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a file and update the graph with its structures.
        
        This method parses the file, converts the parsed structures to graph
        elements, and updates the graph store.
        
        Args:
            file_path: Path to the file to process.
            
        Returns:
            bool: True if successful, False otherwise.
            
        Raises:
            ValueError: If the file is invalid or unsupported.
            IOError: If the file cannot be read.
        """
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if not file_path.is_file():
                raise ValueError(f"Not a file: {file_path}")
                
            # Parse the file
            logger.debug(f"Parsing file: {file_path}")
            parsed_data = self.parser.parse_file(file_path)
            
            # Remove existing nodes for this file before adding new ones
            # This ensures updates are clean
            self.graph_store.remove_file_nodes(str(file_path))
            
            # Build graph from parsed data
            self._build_graph_from_parsed_data(parsed_data)
            
            # Save the updated graph
            self.graph_store.save_graph()
            
            logger.info(f"Successfully processed file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            # Re-raise to be handled by the caller
            raise
    
    def _build_graph_from_parsed_data(self, parsed_data: Dict[str, Any]) -> None:
        """
        Build graph nodes and edges from parsed file data.
        
        Args:
            parsed_data: Dictionary of parsed code structures from the parser.
        """
        file_path = parsed_data["file_path"]
        language = parsed_data["language"]
          # Create a file node
        file_node_id = f"file:{file_path}"
        file_attributes = {
            "type": "file",
            "name": Path(file_path).name,
            "language": language,
        }
        self.graph_store.add_node(
            node_id=file_node_id,
            attributes=file_attributes,
            file_path=file_path,
            language=language
        )
        
        # Process functions
        for func in parsed_data.get("functions", []):
            self._add_function_to_graph(func, file_path, file_node_id)
        
        # Process classes
        for cls in parsed_data.get("classes", []):
            self._add_class_to_graph(cls, file_path, file_node_id)
    
    def _add_function_to_graph(self, func: Dict[str, Any], file_path: str, 
                               file_node_id: str) -> None:
        """
        Add a function and its relationships to the graph.
        
        Args:
            func: Function data from the parser.
            file_path: Path to the source file.
            file_node_id: Node ID of the containing file.
        """
        func_name = func["name"]
        func_node_id = f"func:{file_path}:{func_name}"
          # Create function node
        func_attributes = {
            "type": "function",
            "name": func_name,
            "line": func.get("line"),
            "end_line": func.get("end_line"),
            "docstring": func.get("docstring")
        }
        self.graph_store.add_node(
            node_id=func_node_id,
            attributes=func_attributes, 
            file_path=file_path
        )
        
        # Add relationship from file to function
        self.graph_store.add_edge(file_node_id, func_node_id, "contains")
    
    def _add_class_to_graph(self, cls: Dict[str, Any], file_path: str, 
                            file_node_id: str) -> None:
        """
        Add a class and its relationships to the graph.
        
        Args:
            cls: Class data from the parser.
            file_path: Path to the source file.
            file_node_id: Node ID of the containing file.
        """
        class_name = cls["name"]
        class_node_id = f"class:{file_path}:{class_name}"
          # Create class node
        class_attributes = {
            "type": "class",
            "name": class_name,
            "line": cls.get("line"),
            "end_line": cls.get("end_line"),
            "docstring": cls.get("docstring")
        }
        self.graph_store.add_node(
            node_id=class_node_id,
            attributes=class_attributes,
            file_path=file_path
        )
        
        # Add relationship from file to class
        self.graph_store.add_edge(file_node_id, class_node_id, "contains")
        
        # Process class methods if available
        for method in cls.get("methods", []):
            method_name = method["name"]
            method_node_id = f"method:{file_path}:{class_name}.{method_name}"
              # Create method node
            method_attributes = {
                "type": "method",
                "name": method_name,
                "class_name": class_name,
                "line": method.get("line"),
                "end_line": method.get("end_line"),
                "docstring": method.get("docstring")
            }
            self.graph_store.add_node(
                node_id=method_node_id,
                attributes=method_attributes,
                file_path=file_path
            )
            
            # Add relationships
            self.graph_store.add_edge(class_node_id, method_node_id, "contains")


# For testing/development
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) > 1:
        graph_store = GraphStore()
        builder = GraphBuilder(graph_store)
        
        test_file = Path(sys.argv[1])
        try:
            success = builder.process_file(test_file)
            if success:
                print(f"Successfully processed file: {test_file}")
                print(f"Graph stats: {graph_store.get_graph_stats()}")
            else:
                print(f"Failed to process file: {test_file}")
        except Exception as e:
            print(f"Error processing file {test_file}: {str(e)}")
    else:
        print("Usage: python graph_builder.py <file_path>")
