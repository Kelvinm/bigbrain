# BigBrain: Graph RAG for Code Understanding

A Retrieval Augmented Generation (RAG) system for code understanding, built using a graph-based approach to represent code structure and relationships. BigBrain enhances AI coding assistance by providing context from your codebase through a knowledge graph.

## Project Goals

- Create a robust Python backend framework that parses source code and builds a knowledge graph
- Develop a VS Code extension that integrates with the Agent Chat system
- Enhance AI coding assistance by providing relevant code context through graph-based retrieval
- Support multiple programming languages and provide a seamless coding experience

## Features

- Python backend that parses source code and builds a knowledge graph
- VS Code extension that communicates with the backend and provides enhanced AI coding assistance
- JSON protocol for communication between the extension and backend
- Support for Python code parsing (with more languages to come)
- Graph-based representation of code structure and relationships
- Retrieval-Augmented Generation (RAG) for improved code understanding

## Installation

### Backend (Python)

1. Clone the repository
2. Create a virtual environment:
   ```bash
   cd bigbrain
   uv venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   uv pip install -e .
   ```

### Tree-Sitter Grammars

To use the parser functionality, you need to have the tree-sitter grammars compiled:

```bash
# This feature will be fully implemented in future releases
# For now, the parser will work with a simplified approach
```

## Usage

### Running the Backend

```bash
python main.py --graph-path=/path/to/graph.pickle --log-level=INFO
```

### Backend API

The backend communicates via JSON over stdin/stdout using the protocol defined in `bridge/protocol.py`.

## Development

### Project Structure

```
/home/kelvin/git/bigbrain/
├── bridge/                  # JSON communication module
│   ├── __init__.py
│   ├── handler.py           # Handles stdin/stdout communication
│   └── protocol.py          # JSON protocol definitions
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── graph_builder.py     # Builds graph from parsed data
│   ├── graph_store.py       # Graph management with NetworkX
│   └── parser.py            # Code parsing with tree-sitter
├── grammars/                # For tree-sitter language files
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_parser.py       # Tests for parser module
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── config.py                # Configuration settings
├── main.py                  # Main entry point
├── README.md                # Project documentation
└── setup.py                 # Package installation configuration
```

### Core Components

1. **Parser Module** (`core/parser.py`):
   - Parses source code files and extracts functions, classes
   - Currently supports Python files (with placeholders for tree-sitter integration)
   - Designed for extensibility to add more languages in future phases

2. **Graph Store Module** (`core/graph_store.py`):
   - Manages the knowledge graph using NetworkX
   - Supports adding nodes and edges with attributes
   - Handles persistence to/from disk using pickle
   - Includes file-based node removal for updates

3. **Graph Builder Module** (`core/graph_builder.py`):
   - Converts parsed code structures into graph elements
   - Creates file, function, and class nodes with relationships
   - Updates the graph when files change

4. **Bridge Protocol** (`bridge/protocol.py`):
   - Defines the JSON communication protocol as Pydantic models
   - Includes commands like UPDATE_FILE, QUERY_GRAPH, GET_STATUS, and SHUTDOWN
   - Provides structured request and response formats

5. **Bridge Handler** (`bridge/handler.py`):
   - Processes JSON messages from stdin
   - Dispatches commands to appropriate handlers
   - Sends responses back via stdout
   - Handles errors and validation

6. **Main Entry Point** (`main.py`):
   - Parses command line arguments
   - Sets up logging
   - Initializes components and starts the bridge handler

### Design Decisions

- **Pydantic Models**: Used for robust JSON protocol validation and serialization
- **NetworkX**: Chosen for graph representation due to its flexibility and Python integration
- **Tree-Sitter**: Selected for reliable and efficient code parsing across languages
- **Modular Architecture**: Clear separation between parsing, graph building, and communication
- **Python-dotenv**: Used for environment variable management
- **Pickle Serialization**: Used for graph persistence (with potential for alternatives in future)

### Development Roadmap

Following a phased approach as outlined in PLANNING.md:

1. **Phase 1**: Backend Foundation & Core Python Parsing (Current)
2. **Phase 2**: Enhanced Parsing & Relationships
3. **Phase 3**: Backend Querying & VS Code Bridge Setup
4. **Phase 4**: VS Code Agent Integration & Basic RAG
5. **Phase 5**: Multi-Language Support & Advanced Features
6. **Phase 6**: Optimization & Packaging

### Running Tests

```bash
pytest
```

## License

See the [LICENSE](LICENSE) file for details.