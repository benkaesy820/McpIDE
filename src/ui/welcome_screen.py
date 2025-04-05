#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon

class WelcomeScreen(QWidget):
    """
    Welcome screen widget shown when the application starts
    """
    open_file_requested = Signal()
    open_folder_requested = Signal()
    recent_workspace_selected = Signal(str)
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        
        self._setup_ui()
        self._connect_signals()
        self._load_recent_workspaces()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel("Welcome to McpIDE")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("A VS Code-inspired IDE with future support for MCP")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.subtitle_label)
        
        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.separator)
        
        # Content layout
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        # Left side - Actions
        self.actions_layout = QVBoxLayout()
        self.actions_layout.setContentsMargins(10, 10, 10, 10)
        self.actions_layout.setSpacing(10)
        
        self.actions_label = QLabel("Start")
        actions_font = QFont()
        actions_font.setPointSize(14)
        actions_font.setBold(True)
        self.actions_label.setFont(actions_font)
        self.actions_layout.addWidget(self.actions_label)
        
        self.new_file_button = QPushButton("New File")
        self.open_file_button = QPushButton("Open File...")
        self.open_folder_button = QPushButton("Open Folder...")
        
        self.actions_layout.addWidget(self.new_file_button)
        self.actions_layout.addWidget(self.open_file_button)
        self.actions_layout.addWidget(self.open_folder_button)
        self.actions_layout.addStretch()
        
        # Right side - Recent
        self.recent_layout = QVBoxLayout()
        self.recent_layout.setContentsMargins(10, 10, 10, 10)
        self.recent_layout.setSpacing(10)
        
        self.recent_label = QLabel("Recent")
        self.recent_label.setFont(actions_font)
        self.recent_layout.addWidget(self.recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.setAlternatingRowColors(True)
        self.recent_layout.addWidget(self.recent_list)
        
        # Add layouts to content
        self.content_layout.addLayout(self.actions_layout)
        self.content_layout.addLayout(self.recent_layout)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        self.open_file_button.clicked.connect(self.open_file_requested.emit)
        self.open_folder_button.clicked.connect(self.open_folder_requested.emit)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_item_double_clicked)
        
        # Connect settings signals
        self.settings.recent_workspaces_changed.connect(self._load_recent_workspaces)
        self.settings.theme_changed.connect(self._on_theme_changed)
    
    def _load_recent_workspaces(self):
        """Load recent workspaces from settings"""
        self.recent_list.clear()
        
        workspaces = self.settings.get_recent_workspaces()
        if not workspaces:
            self.recent_list.addItem("No recent workspaces")
            return
        
        for workspace in workspaces:
            item = QListWidgetItem(workspace)
            item.setData(Qt.UserRole, workspace)
            self.recent_list.addItem(item)
    
    @Slot(QListWidgetItem)
    def _on_recent_item_double_clicked(self, item):
        """Handle double-click on a recent workspace item"""
        workspace_path = item.data(Qt.UserRole)
        if workspace_path:
            self.recent_workspace_selected.emit(workspace_path)
    
    @Slot(str)
    def _on_theme_changed(self, theme):
        """Handle theme change"""
        # Update UI based on theme if needed
        pass
