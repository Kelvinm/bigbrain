"""
Integration tests for the complete Python file parsing pipeline.

This module tests the end-to-end flow from parsing a Python file to building
the graph and verifying the resulting graph structure.
"""

import os
import tempfile
from pathlib import Path
import shutil
from unittest import mock

import pytest
import networkx as nx

from core.parser import CodeParser
from core.graph_builder import GraphBuilder
from core.graph_store import GraphStore


class TestParsingPipeline:
    """Integration tests for the complete parsing pipeline."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a temporary graph storage path
        self.graph_path = Path(self.temp_dir) / "test_graph.pickle"
        
        # Initialize the pipeline components with mocking for tree-sitter initialization
        with mock.patch('core.parser.CodeParser._load_languages'):
            self.parser = CodeParser()
            # Mock the languages dictionary
            self.parser.languages = {"python": mock.MagicMock()}
            
            # Initialize graph store with the temporary path
            with mock.patch('core.graph_store.GraphStore.load_graph'):
                self.graph_store = GraphStore(self.graph_path)
                # Create a fresh graph for each test
                self.graph_store.graph = nx.DiGraph()
                self.graph_store.file_nodes = {}
                
                # Initialize the graph builder
                self.graph_builder = GraphBuilder(self.graph_store)
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.temp_dir)
    
    def test_simple_python_file_pipeline(self):
        """Test the complete pipeline with a simple Python file."""
        # Create a test Python file
        test_file_path = Path(self.temp_dir) / "test_module.py"
        with open(test_file_path, 'w') as f:
            f.write("""
# A simple Python module
\"\"\"Module docstring.\"\"\"

def hello_world():
    \"\"\"Print a greeting message.
    
    Returns:
        str: A greeting message
    \"\"\"
    return "Hello, World!"

class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def __init__(self, initial_value=0):
        \"\"\"Initialize the calculator.
        
        Args:
            initial_value (int, optional): Starting value. Defaults to 0.
        \"\"\"
        self.value = initial_value
    
    def add(self, x):
        \"\"\"Add a number to the current value.
        
        Args:
            x (int): Number to add
            
        Returns:
            int: New value
        \"\"\"
        self.value += x
        return self.value
""")
        
        # Mock tree-sitter parsing with realistic results
        with mock.patch('tree_sitter.Parser.parse') as mock_parse, \
             mock.patch('core.parser.CodeParser._parse_python_with_tree_sitter') as mock_parse_python:
            
            # Set up mock to return realistic parse data
            mock_parse_python.return_value = {
                "functions": [
                    {
                        "name": "hello_world",
                        "line": 5,
                        "end_line": 11,
                        "docstring": "Print a greeting message.\n\nReturns:\n    str: A greeting message"
                    }
                ],
                "classes": [
                    {
                        "name": "Calculator",
                        "line": 13,
                        "end_line": 35,
                        "docstring": "A simple calculator class.",
                        "methods": [
                            {
                                "name": "__init__",
                                "line": 16,
                                "end_line": 22,
                                "docstring": "Initialize the calculator.\n\nArgs:\n    initial_value (int, optional): Starting value. Defaults to 0."
                            },
                            {
                                "name": "add",
                                "line": 24,
                                "end_line": 34,
                                "docstring": "Add a number to the current value.\n\nArgs:\n    x (int): Number to add\n    \nReturns:\n    int: New value"
                            }
                        ]
                    }
                ]
            }
            
            # Process the file with our graph builder
            with mock.patch('core.graph_store.GraphStore.save_graph'):
                success = self.graph_builder.process_file(test_file_path)
            
            # Verify the process was successful
            assert success is True
              # Verify file node was created
            file_node_id = f"file:{test_file_path}"
            assert self.graph_store.graph.has_node(file_node_id)
            file_node = self.graph_store.get_node(file_node_id)
            assert file_node["name"] == "test_module.py"
            assert file_node["language"] == "python"
            
            # Verify function node and relationships
            func_node_id = f"func:{test_file_path}:hello_world"
            assert self.graph_store.graph.has_node(func_node_id)
            assert self.graph_store.graph.has_edge(file_node_id, func_node_id)
            
            func_node = self.graph_store.get_node_info(func_node_id)
            assert func_node["name"] == "hello_world"
            assert "greeting message" in func_node["docstring"]
            
            # Verify class node and relationships
            class_node_id = f"class:{test_file_path}:Calculator"
            assert self.graph_store.graph.has_node(class_node_id)
            assert self.graph_store.graph.has_edge(file_node_id, class_node_id)
            
            class_node = self.graph_store.get_node_info(class_node_id)
            assert class_node["name"] == "Calculator"
            assert class_node["docstring"] == "A simple calculator class."
            
            # Check graph statistics
            stats = self.graph_store.get_graph_stats()
            assert stats["total_nodes"] > 0
            assert stats["total_edges"] > 0
            assert stats["indexed_files"] == 1
            assert "file" in stats["node_types"]
            assert "function" in stats["node_types"]
            assert "class" in stats["node_types"]
    
    def test_pipeline_with_multiple_files(self):
        """Test the pipeline with multiple Python files."""
        # Create two test Python files with inter-related code
        # File 1: module.py
        module_path = Path(self.temp_dir) / "module.py"
        with open(module_path, 'w') as f:
            f.write("""
