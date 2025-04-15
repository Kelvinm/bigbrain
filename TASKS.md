# Project Tasks

## Phase 1: Backend Foundation & Core Python Parsing (MVP)
Current Phase: In Progress (April 15, 2025)

### Completed
- [x] Set up initial project structure (directories, virtual environment)
- [x] Create basic configuration module (`config.py`)
- [x] Implement parser module skeleton (`core/parser.py`)
- [x] Implement graph store module for NetworkX integration (`core/graph_store.py`)
- [x] Define JSON protocol for bridge communication (`bridge/protocol.py`)
- [x] Create bridge handler for stdin/stdout communication (`bridge/handler.py`)
- [x] Set up main entry point (`main.py`)
- [x] Update project documentation (`README.md`)

### In Progress
- [x] Implement graph builder module to connect parser and graph store (`core/graph_builder.py`)
- [x] Complete tree-sitter integration in the parser module
- [x] Create comprehensive unit tests for all modules
- [x] Test the complete pipeline for Python file parsing
- [x] Document the JSON protocol fully

### Up Next
- [x] Set up GitHub Actions for CI/CD testing
- [x] Create a simple command-line interface for manual backend testing
- [ ] Prepare for Phase 2 (Enhanced Parsing & Relationships)

## Phase 2: Backend - Enhanced Parsing & Relationships
Status: Not Started

### Tasks
- [ ] Enhance parser to extract imports, function calls, docstrings, and inheritance
- [ ] Update graph builder to add relationship edges (IMPORTS, CALLS, INHERITS_FROM)
- [ ] Store docstrings as node attributes for use in RAG
- [ ] Add tests for new parsing features
- [ ] Update documentation to reflect enhanced capabilities

## Phase 3: Backend Querying & VS Code Bridge Setup
Status: Not Started

### Tasks
- [ ] Create query engine module (`core/query_engine.py`)
- [ ] Implement basic query functions (find definition, callers, documentation)
- [ ] Update bridge to handle query_graph commands
- [ ] Set up VS Code extension project structure
- [ ] Implement backend process manager in the extension
- [ ] Create bridge client for VS Code extension
- [ ] Implement file system watcher for update_file events
- [ ] Add "Index Project" command
- [ ] Create status bar indicator

## Phase 4: VS Code Agent Integration & Basic RAG
Status: Not Started

### Tasks
- [ ] Implement chat agent participant
- [ ] Create basic request handler for VS Code chat
- [ ] Implement query formulation based on chat requests
- [ ] Integrate bridge client with query system
- [ ] Implement basic RAG functionality
  - [ ] Extract context from graph queries
  - [ ] Augment prompts with context
  - [ ] Stream responses to chat UI
- [ ] Add error handling for backend communication

## Phase 5: Multi-Language Support & Advanced RAG/Agent Features
Status: Not Started

### Tasks
- [ ] Add support for JavaScript/TypeScript
- [ ] Refine parser and graph builder for multi-language support
- [ ] Implement advanced context selection/ranking
- [ ] Add current editor context integration
- [ ] Enhance agent interaction capabilities
- [ ] Implement extension configuration settings

## Phase 6: Optimization, Packaging & Standalone Viability
Status: Not Started

### Tasks
- [ ] Perform performance profiling and optimization
- [ ] Evaluate NetworkX scalability
- [ ] Refine error handling and logging
- [ ] Complete documentation for standalone use
- [ ] Package the VS Code extension
- [ ] Add final tests and integration tests
- [ ] Prepare for potential marketplace publication
