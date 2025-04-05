#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application settings management for McpIDE.
Handles persistent settings storage and provides signals for settings changes.
"""

from PySide6.QtCore import QSettings, QObject, Signal, Slot

class AppSettings(QObject):
    """
    Class to manage application settings with signals for changes
    """
    # Signals
    theme_changed = Signal(str)
    recent_workspaces_changed = Signal(list)
    editor_font_changed = Signal(str, int)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        
        # Default settings
        self._default_settings = {
            # Appearance
            "theme": "dark",
            "icon_theme": "default",
            
            # Workspace
            "recent_workspaces": [],
            "last_workspace": "",
            "show_welcome_screen": True,
            "welcome_tab_closed": False,
            
            # Editor
            "font_family": "Consolas",
            "font_size": 12,
            "tab_size": 4,
            "use_spaces": True,
            "show_line_numbers": True,
            "word_wrap": False,
            "auto_save": False,
            "auto_save_interval": 30000,  # 30 seconds
            
            # UI
            "show_status_bar": True,
            "show_menu_bar": True,
            "show_activity_bar": True,
            "editor_layout": "single",  # single, split-horizontal, split-vertical
            
            # Terminal
            "terminal_shell": "",  # Empty for system default
            "terminal_font_family": "Consolas",
            "terminal_font_size": 12,
            
            # MCP
            "mcp_enabled": True,
            "mcp_server_port": 9000,
            "mcp_expose_resources": True,
            "mcp_tools_enabled": True
        }
        
        # Initialize settings with defaults if they don't exist
        for key, value in self._default_settings.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)
    
    # Theme settings
    def get_theme(self):
        """Get the current theme (dark or light)"""
        return self.settings.value("theme", "dark")
    
    def set_theme(self, theme):
        """Set the theme and emit signal"""
        if theme in ["dark", "light"]:
            self.settings.setValue("theme", theme)
            self.theme_changed.emit(theme)
    
    # Workspace settings
    def get_recent_workspaces(self):
        """Get list of recent workspaces"""
        return self.settings.value("recent_workspaces", [])
    
    def add_recent_workspace(self, workspace_path):
        """Add a workspace to recent workspaces and set as last workspace"""
        workspaces = self.get_recent_workspaces()
        
        # Remove if already exists (to move to front)
        if workspace_path in workspaces:
            workspaces.remove(workspace_path)
        
        # Add to front of list
        workspaces.insert(0, workspace_path)
        
        # Keep only the 10 most recent
        workspaces = workspaces[:10]
        
        # Save and emit signal
        self.settings.setValue("recent_workspaces", workspaces)
        self.settings.setValue("last_workspace", workspace_path)
        self.settings.setValue("show_welcome_screen", False)
        self.recent_workspaces_changed.emit(workspaces)
    
    def get_last_workspace(self):
        """Get the last opened workspace"""
        return self.settings.value("last_workspace", "")
    
    def should_show_welcome_screen(self):
        """Check if welcome screen should be shown"""
        return bool(self.settings.value("show_welcome_screen", True))
    
    def set_show_welcome_screen(self, show):
        """Set whether to show welcome screen"""
        self.settings.setValue("show_welcome_screen", bool(show))
    
    def is_welcome_tab_closed(self):
        """Check if welcome tab was closed in previous session"""
        return bool(self.settings.value("welcome_tab_closed", False))
    
    def set_welcome_tab_closed(self, closed):
        """Set whether welcome tab is closed"""
        self.settings.setValue("welcome_tab_closed", bool(closed))
    
    # Editor settings
    def get_font_family(self):
        """Get the editor font family"""
        return self.settings.value("font_family", "Consolas")
    
    def get_font_size(self):
        """Get the editor font size"""
        return int(self.settings.value("font_size", 12))
    
    def set_editor_font(self, family, size):
        """Set the editor font and emit signal"""
        self.settings.setValue("font_family", family)
        self.settings.setValue("font_size", size)
        self.editor_font_changed.emit(family, size)
    
    def get_tab_size(self):
        """Get the editor tab size"""
        return int(self.settings.value("tab_size", 4))
    
    def get_use_spaces(self):
        """Get whether to use spaces instead of tabs"""
        return bool(self.settings.value("use_spaces", True))
    
    def get_show_line_numbers(self):
        """Get whether to show line numbers"""
        return bool(self.settings.value("show_line_numbers", True))
    
    def get_word_wrap(self):
        """Get whether to wrap words"""
        return bool(self.settings.value("word_wrap", False))
    
    def get_auto_save(self):
        """Get whether auto-save is enabled"""
        return bool(self.settings.value("auto_save", False))
    
    def get_auto_save_interval(self):
        """Get auto-save interval in milliseconds"""
        return int(self.settings.value("auto_save_interval", 30000))
    
    # UI settings
    def get_editor_layout(self):
        """Get the editor layout"""
        return self.settings.value("editor_layout", "single")
    
    def set_editor_layout(self, layout):
        """Set the editor layout"""
        if layout in ["single", "split-horizontal", "split-vertical"]:
            self.settings.setValue("editor_layout", layout)
    
    # MCP settings
    def is_mcp_enabled(self):
        """Check if MCP is enabled"""
        return bool(self.settings.value("mcp_enabled", True))
    
    def get_mcp_server_port(self):
        """Get the MCP server port"""
        return int(self.settings.value("mcp_server_port", 9000))
    
    # Generic settings methods
    def set_setting(self, key, value):
        """Generic method to set a setting"""
        if key in self._default_settings:
            self.settings.setValue(key, value)
            
            # Emit specific signals for certain settings
            if key == "theme":
                self.theme_changed.emit(value)
            elif key == "recent_workspaces":
                self.recent_workspaces_changed.emit(value)
            elif key in ["font_family", "font_size"]:
                self.editor_font_changed.emit(
                    self.get_font_family(), 
                    self.get_font_size()
                )
    
    def get_setting(self, key, default=None):
        """Generic method to get a setting"""
        if default is None and key in self._default_settings:
            default = self._default_settings[key]
        return self.settings.value(key, default)
