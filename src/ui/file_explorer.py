#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File explorer component for McpIDE.
Provides a tree view of files and directories with context menu actions.
"""

import os
from PySide6.QtWidgets import (
    QTreeView, QFileSystemModel, QVBoxLayout, QWidget,
    QLineEdit, QMenu, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QDir, Signal, Slot, QModelIndex, QSize
from PySide6.QtGui import QAction, QKeySequence

class FileExplorer(QWidget):
    """
    File explorer widget for browsing and managing files
    """
    file_activated = Signal(str)  # Emitted when a file is activated (double-clicked)
    
    def __init__(self, settings, theme_manager):
        super().__init__()
        self.settings = settings
        self.theme_manager = theme_manager
        self.current_path = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files...")
        self.layout.addWidget(self.search_box)
        
        # File system model
        self.model = QFileSystemModel()
        self.model.setReadOnly(False)
        
        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Hide unnecessary columns
        self.tree_view.setHeaderHidden(True)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)
        
        self.layout.addWidget(self.tree_view)
    
    def _connect_signals(self):
        """Connect signals to slots"""
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.search_box.textChanged.connect(self._filter_files)
        
        # Connect theme change
        self.settings.theme_changed.connect(self._on_theme_changed)
    
    def set_root_path(self, path):
        """Set the root path for the file explorer"""
        if os.path.exists(path):
            self.current_path = path
            index = self.model.setRootPath(path)
            self.tree_view.setRootIndex(index)
    
    @Slot(QModelIndex)
    def _on_item_double_clicked(self, index):
        """Handle double-click on an item"""
        path = self.model.filePath(index)
        if os.path.isfile(path):
            try:
                # Make sure the file exists and is readable
                with open(path, 'r', encoding='utf-8') as _:
                    pass
                self.file_activated.emit(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    @Slot(str)
    def _filter_files(self, text):
        """Filter files based on search text"""
        if not text:
            self.model.setNameFilters([])
        else:
            self.model.setNameFilters([f"*{text}*"])
        self.model.setNameFilterDisables(False)
    
    @Slot(object)
    def _show_context_menu(self, position):
        """Show context menu for file explorer"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return
        
        path = self.model.filePath(index)
        is_dir = os.path.isdir(path)
        
        menu = QMenu()
        
        # Common actions
        open_action = QAction("Open" if not is_dir else "Open Folder", self)
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        
        # Directory-specific actions
        new_file_action = None
        new_folder_action = None
        if is_dir:
            new_file_action = QAction("New File", self)
            new_folder_action = QAction("New Folder", self)
            menu.addAction(new_file_action)
            menu.addAction(new_folder_action)
            menu.addSeparator()
        
        menu.addAction(open_action)
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        
        # Show menu and handle action
        action = menu.exec_(self.tree_view.viewport().mapToGlobal(position))
        
        if action == open_action:
            if is_dir:
                self.set_root_path(path)
            else:
                self.file_activated.emit(path)
        elif action == rename_action:
            self._rename_item(index)
        elif action == delete_action:
            self._delete_item(index)
        elif new_file_action and action == new_file_action:
            self._create_new_file(path)
        elif new_folder_action and action == new_folder_action:
            self._create_new_folder(path)
    
    def _rename_item(self, index):
        """Rename a file or folder"""
        path = self.model.filePath(index)
        name = os.path.basename(path)
        parent_dir = os.path.dirname(path)
        
        new_name, ok = QInputDialog.getText(
            self, "Rename", "New name:", text=name
        )
        
        if ok and new_name:
            new_path = os.path.join(parent_dir, new_name)
            try:
                os.rename(path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename: {str(e)}")
    
    def _delete_item(self, index):
        """Delete a file or folder"""
        path = self.model.filePath(index)
        name = os.path.basename(path)
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(f"Are you sure you want to delete '{name}'?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete: {str(e)}")
    
    def _create_new_file(self, directory):
        """Create a new file in the specified directory"""
        file_name, ok = QInputDialog.getText(
            self, "New File", "File name:"
        )
        
        if ok and file_name:
            file_path = os.path.join(directory, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                self.file_activated.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file: {str(e)}")
    
    def _create_new_folder(self, directory):
        """Create a new folder in the specified directory"""
        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Folder name:"
        )
        
        if ok and folder_name:
            folder_path = os.path.join(directory, folder_name)
            try:
                os.makedirs(folder_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create folder: {str(e)}")
    
    @Slot(str)
    def _on_theme_changed(self, theme):
        """Handle theme change"""
        # Update tree view styling
        pass
