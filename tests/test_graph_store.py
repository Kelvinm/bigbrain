"""
Tests for the graph_store module.
"""

import os
import tempfile
from pathlib import Path
import pickle
from unittest import mock

import pytest
import networkx as nx

from core.graph_store import GraphStore


class TestGraphStore:
    """Test cases for the GraphStore class."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        # Create a temporary file for the graph storage
        self.temp_dir = tempfile.TemporaryDirectory()
        self.graph_path = Path(self.temp_dir.name) / "test_graph.pickle"
        
        # Initialize graph store with the temporary path
        with mock.patch('core.graph_store.GraphStore.load_graph'):
            self.graph_store = GraphStore(self.graph_path)
    
    def teardown_method(self):
        """Clean up after each test method."""
        self.temp_dir.cleanup()
    
    def test_add_and_get_node(self):
        """Test adding a node and retrieving its information."""
        # Add a node
        self.graph_store.add_node(
            "func:test.py:test_function",
            "function",
            name="test_function",
            file_path="test.py",
            line=10
        )
        
        # Get node info
        node_info = self.graph_store.get_node_info("func:test.py:test_function")
        
        # Check node attributes
        assert node_info["type"] == "function"
        assert node_info["name"] == "test_function"
        assert node_info["file_path"] == "test.py"
        assert node_info["line"] == 10
    
    def test_add_edge(self):
        """Test adding an edge between nodes."""
        # Add nodes
        self.graph_store.add_node(
            "file:test.py",
            "file", 
            name="test.py",
            file_path="test.py"
        )
        
        self.graph_store.add_node(
            "func:test.py:test_function",
            "function",
            name="test_function",
            file_path="test.py",
            line=10
        )
        
        # Add edge
        self.graph_store.add_edge(
            "file:test.py",
            "func:test.py:test_function",
            "contains"
        )
        
        # Check edge existence
        assert self.graph_store.graph.has_edge("file:test.py", "func:test.py:test_function")
        
        # Check edge attributes
        edge_attrs = self.graph_store.graph.get_edge_data(
            "file:test.py", 
            "func:test.py:test_function"
        )
        assert edge_attrs["type"] == "contains"
    
    def test_remove_file_nodes(self):
        """Test removing all nodes associated with a specific file."""
        # Add file node
        self.graph_store.add_node(
            "file:test.py",
            "file", 
            name="test.py",
            file_path="test.py"
        )
        
        # Add function nodes for the file
        self.graph_store.add_node(
            "func:test.py:function1",
            "function",
            name="function1",
            file_path="test.py",
            line=10
        )
        
        self.graph_store.add_node(
            "func:test.py:function2",
            "function",
            name="function2",
            file_path="test.py",
            line=20
        )
        
        # Add edges
        self.graph_store.add_edge(
            "file:test.py",
            "func:test.py:function1",
            "contains"
        )
        
        self.graph_store.add_edge(
            "file:test.py",
            "func:test.py:function2",
            "contains"
        )
        
        # Initial check
        assert len(self.graph_store.graph.nodes) == 3
        
        # Remove file nodes
        self.graph_store.remove_file_nodes("test.py")
        
        # Check nodes were removed
        assert len(self.graph_store.graph.nodes) == 0
        assert len(self.graph_store.file_nodes) == 0
    
    def test_save_and_load_graph(self):
        """Test saving and loading the graph to/from disk."""
        # Add some nodes
        self.graph_store.add_node(
            "file:test.py",
            "file", 
            name="test.py",
            file_path="test.py"
        )
        
        self.graph_store.add_node(
            "func:test.py:test_function",
            "function",
            name="test_function",
            file_path="test.py",
            line=10
        )
        
        # Save the graph
        self.graph_store.save_graph()
        
        # Create a new graph store to load the saved graph
        new_graph_store = GraphStore(self.graph_path)
        
        # Check loaded graph has same nodes
        assert len(new_graph_store.graph.nodes) == len(self.graph_store.graph.nodes)
        assert new_graph_store.graph.has_node("file:test.py")
        assert new_graph_store.graph.has_node("func:test.py:test_function")
    
    def test_get_node_info_nonexistent(self):
        """Test getting information for a non-existent node (edge case)."""
        node_info = self.graph_store.get_node_info("nonexistent_node")
        assert node_info is None
    
    def test_add_edge_missing_nodes(self):
        """Test adding an edge with missing nodes (failure case)."""
        with pytest.raises(ValueError) as excinfo:
            self.graph_store.add_edge(
                "source_node",
                "target_node",
                "relationship"
            )
        
        assert "Missing nodes" in str(excinfo.value)
    
    def test_get_graph_stats(self):
        """Test getting statistics about the graph."""
        # Add nodes of different types
        self.graph_store.add_node(
            "file:test.py",
            "file", 
            name="test.py",
            file_path="test.py"
        )
        
        self.graph_store.add_node(
            "func:test.py:function1",
            "function",
            name="function1",
            file_path="test.py",
            line=10
        )
        
        self.graph_store.add_node(
            "class:test.py:TestClass",
            "class",
            name="TestClass",
            file_path="test.py",
            line=20
        )
        
        # Add edges of different types
        self.graph_store.add_edge(
            "file:test.py",
            "func:test.py:function1",
            "contains"
        )
        
        self.graph_store.add_edge(
            "file:test.py",
            "class:test.py:TestClass",
            "contains"
        )
        
        # Get stats
        stats = self.graph_store.get_graph_stats()
        
        # Check stats
        assert stats["total_nodes"] == 3
        assert stats["total_edges"] == 2
        assert stats["indexed_files"] == 1
        assert stats["node_types"]["file"] == 1
        assert stats["node_types"]["function"] == 1
        assert stats["node_types"]["class"] == 1
        assert stats["edge_types"]["contains"] == 2
