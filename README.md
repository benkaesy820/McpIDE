# McpIDE

A VS Code-inspired IDE with integrated support for the Model Context Protocol (MCP) and other productivity tools for software engineers and knowledge workers.

## About McpIDE

McpIDE is designed to be an all-in-one development environment that combines the familiar VS Code experience with powerful integrations for AI and productivity tools. At its core, McpIDE supports the Model Context Protocol (MCP), enabling seamless interaction between your development environment and AI assistants like Claude.

## Features

### Implemented
- Modern UI with dark/light mode switching
- File explorer with context menu actions (new file, rename, delete)
- Workspace management with recent workspaces list
- Advanced code editing with:
  - Line numbers
  - Auto-indentation
  - Unsaved changes tracking
  - Context menu
  - Cursor position tracking
  - Compatibility with different PySide6 versions
- Settings management with local storage
- Session persistence:
  - Last workspace memory (reopens your last project)
  - Remembers open files between sessions
  - Preserves window layout and state
- Improved error handling for file operations

### Planned
- Model Context Protocol (MCP) Integration:
  - MCP server capabilities for exposing codebase as resources
  - AI assistant integration for code understanding and generation
  - Tools for code analysis, refactoring, and documentation
- Advanced Development Features:
  - Syntax highlighting for various languages
  - Search functionality with AI-powered natural language queries
  - Terminal integration
  - Markdown preview for documentation
  - Split editor views
- Productivity Enhancements:
  - Code snippets management
  - AI-assisted code completion
  - Project templates and boilerplate generation

## Development

This project is being developed iteratively. See the [Development Plan](docs/development_plan.md) for details.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It enables seamless communication between development environments like McpIDE and AI assistants, allowing the AI to understand your codebase and provide intelligent assistance.

Learn more about MCP at [modelcontextprotocol.io](https://modelcontextprotocol.io/introduction).

## Requirements

- Python 3.10+ (recommended, 3.12 is the latest stable version)
- PySide6 6.5.0+ (compatible with Python 3.10-3.13)
- QScintilla 2.14.0+
- Pygments 2.15.0+

Note: The specific versions of these dependencies may need to be adjusted based on compatibility with your Python version. See the requirements.txt file for the exact versions used in development.

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python src/main.py`

## License

[MIT](LICENSE)
