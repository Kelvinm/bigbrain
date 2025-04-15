"""
Configuration module for BigBrain.

This module defines constants, paths, and settings used throughout the project.
It centralizes configuration to make it easier to modify project-wide settings.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Set, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Project root directory (inferred from this file's location)
PROJECT_ROOT = Path(__file__).parent.absolute()

# Tree-sitter grammar paths
GRAMMAR_DIR = PROJECT_ROOT / "grammars"
os.makedirs(GRAMMAR_DIR, exist_ok=True)

# Output and storage paths
DATA_DIR = PROJECT_ROOT / "data"
os.makedirs(DATA_DIR, exist_ok=True)
GRAPH_FILE = DATA_DIR / "code_graph.pickle"

# Language support configuration
SUPPORTED_LANGUAGES = {
    "python": {
        "extensions": [".py"],
        "grammar_path": GRAMMAR_DIR / "tree-sitter-python",
        "grammar_url": "https://github.com/tree-sitter/tree-sitter-python",
    },
    # Additional languages will be added in Phase 5
}

# File parsing configuration
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB limit for files to parse

# Node types
NODE_TYPES = {
    "FILE": "FILE",  
    "CLASS": "CLASS",
    "FUNCTION": "FUNCTION",
    "METHOD": "METHOD",
    "PROPERTY": "PROPERTY",
    "VARIABLE": "VARIABLE",
    "IMPORT": "IMPORT",
    "MODULE": "MODULE",
}

# Edge types
EDGE_TYPES = {
    "CONTAINS": "CONTAINS",       # File contains class/function, class contains method
    "CALLS": "CALLS",             # Function/method calls another function/method
    "IMPORTS": "IMPORTS",         # File/module imports another module
    "INHERITS_FROM": "INHERITS_FROM", # Class inherits from another class
    "REFERENCES": "REFERENCES",   # References a variable or property
}

# Node ID format templates (to ensure uniqueness across the graph)
NODE_ID_FORMATS = {
    NODE_TYPES["FILE"]: "{path}",
    NODE_TYPES["CLASS"]: "{path}:class:{name}",
    NODE_TYPES["FUNCTION"]: "{path}:function:{name}",
    NODE_TYPES["METHOD"]: "{path}:class:{class_name}:method:{name}",
    NODE_TYPES["PROPERTY"]: "{path}:class:{class_name}:property:{name}",
    NODE_TYPES["VARIABLE"]: "{path}:variable:{name}",
    NODE_TYPES["IMPORT"]: "{path}:import:{name}",
    NODE_TYPES["MODULE"]: "module:{name}",
}

# Bridge protocol settings
PROTOCOL_VERSION = "1.0.0"
DEFAULT_COMMAND_TIMEOUT = 30.0  # seconds

# CLI settings
CLI_DEFAULT_VERBOSE = False
CLI_DEFAULT_OUTPUT_FORMAT = "text"  # "text" or "json"
