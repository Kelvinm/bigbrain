# Graph RAG Project Plan: Backend Framework & VS Code Agent Extension

## 1. Project Objectives

1.  **Develop a Python Backend Framework:** Create a robust backend system capable of parsing source code (`py-tree-sitter`), building and maintaining a knowledge graph (`NetworkX`), and exposing querying capabilities via a defined JSON protocol over stdin/stdout. This framework should be usable independently.
2.  **Create a VS Code Extension:** Build a VS Code extension that:
    *   Manages the lifecycle of the Python backend process using Node.js `child_process`.
    *   Communicates with the backend via the JSON protocol.
    *   Triggers graph updates based on file changes (`onDidSaveTextDocument`).
    *   Integrates with VS Code's Agent Chat (`@workspace` agent participant).
    *   Uses the backend's knowledge graph as a retrieval source for a RAG (Retrieval-Augmented Generation) process to provide context to LLM requests within the chat agent.
    *   Enhances the AI coding assistant's capabilities for code understanding, generation, and testing within the user's workspace.

## 2. Core Architecture

### 2.1 Python Backend Framework

*   **Parser (`core/parser.py`):** `py-tree-sitter` based, modular language support, extracts code structures (functions, classes, imports, calls, etc.).
*   **Graph Builder (`core/graph_builder.py`):** Translates parsed data into graph nodes/edges.
*   **Graph Store (`core/graph_store.py`):** `NetworkX`-based in-memory graph management, persistence (`pickle`), file-based node removal for updates.
*   **Query Engine (`core/query_engine.py`):** Executes specific graph traversals based on query commands.
*   **Bridge Handler (`bridge/handler.py`, `protocol.py`):** Defines and handles JSON communication protocol over stdin/stdout.
*   **Main Entry Point (`main.py`):** Manages stdin/stdout, process lifecycle, dispatches commands.
*   **Configuration (`config.py`):** Settings for paths, grammars, etc.

### 2.2 VS Code Extension (TypeScript/JavaScript)

*   **Extension Core (`src/extension.ts`):** Activation logic, command registration, lifecycle management.
*   **Backend Process Manager (`src/backendManager.ts`):** Spawns, monitors, and manages communication with the Python `child_process`. Handles restarts and errors.
*   **Bridge Client (`src/bridgeClient.ts`):** Sends JSON requests (index file, query graph) to the Python backend and parses responses.
*   **Filesystem Watcher Integration:** Hooks into `vscode.workspace.onDidSaveTextDocument` to trigger `update_file` commands via the Bridge Client.
*   **Chat Agent Participant (`src/agentParticipant.ts`):**
    *   Registers the extension as a chat participant (e.g., `@graphrag`).
    *   Handles incoming chat requests (`vscode.ChatRequestHandler`).
    *   Analyzes requests to determine when graph context is needed.
    *   Formulates queries for the Python backend based on the request and editor context.
    *   Sends queries via the Bridge Client.
    *   **RAG Implementation:** Receives graph context, combines it with the original user prompt and potentially other context (e.g., open file snippets).
    *   Invokes the underlying LLM (via `vscode.LanguageModelAccess`) with the augmented prompt.
    *   Streams or presents the final response back to the chat interface.
*   **UI Components:**
    *   Commands (e.g., "GraphRAG: Index Project", "GraphRAG: Show Status").
    *   Status Bar Item (indicating backend status, indexing progress).
    *   Configuration Settings (`package.json` contribution points).

## 3. Phased Rollout Plan

### Phase 1: Backend Foundation & Core Python Parsing (MVP)

*   **Goal:** Establish the Python backend structure, parse Python files for core structures, build a simple graph, enable updates via file saves triggered externally.
*   **Backend Features:**
    *   Python project setup, dependencies, grammar compilation.
    *   `parser.py`: Extract Python files, functions, classes.
    *   `graph_store.py`: NetworkX DiGraph, add node/edge, save/load (pickle), remove by file.
    *   `graph_builder.py`: Populate graph from parse data.
    *   `main.py`/`bridge`: Handle `update_file` command via stdin/stdout JSON.
*   **Outcome:** A runnable Python backend that can build/update a graph from specified files via stdin commands. Document the JSON protocol.

### Phase 2: Backend - Enhanced Parsing & Relationships

*   **Goal:** Enrich the backend graph with more detailed code relationships (Python).
*   **Backend Features:**
    *   `parser.py`: Extract imports, function calls, docstrings, basic inheritance.
    *   `graph_builder.py`: Add `IMPORTS`, `CALLS`, `INHERITS_FROM` edges, store docstrings.
*   **Outcome:** Backend graph contains richer contextual links within Python code.

### Phase 3: Backend Querying & VS Code Bridge Setup

