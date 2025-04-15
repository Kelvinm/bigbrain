"""
Graph store module for managing the code knowledge graph.

This module provides a NetworkX-based in-memory graph management system,
with persistence capabilities (using pickle), and methods to update or
remove nodes/edges related to specific files.
"""

import logging
import pickle
import os
import networkx as nx
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)


class GraphStore:
    """
    Manages a knowledge graph of code entities and their relationships.
    
    The GraphStore uses NetworkX DiGraph as the underlying representation
    and provides methods to add, update, query, and persist the graph.
    Node removal is handled at the file level to maintain consistency.
    """
    
    def __init__(self, graph_path: Optional[Path] = None):
        """
        Initialize the graph store with an optional path for persistence.
        
        Args:
            graph_path (Path, optional): Path to store/load the graph pickle file.
                If None, the graph will only be kept in memory.
        """
        self.graph = nx.DiGraph()
        self.graph_path = graph_path
        self.file_nodes: Dict[str, Set[str]] = {}  # Maps file paths to node IDs
        
        # Try to load existing graph if path is provided
        if graph_path and graph_path.exists():
            self.load_graph()
    
    def add_node(self, node_id: str, attributes: Dict[str, Any], file_path: Optional[str] = None) -> bool:
        """
        Add a node to the graph with the given attributes.
        
        Args:
            node_id (str): Unique identifier for the node.
            attributes (Dict[str, Any]): Node attributes.
            file_path (str, optional): Source file path this node belongs to.
                Used for file-based node removal.
            
        Returns:
            bool: True if node was added, False if it already existed.
        """
        node_exists = node_id in self.graph.nodes
        self.graph.add_node(node_id, **attributes)
        
        # Track which file this node belongs to
        if file_path:
            if file_path not in self.file_nodes:
                self.file_nodes[file_path] = set()
            self.file_nodes[file_path].add(node_id)
        
        return not node_exists
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str, 
                attributes: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an edge between two nodes with a specific type and optional attributes.
        
        Args:
            source_id (str): Source node ID.
            target_id (str): Target node ID.
            edge_type (str): Type of the relationship.
            attributes (Dict[str, Any], optional): Edge attributes.
            
        Returns:
            bool: True if edge was added, False if it already existed.
        """
        if attributes is None:
            attributes = {}
        
        # Add the edge_type to attributes
        attributes['edge_type'] = edge_type
        
        edge_exists = self.graph.has_edge(source_id, target_id)
        self.graph.add_edge(source_id, target_id, **attributes)
        
        return not edge_exists
    
    def remove_file_nodes(self, file_path: str) -> int:
        """
        Remove all nodes associated with a specific file.
        
        This is used when a file is deleted or needs to be re-indexed
        to ensure consistency.
        
        Args:
            file_path (str): Path of the file whose nodes should be removed.
            
        Returns:
            int: Number of nodes removed.
        """
        if file_path not in self.file_nodes:
            return 0
        
        nodes_to_remove = list(self.file_nodes[file_path])
        self.graph.remove_nodes_from(nodes_to_remove)
        count = len(nodes_to_remove)
        del self.file_nodes[file_path]
        
        return count
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node and its attributes by ID.
        
        Args:
            node_id (str): ID of the node to retrieve.
            
        Returns:
            Dict[str, Any] or None: Node attributes if found, None otherwise.
        """
        if node_id in self.graph.nodes:
            return dict(self.graph.nodes[node_id])
        return None
    
    def get_connected_nodes(self, node_id: str, edge_type: Optional[str] = None,
                           direction: str = "outgoing") -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get nodes connected to the specified node.
        
        Args:
            node_id (str): ID of the node to find connections for.
            edge_type (str, optional): Filter by edge type.
            direction (str): "outgoing" for successors, "incoming" for predecessors,
                or "both" for both directions.
                
        Returns:
            List[Tuple[str, Dict[str, Any]]]: List of (node_id, attributes) pairs.
        """
        if node_id not in self.graph.nodes:
            return []
        
        connected_nodes = []
        
        if direction in ["outgoing", "both"]:
            for succ_id in self.graph.successors(node_id):
                edge_data = self.graph.get_edge_data(node_id, succ_id)
                if edge_type is None or edge_data.get("edge_type") == edge_type:
                    connected_nodes.append((succ_id, dict(self.graph.nodes[succ_id])))
        
        if direction in ["incoming", "both"]:
            for pred_id in self.graph.predecessors(node_id):
                edge_data = self.graph.get_edge_data(pred_id, node_id)
                if edge_type is None or edge_data.get("edge_type") == edge_type:
                    connected_nodes.append((pred_id, dict(self.graph.nodes[pred_id])))
        
        return connected_nodes
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the graph.
        
        Returns:
            Dict[str, int]: Dictionary with graph statistics.
        """
        edge_types = {}
        for _, _, edge_data in self.graph.edges(data=True):
            edge_type = edge_data.get("edge_type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "files": len(self.file_nodes),
            "edge_types": edge_types
        }
    
    def save_graph(self, path: Optional[Path] = None) -> bool:
        """
        Save the graph to disk using pickle.
        
        Args:
            path (Path, optional): Path to save the graph to.
                If None, uses the path provided at initialization.
                
        Returns:
            bool: True if successful, False otherwise.
        """
        save_path = path or self.graph_path
        if not save_path:
            logger.error("No path specified for saving graph")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(save_path.parent, exist_ok=True)
            
            # Create a dict with all data needed to reconstruct the graph
            data_to_save = {
                "graph": self.graph,
                "file_nodes": self.file_nodes
            }
            
            with open(save_path, "wb") as f:
                pickle.dump(data_to_save, f)
                
            logger.info(f"Graph saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            return False
    
    def load_graph(self, path: Optional[Path] = None) -> bool:
        """
        Load the graph from disk.
        
        Args:
            path (Path, optional): Path to load the graph from.
                If None, uses the path provided at initialization.
                
        Returns:
            bool: True if successful, False otherwise.
        """
        load_path = path or self.graph_path
        if not load_path or not load_path.exists():
            logger.error(f"Graph file not found: {load_path}")
            return False
        
        try:
            with open(load_path, "rb") as f:
                data = pickle.load(f)
            
            self.graph = data["graph"]
            self.file_nodes = data["file_nodes"]
            
            logger.info(f"Graph loaded from {load_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            return False
    
    def clear(self) -> None:
        """
        Clear the graph and file node mappings.
        """
        self.graph.clear()
        self.file_nodes.clear()
        logger.info("Graph cleared")
