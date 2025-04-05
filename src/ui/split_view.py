#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Split view container component for McpIDE.
Allows splitting the editor area horizontally or vertically.
"""

from PySide6.QtWidgets import (
    QWidget, QSplitter, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTabWidget, QMenu, QToolButton
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QAction

from src.ui.editor import CodeEditor

class SplitViewContainer(QWidget):
    """
    Container widget that manages split views of editors.
    Allows horizontal and vertical splitting.
    """
    # Signals
    editor_created = Signal(CodeEditor)  # Emitted when a new editor is created
    editor_closed = Signal(CodeEditor)   # Emitted when an editor is closed
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.main_splitter = None
        self.editor_tabs = {}  # Dictionary to track editor tab widgets
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.main_splitter)
        
        # Create initial editor tabs
        self._create_editor_tabs()
    
    def _create_editor_tabs(self, parent_splitter=None, orientation=Qt.Horizontal):
        """Create a new editor tab widget"""
        if parent_splitter is None:
            parent_splitter = self.main_splitter
            
        # Create tab widget
        tabs = QTabWidget()
        tabs.setTabsClosable(True)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)
        
        # Add tab widget to splitter
        parent_splitter.addWidget(tabs)
        
        # Connect signals
        tabs.tabCloseRequested.connect(lambda index: self._on_tab_close_requested(tabs, index))
        
        # Add to tracking dictionary
        self.editor_tabs[id(tabs)] = tabs
        
        # Add context menu for tabs
        tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        tabs.customContextMenuRequested.connect(lambda pos: self._show_tab_context_menu(tabs, pos))
        
        return tabs
    
    def split_horizontally(self, tab_widget=None):
        """Split the view horizontally"""
        if tab_widget is None:
            # Use the currently active tab widget
            tab_widget = self._get_active_tab_widget()
            if tab_widget is None:
                return
        
        # Get the parent splitter
        parent = tab_widget.parent()
        if not isinstance(parent, QSplitter):
            return
            
        # Check if we need to change orientation
        if parent.orientation() != Qt.Vertical:
            # Create a new splitter with vertical orientation
            new_splitter = QSplitter(Qt.Vertical)
            
            # Get the index of the tab widget in its parent
            index = parent.indexOf(tab_widget)
            
            # Remove the tab widget from its parent
            tab_widget.setParent(None)
            
            # Add the new splitter to the parent at the same index
            parent.insertWidget(index, new_splitter)
            
            # Add the tab widget to the new splitter
            new_splitter.addWidget(tab_widget)
            
            # Create a new tab widget and add it to the new splitter
            new_tabs = self._create_editor_tabs(new_splitter, Qt.Vertical)
        else:
            # Parent already has the right orientation, just add a new tab widget
            new_tabs = self._create_editor_tabs(parent, Qt.Vertical)
        
        # Set equal sizes
        parent.setSizes([parent.size().height() // 2] * parent.count())
        
        return new_tabs
    
    def split_vertically(self, tab_widget=None):
        """Split the view vertically"""
        if tab_widget is None:
            # Use the currently active tab widget
            tab_widget = self._get_active_tab_widget()
            if tab_widget is None:
                return
        
        # Get the parent splitter
        parent = tab_widget.parent()
        if not isinstance(parent, QSplitter):
            return
            
        # Check if we need to change orientation
        if parent.orientation() != Qt.Horizontal:
            # Create a new splitter with horizontal orientation
            new_splitter = QSplitter(Qt.Horizontal)
            
            # Get the index of the tab widget in its parent
            index = parent.indexOf(tab_widget)
            
            # Remove the tab widget from its parent
            tab_widget.setParent(None)
            
            # Add the new splitter to the parent at the same index
            parent.insertWidget(index, new_splitter)
            
            # Add the tab widget to the new splitter
            new_splitter.addWidget(tab_widget)
            
            # Create a new tab widget and add it to the new splitter
            new_tabs = self._create_editor_tabs(new_splitter, Qt.Horizontal)
        else:
            # Parent already has the right orientation, just add a new tab widget
            new_tabs = self._create_editor_tabs(parent, Qt.Horizontal)
        
        # Set equal sizes
        parent.setSizes([parent.size().width() // 2] * parent.count())
        
        return new_tabs
    
    def _get_active_tab_widget(self):
        """Get the currently active tab widget"""
        # Find the tab widget that has focus
        for tab_id, tabs in self.editor_tabs.items():
            if tabs.hasFocus() or tabs.currentWidget() and tabs.currentWidget().hasFocus():
                return tabs
        
        # If none has focus, return the first one
        if self.editor_tabs:
            return next(iter(self.editor_tabs.values()))
        
        return None
    
    def _on_tab_close_requested(self, tab_widget, index):
        """Handle tab close request"""
        # Get the widget at the index
        widget = tab_widget.widget(index)
        
        # Check if it's an editor with unsaved changes
        if hasattr(widget, 'file_path') and hasattr(widget, 'document') and widget.document().isModified():
            # TODO: Handle unsaved changes
            pass
        
        # Remove the tab
        tab_widget.removeTab(index)
        
        # Emit signal
        if isinstance(widget, CodeEditor):
            self.editor_closed.emit(widget)
        
        # Check if this tab widget is now empty
        if tab_widget.count() == 0:
            # Get the parent splitter
            parent = tab_widget.parent()
            if isinstance(parent, QSplitter) and parent.count() > 1:
                # Remove this tab widget
                tab_widget.setParent(None)
                tab_widget.deleteLater()
                
                # Remove from tracking dictionary
                if id(tab_widget) in self.editor_tabs:
                    del self.editor_tabs[id(tab_widget)]
                
                # If the parent splitter now has only one child, collapse it
                if parent.count() == 1 and parent != self.main_splitter:
                    # Get the grandparent
                    grandparent = parent.parent()
                    if isinstance(grandparent, QSplitter):
                        # Get the remaining widget
                        remaining = parent.widget(0)
                        
                        # Get the index of the parent in the grandparent
                        index = grandparent.indexOf(parent)
                        
                        # Remove the parent from the grandparent
                        parent.setParent(None)
                        
                        # Add the remaining widget to the grandparent at the same index
                        grandparent.insertWidget(index, remaining)
                        
                        # Delete the parent
                        parent.deleteLater()
    
    def _show_tab_context_menu(self, tab_widget, position):
        """Show context menu for tab widget"""
        menu = QMenu()
        
        # Add actions
        split_h_action = QAction("Split Horizontally", self)
        split_h_action.triggered.connect(lambda: self.split_horizontally(tab_widget))
        menu.addAction(split_h_action)
        
        split_v_action = QAction("Split Vertically", self)
        split_v_action.triggered.connect(lambda: self.split_vertically(tab_widget))
        menu.addAction(split_v_action)
        
        # Only add close split action if there's more than one tab widget
        if len(self.editor_tabs) > 1:
            menu.addSeparator()
            close_split_action = QAction("Close Split", self)
            close_split_action.triggered.connect(lambda: self._close_split(tab_widget))
            menu.addAction(close_split_action)
        
        # Show the menu
        menu.exec_(tab_widget.mapToGlobal(position))
    
    def _close_split(self, tab_widget):
        """Close a split view"""
        # Get the parent splitter
        parent = tab_widget.parent()
        if not isinstance(parent, QSplitter):
            return
            
        # Check if there are any tabs with unsaved changes
        for i in range(tab_widget.count()):
            widget = tab_widget.widget(i)
            if hasattr(widget, 'document') and widget.document().isModified():
                # TODO: Handle unsaved changes
                pass
        
        # Move all tabs to another tab widget
        target_tab_widget = None
        for tab_id, tabs in self.editor_tabs.items():
            if tabs != tab_widget:
                target_tab_widget = tabs
                break
        
        if target_tab_widget:
            # Move all tabs to the target
            while tab_widget.count() > 0:
                widget = tab_widget.widget(0)
                text = tab_widget.tabText(0)
                tab_widget.removeTab(0)
                index = target_tab_widget.addTab(widget, text)
                target_tab_widget.setCurrentIndex(index)
        
        # Remove this tab widget
        tab_widget.setParent(None)
        tab_widget.deleteLater()
        
        # Remove from tracking dictionary
        if id(tab_widget) in self.editor_tabs:
            del self.editor_tabs[id(tab_widget)]
        
        # If the parent splitter now has only one child, collapse it
        if parent.count() == 1 and parent != self.main_splitter:
            # Get the grandparent
            grandparent = parent.parent()
            if isinstance(grandparent, QSplitter):
                # Get the remaining widget
                remaining = parent.widget(0)
                
                # Get the index of the parent in the grandparent
                index = grandparent.indexOf(parent)
                
                # Remove the parent from the grandparent
                parent.setParent(None)
                
                # Add the remaining widget to the grandparent at the same index
                grandparent.insertWidget(index, remaining)
                
                # Delete the parent
                parent.deleteLater()
    
    def add_editor(self, editor, title, tab_widget=None):
        """Add an editor to a tab widget"""
        if tab_widget is None:
            tab_widget = self._get_active_tab_widget()
            if tab_widget is None:
                # Create a new tab widget if none exists
                tab_widget = self._create_editor_tabs()
        
        # Add the editor to the tab widget
        index = tab_widget.addTab(editor, title)
        tab_widget.setCurrentIndex(index)
        
        # Emit signal
        self.editor_created.emit(editor)
        
        return index
    
    def get_all_editors(self):
        """Get all editor widgets"""
        editors = []
        for tab_id, tabs in self.editor_tabs.items():
            for i in range(tabs.count()):
                widget = tabs.widget(i)
                if isinstance(widget, CodeEditor):
                    editors.append(widget)
        return editors
    
    def get_current_editor(self):
        """Get the currently active editor"""
        tab_widget = self._get_active_tab_widget()
        if tab_widget:
            widget = tab_widget.currentWidget()
            if isinstance(widget, CodeEditor):
                return widget
        return None