\"\"\"A utility module.\"\"\"

def utility_function():
    \"\"\"A utility function.\"\"\"
    return "utility"
""")

        # File 2: main.py (which would import module.py)
        main_path = Path(self.temp_dir) / "main.py"
        with open(main_path, 'w') as f:
            f.write("""
\"\"\"Main module.\"\"\"

import module

def main():
    \"\"\"Main function.\"\"\"
    return module.utility_function()
""")
        
        # Mock parser results for module.py
        module_results = {
            "functions": [
                {
                    "name": "utility_function",
                    "line": 4,
                    "end_line": 6,
                    "docstring": "A utility function."
                }
            ],
            "classes": []
        }
        
        # Mock parser results for main.py
        main_results = {
            "functions": [
                {
                    "name": "main", 
                    "line": 6, 
                    "end_line": 8, 
                    "docstring": "Main function."
                }
            ],
            "classes": []
        }
        
        # Mock parser and process both files
        with mock.patch('core.parser.CodeParser._parse_python_with_tree_sitter') as mock_parse_python, \
             mock.patch('core.graph_store.GraphStore.save_graph'):
            
            # Process module.py
            mock_parse_python.return_value = module_results
            self.graph_builder.process_file(module_path)
            
            # Process main.py
            mock_parse_python.return_value = main_results
            self.graph_builder.process_file(main_path)
            
            # Verify both files were processed
            assert len(self.graph_store.file_nodes) == 2
            
            # Check main.py nodes
            main_file_node_id = f"file:{main_path}"
            main_func_node_id = f"func:{main_path}:main"
            assert self.graph_store.graph.has_node(main_file_node_id)
            assert self.graph_store.graph.has_node(main_func_node_id)
            
            # Check module.py nodes
            module_file_node_id = f"file:{module_path}"
            utility_func_node_id = f"func:{module_path}:utility_function"
            assert self.graph_store.graph.has_node(module_file_node_id)
            assert self.graph_store.graph.has_node(utility_func_node_id)
            
            # Check graph statistics
            stats = self.graph_store.get_graph_stats()
            assert stats["indexed_files"] == 2
            assert stats["node_types"]["function"] == 2
            assert stats["edge_types"]["contains"] > 0
    
    def test_pipeline_update_file(self):
        """Test updating a file in the pipeline."""
        # Create a test file
        test_file_path = Path(self.temp_dir) / "updatable.py"
        with open(test_file_path, 'w') as f:
            f.write("""
\"\"\"Initial module.\"\"\"

def initial_function():
    return "initial"
""")
        
        # Mock initial parse result
        initial_result = {
            "functions": [
                {
                    "name": "initial_function",
                    "line": 4,
                    "end_line": 5,
                    "docstring": None
                }
            ],
            "classes": []
        }
        
        # Process the initial file
        with mock.patch('core.parser.CodeParser._parse_python_with_tree_sitter') as mock_parse_python, \
             mock.patch('core.graph_store.GraphStore.save_graph'):
            
            mock_parse_python.return_value = initial_result
            self.graph_builder.process_file(test_file_path)
            
            # Verify initial state
            file_node_id = f"file:{test_file_path}"
            func_node_id = f"func:{test_file_path}:initial_function"
            assert self.graph_store.graph.has_node(file_node_id)
            assert self.graph_store.graph.has_node(func_node_id)
            
            # Save the initial node count
            initial_node_count = len(self.graph_store.graph.nodes)
            
            # Update the file
            with open(test_file_path, 'w') as f:
                f.write("""
\"\"\"Updated module.\"\"\"

def initial_function():
    return "initial"

def new_function():
    \"\"\"A new function.\"\"\"
    return "new"
""")
            
            # Mock updated parse result
            updated_result = {
                "functions": [
                    {
                        "name": "initial_function",
                        "line": 4,
                        "end_line": 5,
                        "docstring": None
                    },
                    {
                        "name": "new_function",
                        "line": 7,
                        "end_line": 9,
                        "docstring": "A new function."
                    }
                ],
                "classes": []
            }
            
            # Process the updated file
            mock_parse_python.return_value = updated_result
            self.graph_builder.process_file(test_file_path)
            
            # Verify the file was updated
            updated_func_node_id = f"func:{test_file_path}:new_function"
            assert self.graph_store.graph.has_node(updated_func_node_id)
            
            # Verify we have more nodes now
            assert len(self.graph_store.graph.nodes) > initial_node_count
            
            # Check the new function node
            new_func_node = self.graph_store.get_node_info(updated_func_node_id)
            assert new_func_node["name"] == "new_function"
            assert new_func_node["docstring"] == "A new function."
