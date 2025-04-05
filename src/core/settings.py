#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtCore import QSettings, QObject, Signal, Slot

class Settings(QObject):
    """
    Class to manage application settings with signals for changes
    """
    # Signals
    theme_changed = Signal(str)
    recent_workspaces_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.settings = QSettings()

        # Default settings
        self._default_settings = {
            "theme": "dark",
            "recent_workspaces": [],
            "last_workspace": "",
            "show_welcome_screen": True,
            "welcome_tab_closed": False,
            "font_family": "Consolas",
            "font_size": 12,
            "tab_size": 4,
            "use_spaces": True,
            "show_line_numbers": True,
            "word_wrap": False
        }

        # Initialize settings with defaults if they don't exist
        for key, value in self._default_settings.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)

    def get_theme(self):
        """Get the current theme (dark or light)"""
        return self.settings.value("theme", "dark")

    def set_theme(self, theme):
        """Set the theme and emit signal"""
        if theme in ["dark", "light"]:
            self.settings.setValue("theme", theme)
            self.theme_changed.emit(theme)

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

    def get_font_family(self):
        """Get the editor font family"""
        return self.settings.value("font_family", "Consolas")

    def get_font_size(self):
        """Get the editor font size"""
        return int(self.settings.value("font_size", 12))

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

    def set_setting(self, key, value):
        """Generic method to set a setting"""
        if key in self._default_settings:
            self.settings.setValue(key, value)

            # Emit specific signals for certain settings
            if key == "theme":
                self.theme_changed.emit(value)
            elif key == "recent_workspaces":
                self.recent_workspaces_changed.emit(value)

    def get_setting(self, key, default=None):
        """Generic method to get a setting"""
        if default is None and key in self._default_settings:
            default = self._default_settings[key]
        return self.settings.value(key, default)

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
