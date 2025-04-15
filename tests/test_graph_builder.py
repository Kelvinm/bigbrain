"""
Tests for the graph_builder module.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import networkx as nx

from core.graph_builder import GraphBuilder
from core.graph_store import GraphStore
from core.parser import CodeParser


class TestGraphBuilder:
    """Test cases for the GraphBuilder class."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        # Use a mock graph store to avoid file operations
        with mock.patch('core.graph_store.GraphStore.load_graph'):
            self.graph_store = GraphStore()
            
            # Create a fresh graph for each test
            self.graph_store.graph = nx.DiGraph()
            self.graph_store.file_nodes = {}
            
            # Initialize the graph builder
            self.graph_builder = GraphBuilder(self.graph_store)
            
    def test_process_simple_python_file(self):
        """Test processing a simple Python file with a function and class."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(b"""
def test_function():
    \"\"\"Test function docstring.\"\"\"
    return True

class TestClass:
    \"\"\"Test class docstring.\"\"\"
    def method(self):
        return "test"
            """)
            
        try:
            file_path = Path(temp_file.name)
            
            # Process the file
            with mock.patch('core.graph_store.GraphStore.save_graph'):
                success = self.graph_builder.process_file(file_path)
            
            # Check processing was successful
            assert success is True
            
            # Check file node was created
            file_node_id = f"file:{temp_file.name}"
            assert self.graph_store.graph.has_node(file_node_id)
            
            # Check function node was created
            func_node_id = f"func:{temp_file.name}:test_function"
            assert self.graph_store.graph.has_node(func_node_id)
            
            # Check class node was created
            class_node_id = f"class:{temp_file.name}:TestClass"
            assert self.graph_store.graph.has_node(class_node_id)
            
            # Check relationships
            assert self.graph_store.graph.has_edge(file_node_id, func_node_id)
            assert self.graph_store.graph.has_edge(file_node_id, class_node_id)
            
            # Check node attributes
            func_node = self.graph_store.get_node_info(func_node_id)
            assert func_node["name"] == "test_function"
            assert func_node["type"] == "function"
            
            class_node = self.graph_store.get_node_info(class_node_id)
            assert class_node["name"] == "TestClass"
            assert class_node["type"] == "class"
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
    
    def test_process_empty_python_file(self):
        """Test processing an empty Python file (edge case)."""
        # Create a temporary empty Python file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(b"# Empty file\n")
            
        try:
            file_path = Path(temp_file.name)
            
            # Process the file
            with mock.patch('core.graph_store.GraphStore.save_graph'):
                success = self.graph_builder.process_file(file_path)
            
            # Check processing was successful even for empty files
            assert success is True
            
            # Check file node was created
            file_node_id = f"file:{temp_file.name}"
            assert self.graph_store.graph.has_node(file_node_id)
            
            # Check there are no other nodes except the file node
            assert len(self.graph_store.graph.nodes) == 1
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
    
    def test_process_nonexistent_file(self):
        """Test handling of non-existent files (failure case)."""
        file_path = Path("/nonexistent/file.py")
        
        # Process the file and expect an error
        with pytest.raises(FileNotFoundError):
            self.graph_builder.process_file(file_path)
            
    def test_process_update_existing_file(self):
        """Test updating an existing file in the graph."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(b"""
def original_function():
    pass
            """)
            
        try:
            file_path = Path(temp_file.name)
            
            # Process the file first time
            with mock.patch('core.graph_store.GraphStore.save_graph'):
                self.graph_builder.process_file(file_path)
            
            # Get the initial node count
            initial_node_count = len(self.graph_store.graph.nodes)
            
            # Update the file content
            with open(file_path, 'w') as f:
                f.write("""
def original_function():
    pass
    
def new_function():
    pass
                """)
                
            # Process the updated file
            with mock.patch('core.graph_store.GraphStore.save_graph'):
                self.graph_builder.process_file(file_path)
                
            # Check new nodes were added
            assert len(self.graph_store.graph.nodes) > initial_node_count
            
            # Check both functions exist
            func1_node_id = f"func:{temp_file.name}:original_function"
            func2_node_id = f"func:{temp_file.name}:new_function"
            
            assert self.graph_store.graph.has_node(func1_node_id)
            assert self.graph_store.graph.has_node(func2_node_id)
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
    
    def test_process_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as temp_file:
            temp_file.write(b"Some content")
            
        try:
            file_path = Path(temp_file.name)
            
            # Process the file and expect an error
            with pytest.raises(ValueError) as excinfo:
                self.graph_builder.process_file(file_path)
            
            assert "Unsupported file type" in str(excinfo.value)
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
