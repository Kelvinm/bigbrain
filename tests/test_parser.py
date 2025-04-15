"""
Tests for the parser module.
"""

import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from core.parser import CodeParser


class TestParser:
    """Test cases for the CodeParser class."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        # Mock the tree-sitter language loading to avoid actual file operations
        with mock.patch('core.parser.CodeParser._load_languages'):
            self.parser = CodeParser()
            
            # Mock the languages dictionary
            self.parser.languages = {"python": mock.MagicMock()}
    
    def test_detect_language_python(self):
        """Test language detection for Python files."""
        test_file = Path("test_file.py")
        
        language = self.parser.detect_language(test_file)
        
        assert language == "python"
    
    def test_detect_language_unsupported(self):
        """Test language detection for unsupported file types."""
        test_file = Path("test_file.xyz")
        
        language = self.parser.detect_language(test_file)
        
        assert language is None
    
    def test_parse_python_file(self):
        """Test parsing a simple Python file with functions and classes."""
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
            # Mock the actual tree-sitter parsing to test our logic
            with mock.patch('tree_sitter.Parser.parse') as mock_parse, \
                 mock.patch('core.parser.CodeParser._parse_python_with_tree_sitter') as mock_parse_python:
                
                # Set up the mock to return a simple structure
                mock_parse_python.return_value = {
                    "functions": [
                        {
                            "name": "test_function",
                            "line": 2,
                            "end_line": 4,
                            "docstring": "Test function docstring."
                        }
                    ],
                    "classes": [
                        {
                            "name": "TestClass",
                            "line": 6,
                            "end_line": 9,
                            "docstring": "Test class docstring.",
                            "methods": [
                                {
                                    "name": "method",
                                    "line": 8,
                                    "end_line": 9,
                                    "docstring": None
                                }
                            ]
                        }
                    ]
                }
                
                # Parse the file
                result = self.parser.parse_file(Path(temp_file.name))
                
                # Check basic structure
                assert result["language"] == "python"
                assert result["file_path"] == temp_file.name
                
                # Check functions
                assert len(result["functions"]) == 1
                assert result["functions"][0]["name"] == "test_function"
                assert result["functions"][0]["docstring"] == "Test function docstring."
                
                # Check classes
                assert len(result["classes"]) == 1
                assert result["classes"][0]["name"] == "TestClass"
                assert result["classes"][0]["docstring"] == "Test class docstring."
                assert len(result["classes"][0]["methods"]) == 1
                assert result["classes"][0]["methods"][0]["name"] == "method"
                
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
    
    def test_parse_function_with_tree_sitter(self):
        """Test detailed tree-sitter parsing of a function with docstring."""
        # This test mocks internal tree-sitter node structure to test extraction logic
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            code = """
def example_function():
    \"\"\"This is a docstring.\"\"\"
    x = 1
    return x
"""
            temp_file.write(code.encode('utf-8'))
            
        try:
            file_path = Path(temp_file.name)
            
            # We'll test the extraction logic directly
            # by mocking the tree-sitter parser behavior
            with mock.patch('tree_sitter.Parser.parse') as mock_parse, \
                 mock.patch('core.parser.CodeParser._extract_function_info') as mock_extract:
                
                # Mock function extraction to return expected data
                mock_extract.return_value = {
                    "name": "example_function",
                    "line": 2,
                    "end_line": 5,
                    "docstring": "This is a docstring."
                }
                
                # Read the source code for the test
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Mock the parse tree structure
                mock_root_node = mock.MagicMock()
                mock_function_node = mock.MagicMock()
                mock_function_node.type = 'function_definition'
                mock_root_node.children = [mock_function_node]
                
                mock_tree = mock.MagicMock()
                mock_tree.root_node = mock_root_node
                mock_parse.return_value = mock_tree
                
                # Call the parser with our mocked tree-sitter
                result = self.parser._parse_python_with_tree_sitter(source_code, file_path)
                
                # Verify results
                assert len(result["functions"]) == 1
                assert result["functions"][0]["name"] == "example_function"
                assert result["functions"][0]["docstring"] == "This is a docstring."
                
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
    
    def test_parse_large_file(self):
        """Test handling of files exceeding size limit."""
        # Create a temporary file larger than MAX_FILE_SIZE
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            # Write a large file (2MB of data)
            temp_file.write(b"# Large file\n" * 200000)
        
        try:
            # Check that ValueError is raised for large files
            with pytest.raises(ValueError) as excinfo:
                self.parser.parse_file(Path(temp_file.name))
            
            assert "exceeds maximum size limit" in str(excinfo.value)
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
    
    def test_parse_nonexistent_file(self):
        """Test handling of non-existent files."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_file(Path("/nonexistent/file.py"))
    
    def test_extract_docstring(self):
        """Test docstring extraction from different formats."""
        # Mock a node with a triple-quoted docstring
        node = mock.MagicMock()
        block_node = mock.MagicMock()
        string_node = mock.MagicMock()
        
        # Set up the node structure
        node.children = [block_node]
        block_node.type = 'block'
        block_node.children = [string_node]
        string_node.type = 'string'
        
        # Test triple quotes
        source_code = '"""This is a triple-quoted docstring."""'
        with mock.patch('core.parser.CodeParser._get_node_text', return_value=source_code):
            docstring = self.parser._extract_docstring(node, source_code)
            assert docstring == "This is a triple-quoted docstring."
        
        # Test single quotes
        source_code = "'This is a single-quoted docstring.'"
        with mock.patch('core.parser.CodeParser._get_node_text', return_value=source_code):
            docstring = self.parser._extract_docstring(node, source_code)
            assert docstring == "This is a single-quoted docstring."
            
    def test_get_node_text(self):
        """Test extracting text content from a node."""
        # Create a mock node with start and end bytes
        node = mock.MagicMock()
        node.start_byte = 5
        node.end_byte = 10
        
        # Test with a simple source code string
        source_code = "abcdefghijklmn"
        result = self.parser._get_node_text(node, source_code)
        
        # Should extract characters from positions 5 to 10
        assert result == "fghij"