*   **Goal:** Enable backend querying and establish basic communication from VS Code.
*   **Backend Features:**
    *   `query_engine.py`: Implement basic query functions (find definition, callers, documentation by name).
    *   `main.py`/`bridge`: Handle `query_graph` command via JSON protocol.
*   **VS Code Extension Features:**
    *   Basic Extension project setup (TypeScript).
    *   Implement `BackendProcessManager`: Spawn Python process.
    *   Implement `BridgeClient`: Send `update_file` command JSON to backend stdin, basic stdout handling.
    *   Implement `onDidSaveTextDocument` listener to trigger `update_file` via Bridge Client.
    *   Register "Index Project" command that iterates workspace Python files and sends `update_file` for each.
    *   Add Status Bar Item showing basic backend status (running/stopped).
*   **Outcome:** Extension can start the backend and trigger graph updates on save/command. Backend can answer simple queries via stdin/stdout.

### Phase 4: VS Code Agent Integration & Basic RAG

*   **Goal:** Integrate with VS Code Chat Agent and perform basic RAG using graph data.
*   **VS Code Extension Features:**
    *   Implement `AgentParticipant`: Register chat participant (`@graphrag`).
    *   Implement basic `vscode.ChatRequestHandler`: Intercept simple requests.
    *   Implement query formulation: Based on chat request, formulate a simple query (e.g., find definition) for the backend.
    *   Integrate `BridgeClient` to send `query_graph` requests and receive results.
    *   **Basic RAG:**
        *   Get context string(s) from backend query response.
        *   Prepend context to the user's original prompt.
        *   Use `vscode.LanguageModelAccess.chatRequest` to send the augmented prompt to the default LLM.
        *   Stream the LLM response back to the chat UI.
    *   Handle errors gracefully (backend communication, query failures).
*   **Outcome:** User can invoke `@graphrag` in chat, the extension queries the backend, gets context, asks the LLM, and shows the response.

### Phase 5: Multi-Language Support & Advanced RAG/Agent Features

*   **Goal:** Extend language support, improve RAG, enhance agent interaction.
*   **Backend Features:**
    *   Add support for JS/TS (grammars, queries).
    *   Refine `parser.py`, `graph_builder.py` for multi-language handling.
*   **VS Code Extension Features:**
    *   Pass language information in `update_file` commands.
    *   Adapt query formulation for different languages if needed.
    *   **Improved RAG:**
        *   More sophisticated context selection/ranking based on query results.
        *   Consider context from the currently active editor.
        *   Potentially use LLM embeddings for semantic search over docstrings (advanced).
    *   **Enhanced Agent Interaction:**
        *   Handle more complex chat commands/requests.
        *   Provide follow-up suggestions or actions.
        *   Use VS Code progress indicators for long operations (indexing).
        *   Implement extension configuration settings (Python path, graph path, include/exclude patterns).
*   **Outcome:** More robust, multi-language capable agent with smarter context retrieval and better UX.

### Phase 6: Optimization, Packaging & Standalone Viability

*   **Goal:** Optimize performance, package the extension, and ensure the backend is documented for standalone use.
*   **Backend Features:**
    *   Performance profiling and optimization (parsing, graph ops).
    *   Investigate NetworkX limits; plan for alternatives (Neo4j) if needed.
    *   Refine error handling and logging.
    *   Document the JSON protocol clearly for standalone use.
    *   Provide instructions for running the backend independently (dependencies, configuration).
*   **VS Code Extension Features:**
    *   Refine UI/UX based on usage.
    *   Add tests (unit/integration) for extension components.
    *   Package the extension (`vsce package`).
    *   Consider publishing to VS Code Marketplace.
*   **Outcome:** A polished, performant extension and a backend framework suitable for independent use or integration elsewhere.

## 4. Key Considerations

*   **Performance:** Backend indexing/updates, query latency, extension responsiveness.
*   **Accuracy:** AST parsing correctness, call graph resolution limitations.
*   **Scalability:** Large codebases, multiple languages, graph size (NetworkX memory).
*   **Error Handling:** Robust handling of parsing errors, process crashes, communication timeouts, API errors.
*   **State Management:** Consistency of the graph file, backend process state.
*   **User Experience (Extension):** Clear feedback (status bar, progress), intuitive commands, useful configuration.
*   **Security:** Sandboxing of the Python process, validation of inputs.
*   **API Stability:** Both the internal JSON protocol and VS Code API usage.

## 5. Technology Stack

*   **Backend:** Python 3.x, `py-tree-sitter`, `NetworkX`, `pickle`, `python-dotenv`.
*   **Frontend (VS Code Ext):** TypeScript, Node.js, VS Code API (`vscode`, `child_process`).
*   **Communication:** JSON over stdio pipes.