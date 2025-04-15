# BigBrain CLI Examples

This document provides practical examples for using the BigBrain CLI to interact with the knowledge graph.

## Table of Contents

1. [Installation](#installation)
2. [Processing Files](#processing-files)
3. [Graph Statistics](#graph-statistics)
4. [Querying the Graph](#querying-the-graph)
5. [Managing the Graph](#managing-the-graph)
6. [Output Formatting](#output-formatting)
7. [Advanced Usage](#advanced-usage)

## Installation

After cloning the repository, install the package in development mode:

```bash
# Navigate to the project directory
cd bigbrain

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -e .
```

Once installed, you can use the `bigbrain` command directly, or run the CLI with `python cli.py`.

## Processing Files

Add a single Python file to the graph:

```bash
# Basic usage
python cli.py process -f path/to/file.py

# With verbose output
python cli.py process -f path/to/file.py --verbose

# Using the installed command
bigbrain process -f path/to/file.py
```

Process multiple files in a batch:

```bash
# Process multiple files (shell script)
for file in src/*.py; do
  python cli.py process -f "$file"
done
```

## Graph Statistics

Get statistics about the current state of the graph:

```bash
# Basic stats
python cli.py stats

# Pretty-printed stats
python cli.py stats --pretty
```

Example output:
```json
{
  "total_nodes": 120,
  "total_edges": 180,
  "indexed_files": 15,
  "node_types": {
    "file": 15,
    "function": 50,
    "class": 30,
    "method": 40
  },
  "edge_types": {
    "contains": 150,
    "calls": 30
  }
}
```

## Querying the Graph

### Finding Definitions

Find the definition of a function or class:

```bash
# Find definition by name
python cli.py query find-definition -n function_name

# Find definition with file context
python cli.py query find-definition -n ClassA -f src/models.py
```

Example output:
```json
[
  {
    "id": "class:src/models.py:ClassA",
    "type": "class",
    "name": "ClassA",
    "file_path": "src/models.py",
    "line": 10,
    "end_line": 30,
    "docstring": "A class that represents model A."
  }
]
```

### Listing Functions

List all functions in a specific file:

```bash
# List functions in a file
python cli.py query list-functions -f src/utils.py

# Pretty-print the results
python cli.py query list-functions -f src/utils.py --pretty
```

### Listing Classes

List all classes in a specific file:

```bash
# List classes in a file
python cli.py query list-classes -f src/models.py
```

## Managing the Graph

Clear the graph to start fresh:

```bash
# Clear all nodes from the graph
python cli.py clear
```

Specify a custom graph storage location:

```bash
# Use a custom graph file location
python cli.py stats --graph-path /path/to/custom/graph.pickle
```

## Output Formatting

Use the `--pretty` flag for formatted JSON output:

```bash
# Pretty-print any command output
python cli.py stats --pretty
```

Enable verbose logging with the `--verbose` or `-v` flag:

```bash
# Get detailed logs during execution
python cli.py process -f path/to/file.py --verbose
```

## Advanced Usage

### Processing Complex Projects

For larger codebases, you might want to process all Python files recursively:

```bash
# Process all Python files in a project (shell script)
find ./project -name "*.py" | while read file; do
  python cli.py process -f "$file"
done
```

### Future Enhancements

In Phase 2, the CLI will be enhanced with additional query capabilities:

- Query for function calls (`query calls-to`)
- Query for imports (`query imports-in`) 
- Query for inheritance relationships (`query inherits-from`)
- Semantic search through docstrings (`query semantic-search`)
