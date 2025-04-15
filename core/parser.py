"""
Source code parser using tree-sitter.

This module handles parsing of source code files and extracting relevant structures
like functions, classes, imports, etc. using the tree-sitter library.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import os
import tempfile
import subprocess
import time

import tree_sitter
from tree_sitter import Language, Parser, Node, Tree

from config import GRAMMAR_DIR, SUPPORTED_LANGUAGES, MAX_FILE_SIZE

# Configure logging
logger = logging.getLogger(__name__)


class CodeParser:
    """
    Parser for extracting code structures using tree-sitter.
    """
    
    def __init__(self):
        """
        Initialize the parser with supported languages.
        """
        self.parser = Parser()
        self.languages: Dict[str, Language] = {}
        self._load_languages()
    
    def _load_languages(self) -> None:
        """
        Load the language grammars for tree-sitter.
        
        This method ensures that tree-sitter grammars are available for supported languages.
        If grammars don't exist, it will attempt to download and build them.
        
        Raises:
            FileNotFoundError: If grammar files are not found and cannot be built.
        """
        try:
            # Ensure the grammar directory exists
            GRAMMAR_DIR.mkdir(exist_ok=True, parents=True)
            
            # For Python (initial implementation)
            self._ensure_python_grammar()
            
        except Exception as e:
            logger.error(f"Error loading language grammars: {str(e)}")
            raise
    
    def _ensure_python_grammar(self) -> None:
        """
        Ensure the Python grammar is available for tree-sitter.
        
        This method checks if the Python grammar exists, and if not,
        attempts to download and build it.
        
        Raises:
            RuntimeError: If the grammar cannot be built.
        """
        python_grammar_path = GRAMMAR_DIR / "python.so"
        
        if not python_grammar_path.exists():
            logger.info("Python grammar not found. Attempting to build it.")
            
            # Create a temporary directory for building the grammar
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                
                # Clone the Python grammar repository
                try:
                    logger.info("Cloning tree-sitter-python repository...")
                    subprocess.run(
                        ["git", "clone", "https://github.com/tree-sitter/tree-sitter-python.git", str(tmp_path)],
                        check=True,
                        capture_output=True
                    )
                    
                    # Build the grammar
                    logger.info("Building Python grammar...")
                    tree_sitter.Language.build_library(
                        str(python_grammar_path),
                        [str(tmp_path)]
                    )
                    
                    logger.info(f"Python grammar built successfully at {python_grammar_path}")
                    
                except subprocess.SubprocessError as e:
                    logger.error(f"Failed to clone tree-sitter-python: {str(e)}")
                    raise RuntimeError("Could not clone tree-sitter-python repository") from e
                    
                except Exception as e:
                    logger.error(f"Failed to build Python grammar: {str(e)}")
                    raise RuntimeError("Could not build Python grammar") from e
        
        # Load the Python language
        try:
            self.languages["python"] = Language(str(python_grammar_path), 'python')
            logger.info("Python language loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Python language: {str(e)}")
            raise RuntimeError("Could not load Python language") from e
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect the programming language of a file based on its extension.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            str: Language identifier or None if unsupported.
        """
        suffix = file_path.suffix.lower()
        
        for lang, config in SUPPORTED_LANGUAGES.items():
            if suffix in config["extensions"]:
                return lang
                
        return None
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a source code file and extract its structures.
        
        Args:
            file_path: Path to the file to parse.
            
        Returns:
            Dict[str, Any]: Parsed structures including functions, classes, etc.
            
        Raises:
            ValueError: If the file is too large or unsupported.
            IOError: If file cannot be read.
        """
        # Check file size
        if file_path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(f"File {file_path} exceeds maximum size limit")
        
        # Detect language
        language = self.detect_language(file_path)
        if not language:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
        
        # Parse the source code
        return self._parse_source(source_code, language, file_path)
    
    def _parse_source(self, source_code: str, language: str, file_path: Path) -> Dict[str, Any]:
        """
        Parse source code content and extract structures.
        
        Args:
            source_code: Source code content as string.
            language: Programming language identifier.
            file_path: Path to the original file (for reference).
            
        Returns:
            Dict[str, Any]: Parsed structures.
        """
        result = {
            "file_path": str(file_path),
            "language": language,
            "functions": [],
            "classes": [],
            # Will add more structure types in future phases
        }
        
        # For Phase 1, handle only Python
        if language == "python":
            result.update(self._parse_python_with_tree_sitter(source_code, file_path))
        
        return result
    
    def _parse_python_with_tree_sitter(self, source_code: str, file_path: Path) -> Dict[str, Any]:
        """
        Parse Python source code using tree-sitter and extract structures.
        
        Args:
            source_code: Python source code as string.
            file_path: Path to the original file.
            
        Returns:
            Dict[str, Any]: Extracted Python structures.
        """
        # Set the language for the parser
        self.parser.set_language(self.languages["python"])
        
        # Parse the source code into a syntax tree
        tree = self.parser.parse(bytes(source_code, 'utf8'))
        
        # Extract structures
        functions = []
        classes = []
        imports = []
        function_calls = []
        
        # Get the root node of the syntax tree
        root_node = tree.root_node
        
        # Find function and class definitions, imports, and function calls
        for child in root_node.children:
            if child.type == 'function_definition':
                function_info = self._extract_function_info(child, source_code)
                functions.append(function_info)
                
            elif child.type == 'class_definition':
                class_info = self._extract_class_info(child, source_code)
                classes.append(class_info)
                
            elif child.type == 'import_statement':
                import_info = self._extract_import_info(child, source_code)
                imports.append(import_info)
                
            elif child.type == 'import_from_statement':
                import_info = self._extract_import_from_info(child, source_code)
                imports.append(import_info)
        
        # Extract function calls from the entire tree
        function_calls = self._extract_function_calls(root_node, source_code)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "function_calls": function_calls
        }
    
    def _extract_function_info(self, node: Node, source_code: str) -> Dict[str, Any]:
        """
        Extract information about a function from its syntax tree node.
        
        Args:
            node: The function_definition node.
            source_code: The source code string.
            
        Returns:
            Dict[str, Any]: Function information.
        """
        # Get the function name
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break
                
        if not name_node:
            # Handle lambda or unnamed functions
            name = f"unnamed_function_{node.start_point[0]}"
        else:
            name = self._get_node_text(name_node, source_code)
        
        # Get function line information
        start_line = node.start_point[0] + 1  # Convert to 1-based line numbers
        end_line = node.end_point[0] + 1
        
        # Extract docstring if present
        docstring = self._extract_docstring(node, source_code)
        
        return {
            "name": name,
            "line": start_line,
            "end_line": end_line,
            "docstring": docstring
        }
    
    def _extract_class_info(self, node: Node, source_code: str) -> Dict[str, Any]:
        """
        Extract information about a class from its syntax tree node.
        
        Args:
            node: The class_definition node.
            source_code: The source code string.
            
        Returns:
            Dict[str, Any]: Class information.
        """
        # Get the class name
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break
                
        if not name_node:
            name = f"unnamed_class_{node.start_point[0]}"
        else:
            name = self._get_node_text(name_node, source_code)
        
        # Get class line information
        start_line = node.start_point[0] + 1  # Convert to 1-based line numbers
        end_line = node.end_point[0] + 1
        
        # Extract docstring if present
        docstring = self._extract_docstring(node, source_code)
        
        # Extract class methods
        methods = []
        class_body = None
        
        # Find the class body node
        for child in node.children:
            if child.type == 'block':
                class_body = child
                break
        
        if class_body:
            for child in class_body.children:
                if child.type == 'function_definition':
                    method_info = self._extract_function_info(child, source_code)
                    methods.append(method_info)
        
        return {
            "name": name,
            "line": start_line,
            "end_line": end_line,
            "docstring": docstring,
            "methods": methods
        }
    
    def _extract_docstring(self, node: Node, source_code: str) -> Optional[str]:
        """
        Extract a docstring from a function or class definition.
        
        Args:
            node: The function_definition or class_definition node.
            source_code: The source code string.
            
        Returns:
            Optional[str]: Docstring text if found, None otherwise.
        """
        # Find the block node (function/class body)
        block_node = None
        for child in node.children:
            if child.type == 'block':
                block_node = child
                break
                
        if not block_node or len(block_node.children) < 2:
            return None
        
        # Check for string expression statement as the first non-trivial child
        for child in block_node.children:
            if child.type in ('expression_statement', 'string'):
                # Check if it contains a string literal
                string_node = None
                
                if child.type == 'expression_statement':
                    # Look for string literals in the expression
                    for grandchild in child.children:
                        if grandchild.type == 'string':
                            string_node = grandchild
                            break
                else:  # child.type == 'string'
                    string_node = child
                
                if string_node:
                    # Extract the string content
                    docstring = self._get_node_text(string_node, source_code)
                    
                    # Remove quotes and normalize
                    if docstring.startswith('"""') and docstring.endswith('"""'):
                        return docstring[3:-3].strip()
                    elif docstring.startswith("'''") and docstring.endswith("'''"):
                        return docstring[3:-3].strip()
                    elif docstring.startswith('"') and docstring.endswith('"'):
                        return docstring[1:-1].strip()
                    elif docstring.startswith("'") and docstring.endswith("'"):
                        return docstring[1:-1].strip()
                    else:
                        return docstring.strip()
                
            # If we've found a non-trivial, non-docstring node, stop searching
            elif child.type not in ('newline', 'comment', 'pass_statement'):
                break
        
        return None
    
    def _extract_import_info(self, node: Node, source_code: str) -> Dict[str, Any]:
        """
        Extract information about an import statement from its syntax tree node.
        
        Args:
            node: The import_statement node.
            source_code: The source code string.
            
        Returns:
            Dict[str, Any]: Import information.
        """
        imports = []
        
        # Get the line information
        line = node.start_point[0] + 1  # Convert to 1-based line numbers
        
        # Extract all the imported modules
        for child in node.children:
            if child.type == 'dotted_name':
                module_name = self._get_node_text(child, source_code)
                imports.append({
                    "module": module_name,
                    "name": None,  # No specific name for regular imports
                    "alias": None  # Will be set below if aliased
                })
                
            # Check for aliases (import x as y)
            elif child.type == 'aliased_import':
                # Find the module name and alias
                module = None
                alias = None
                
                for aliased_child in child.children:
                    if aliased_child.type == 'dotted_name':
                        module = self._get_node_text(aliased_child, source_code)
                    elif aliased_child.type == 'identifier':
                        alias = self._get_node_text(aliased_child, source_code)
                
                if module:
                    imports.append({
                        "module": module,
                        "name": None,
                        "alias": alias
                    })
        
        return {
            "type": "import",
            "line": line,
            "imports": imports
        }
    
    def _extract_import_from_info(self, node: Node, source_code: str) -> Dict[str, Any]:
        """
        Extract information about a from-import statement from its syntax tree node.
        
        Args:
            node: The import_from_statement node.
            source_code: The source code string.
            
        Returns:
            Dict[str, Any]: Import information.
        """
        imports = []
        module = None
        line = node.start_point[0] + 1  # Convert to 1-based line numbers
        
        # Extract the module name
        for child in node.children:
            if child.type == 'dotted_name':
                module = self._get_node_text(child, source_code)
                break
        
        # Handle relative imports (from . import x)
        if not module:
            # Count dots for relative imports
            dots = 0
            for child in node.children:
                if child.type == '.':
                    dots += 1
            
            if dots > 0:
                module = '.' * dots
        
        # Extract the imported names
        import_clause = None
        for child in node.children:
            if child.type == 'import_clause':
                import_clause = child
                break
                
        if import_clause:
            # Handle "from x import *"
            for child in import_clause.children:
                if child.type == 'wildcard_import':
                    imports.append({
                        "module": module,
                        "name": "*",
                        "alias": None
                    })
                    break
            
            # Handle "from x import y, z"
            for child in import_clause.named_children:
                if child.type == 'dotted_name':
                    name = self._get_node_text(child, source_code)
                    imports.append({
                        "module": module,
                        "name": name,
                        "alias": None
                    })
                elif child.type == 'aliased_import':
                    # Handle "from x import y as z"
                    name = None
                    alias = None
                    
                    for aliased_child in child.children:
                        if aliased_child.type == 'dotted_name':
                            name = self._get_node_text(aliased_child, source_code)
                        elif aliased_child.type == 'identifier':
                            alias = self._get_node_text(aliased_child, source_code)
                    
                    if name:
                        imports.append({
                            "module": module,
                            "name": name,
                            "alias": alias
                        })
        
        return {
            "type": "from_import",
            "line": line,
            "module": module,
            "imports": imports
        }
    
    def _get_node_text(self, node: Node, source_code: str) -> str:
        """
        Get the text content of a node from the source code.
        
        Args:
            node: The syntax tree node.
            source_code: The source code string.
            
        Returns:
            str: The text content of the node.
        """
        start_byte = node.start_byte
        end_byte = node.end_byte
        
        # Extract the text from the source code
        try:
            return source_code[start_byte:end_byte]
        except IndexError:
            logger.error(f"Index error extracting node text: {start_byte}:{end_byte} from source of length {len(source_code)}")
            return ""


# For testing/development
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        parser = CodeParser()
        test_file = Path(sys.argv[1])
        try:
            result = parser.parse_file(test_file)
            print(f"Parsed {test_file}:")
            print(f"Functions: {len(result['functions'])}")
            for func in result['functions']:
                print(f"  - {func['name']} (line {func['line']})")
                if func['docstring']:
                    print(f"    Docstring: {func['docstring'][:50]}...")
            
            print(f"Classes: {len(result['classes'])}")
            for cls in result['classes']:
                print(f"  - {cls['name']} (line {cls['line']})")
                if cls['docstring']:
                    print(f"    Docstring: {cls['docstring'][:50]}...")
                print(f"    Methods: {len(cls['methods'])}")
                for method in cls['methods']:
                    print(f"      - {method['name']} (line {method['line']})")
                    
        except Exception as e:
            print(f"Error parsing {test_file}: {str(e)}")
    else:
        print("Usage: python parser.py <file_path>")
