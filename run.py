#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
McpIDE - A VS Code-inspired IDE with future support for MCP
"""

import sys
import os

# Make sure we can import from src
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Run the application
from src.main import main

if __name__ == "__main__":
    main()
