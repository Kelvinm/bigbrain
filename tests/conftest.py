"""
Pytest configuration file.

This file configures pytest to properly find and import modules from the project.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
# This allows tests to import modules like 'config', 'bridge', 'core', etc.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
