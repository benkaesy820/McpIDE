#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
McpIDE - A VS Code-inspired IDE with integrated support for the Model Context Protocol (MCP)
and other productivity tools for software engineers and knowledge workers.

This is the main entry point for the application.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.core.settings import Settings
from src.ui.main_window import MainWindow

def main():
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("McpIDE")
    app.setOrganizationName("McpIDE")
    app.setOrganizationDomain("mcpide.org")

    # Initialize settings
    settings = Settings()

    # Create and show the main window
    window = MainWindow(settings)
    window.show()

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
