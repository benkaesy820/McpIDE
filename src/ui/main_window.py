#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main window component for McpIDE.
Provides the main application window with docking, menus, and toolbars.
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QToolBar, QStatusBar,
    QWidget, QSplitter, QFileDialog, QMenuBar, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QSettings, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence

from src.ui.file_explorer import FileExplorer
from src.ui.editor import CodeEditor
from src.ui.theme_manager import ThemeManager
from src.ui.welcome_screen import WelcomeScreen
from src.ui.split_view import SplitViewContainer

class MainWindow(QMainWindow):
    """
    Main application window for McpIDE
    """
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        
        # Set window properties
        self.setObjectName("MainWindow")
        self.setWindowTitle("McpIDE")
        self.setMinimumSize(800, 600)
        
        # Create theme manager
        self.theme_manager = ThemeManager(settings)
        
        # Initialize UI components
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_statusbar()
        
        # Connect signals
        self._connect_signals()
        
        # Set object names for all widgets to ensure proper state saving
        self._set_object_names()
        
        # Apply theme
        self.theme_manager.apply_theme(self.settings.get_theme())
        
        # Restore window state if available
        self._restore_window_state()
        
        # Open last workspace if available
        self._open_last_workspace()
        
        # Restore open files
        self._restore_open_files()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout is a splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.central_widget.setLayout(QVBoxLayout())
        self.central_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.central_widget.layout().addWidget(self.main_splitter)
        
        # File explorer dock
        self.file_explorer_dock = QDockWidget("Explorer", self)
        self.file_explorer_dock.setObjectName("file_explorer_dock")
        self.file_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # File explorer
        self.file_explorer = FileExplorer(self.settings, self.theme_manager)
        self.file_explorer_dock.setWidget(self.file_explorer)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_explorer_dock)
        
        # Split view container for editors
        self.split_view_container = SplitViewContainer(self.settings)
        self.main_splitter.addWidget(self.split_view_container)
        
        # Get the editor tabs from the split view container
        self.editor_tabs = next(iter(self.split_view_container.editor_tabs.values()))
        
        # Connect split view container signals
        self.split_view_container.editor_created.connect(self._on_editor_created)
        self.split_view_container.editor_closed.connect(self._on_editor_closed)
        self.split_view_container.current_editor_changed.connect(self._on_current_editor_changed)
        
        # Add welcome tab if needed
        if self.settings.should_show_welcome_screen() and not self.settings.is_welcome_tab_closed():
            self._add_welcome_tab()
    
    def _add_welcome_tab(self):
        """Add a welcome tab to the editor"""
        self.welcome_screen = WelcomeScreen(self.settings, self.theme_manager)
        
        # Connect welcome screen signals
        self.welcome_screen.open_file_requested.connect(self.open_file)
        self.welcome_screen.open_folder_requested.connect(self.open_folder)
        self.welcome_screen.recent_workspace_selected.connect(self._open_recent_workspace)
        
        # Add to the first tab widget in the split view container
        self.editor_tabs.addTab(self.welcome_screen, "Welcome")
    
    def _create_actions(self):
        """Create actions for menus and toolbars"""
        # File actions
        self.new_file_action = QAction("New File", self)
        self.new_file_action.setShortcut(QKeySequence.New)
        
        self.open_file_action = QAction("Open File...", self)
        self.open_file_action.setShortcut(QKeySequence.Open)
        
        self.open_folder_action = QAction("Open Folder...", self)
        self.open_folder_action.setShortcut("Ctrl+Shift+O")
        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        
        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        
        # Edit actions
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        
        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut(QKeySequence.Cut)
        
        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        
        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        
        self.find_action = QAction("Find", self)
        self.find_action.setShortcut(QKeySequence.Find)
        
        # View actions
        self.toggle_explorer_action = QAction("Explorer", self)
        self.toggle_explorer_action.setCheckable(True)
        self.toggle_explorer_action.setChecked(True)
        
        self.split_horizontal_action = QAction("Split Horizontally", self)
        self.split_horizontal_action.setShortcut("Ctrl+\\")
        
        self.split_vertical_action = QAction("Split Vertically", self)
        self.split_vertical_action.setShortcut("Ctrl+Shift+\\")
        
        self.toggle_theme_action = QAction("Toggle Theme", self)
        
        # Help actions
        self.about_action = QAction("About", self)
    
    def _create_menus(self):
        """Create menus for the main window"""
        # Menu bar
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(self.new_file_action)
        self.file_menu.addAction(self.open_file_action)
        self.file_menu.addAction(self.open_folder_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.find_action)
        
        # View menu
        self.view_menu = self.menu_bar.addMenu("View")
        self.view_menu.addAction(self.toggle_explorer_action)
        self.view_menu.addSeparator()
        
        # Editor layout submenu
        self.editor_layout_menu = self.view_menu.addMenu("Editor Layout")
        self.editor_layout_menu.addAction(self.split_horizontal_action)
        self.editor_layout_menu.addAction(self.split_vertical_action)
        
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.toggle_theme_action)
        
        # Help menu
        self.help_menu = self.menu_bar.addMenu("Help")
        self.help_menu.addAction(self.about_action)
    
    def _create_toolbars(self):
        """Create toolbars for the main window"""
        # Main toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setObjectName("main_toolbar")
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(16, 16))
        
        # Add actions to toolbar
        self.main_toolbar.addAction(self.new_file_action)
        self.main_toolbar.addAction(self.open_file_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.undo_action)
        self.main_toolbar.addAction(self.redo_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.toggle_theme_action)
        
        self.addToolBar(self.main_toolbar)
    
    def _create_statusbar(self):
        """Create status bar for the main window"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.cursor_position_label = QLabel("Line: 1, Column: 1")
        self.status_bar.addPermanentWidget(self.cursor_position_label)
        
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        """Connect signals to slots"""
        # File actions
        self.new_file_action.triggered.connect(self.new_file)
        self.open_file_action.triggered.connect(self.open_file)
        self.open_folder_action.triggered.connect(self.open_folder)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.cut_action.triggered.connect(self.cut)
        self.copy_action.triggered.connect(self.copy)
        self.paste_action.triggered.connect(self.paste)
        self.find_action.triggered.connect(self.find)
        
        # View actions
        self.toggle_explorer_action.triggered.connect(self.toggle_explorer)
        self.split_horizontal_action.triggered.connect(self.split_horizontal)
        self.split_vertical_action.triggered.connect(self.split_vertical)
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        
        # Help actions
        self.about_action.triggered.connect(self.show_about)
        
        # File explorer
        self.file_explorer.file_activated.connect(self._open_file)
        
        # Settings
        self.settings.theme_changed.connect(self.theme_manager.apply_theme)
    
    def _set_object_names(self):
        """Set object names for all widgets to ensure proper state saving"""
        # Main window components
        self.file_explorer_dock.setObjectName("file_explorer_dock")
        self.main_toolbar.setObjectName("main_toolbar")
        self.editor_tabs.setObjectName("editor_tabs")
        self.status_bar.setObjectName("status_bar")
        self.menu_bar.setObjectName("menu_bar")
        
        # Menus
        self.file_menu.setObjectName("file_menu")
        self.edit_menu.setObjectName("edit_menu")
        self.view_menu.setObjectName("view_menu")
        self.help_menu.setObjectName("help_menu")
    
    def _restore_window_state(self):
        """Restore window state from settings"""
        try:
            qsettings = QSettings()
            if qsettings.contains("mainwindow/geometry"):
                self.restoreGeometry(qsettings.value("mainwindow/geometry"))
            if qsettings.contains("mainwindow/state"):
                self.restoreState(qsettings.value("mainwindow/state"))
        except Exception as e:
            print(f"Warning: Could not restore window state: {str(e)}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Save window state
            qsettings = QSettings()
            qsettings.setValue("mainwindow/geometry", self.saveGeometry())
            qsettings.setValue("mainwindow/state", self.saveState())
            
            # Save open files
            self._save_open_files()
        except Exception as e:
            print(f"Warning: Could not save window state: {str(e)}")
        
        # Check for unsaved changes in all editors
        editors = self.split_view_container.get_all_editors()
        for editor in editors:
            if hasattr(editor, 'document') and editor.document().isModified():
                file_name = "Untitled"
                if hasattr(editor, 'file_path') and editor.file_path:
                    file_name = os.path.basename(editor.file_path)
                
                response = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"There are unsaved changes in '{file_name}'. Do you want to save them before closing?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if response == QMessageBox.Save:
                    # Make this editor the current one
                    self.split_view_container.add_editor(editor, file_name)
                    if not self.save_file():
                        event.ignore()
                        return
                elif response == QMessageBox.Cancel:
                    event.ignore()
                    return
        
        event.accept()
    
    @Slot()
    def new_file(self):
        """Create a new file"""
        editor = CodeEditor(self.settings, self.theme_manager)
        
        # Connect editor signals
        editor.cursor_position_changed.connect(self._update_cursor_position)
        
        # Add to split view container
        self.split_view_container.add_editor(editor, "Untitled")
    
    @Slot()
    def open_file(self):
        """Open a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        
        if file_path:
            self._open_file(file_path)
    
    def _open_file(self, file_path):
        """Open a file in the editor"""
        # Validate file path
        if not file_path or not os.path.exists(file_path) or not os.path.isfile(file_path):
            QMessageBox.critical(self, "Error", f"File does not exist: {file_path}")
            return
            
        # Check if file is already open
        editor = self.split_view_container.get_editor_by_path(file_path)
        if editor:
            # Find the tab widget containing this editor
            for tab_id, tabs in self.split_view_container.editor_tabs.items():
                for i in range(tabs.count()):
                    if tabs.widget(i) == editor:
                        tabs.setCurrentIndex(i)
                        return
        
        # Create a new editor
        editor = CodeEditor(self.settings, self.theme_manager)
        
        # Connect editor signals
        editor.cursor_position_changed.connect(self._update_cursor_position)
        
        # Load the file
        if editor.load_file(file_path):
            file_name = os.path.basename(file_path)
            self.split_view_container.add_editor(editor, file_name)
            self.status_bar.showMessage(f"Opened {file_path}")
        else:
            QMessageBox.critical(self, "Error", f"Could not open file: {file_path}")
    
    @Slot()
    def open_folder(self):
        """Open a folder as workspace"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Open Folder", ""
        )
        
        if folder_path:
            self._open_workspace(folder_path)
    
    def _open_workspace(self, folder_path):
        """Open a workspace folder"""
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            self.file_explorer.set_root_path(folder_path)
            self.settings.add_recent_workspace(folder_path)
            self.status_bar.showMessage(f"Opened workspace: {folder_path}")
            self.setWindowTitle(f"McpIDE - {folder_path}")
    
    def _open_recent_workspace(self, folder_path):
        """Open a recent workspace"""
        self._open_workspace(folder_path)
    
    def _open_last_workspace(self):
        """Open the last workspace if available"""
        last_workspace = self.settings.get_last_workspace()
        if last_workspace and os.path.exists(last_workspace) and os.path.isdir(last_workspace):
            self._open_workspace(last_workspace)
    
    @Slot()
    def save_file(self):
        """Save the current file"""
        editor = self.split_view_container.get_current_editor()
        if not editor:
            return False
            
        if not hasattr(editor, 'file_path') or not editor.file_path:
            return self.save_file_as()
        
        if editor.save_file():
            # Update tab title to remove unsaved indicator
            for tab_id, tabs in self.split_view_container.editor_tabs.items():
                index = tabs.indexOf(editor)
                if index >= 0:
                    current_text = tabs.tabText(index)
                    if current_text.endswith('*'):
                        tabs.setTabText(index, current_text[:-1])
            
            self.status_bar.showMessage(f"Saved {editor.file_path}")
            return True
        else:
            QMessageBox.critical(self, "Error", f"Could not save file")
            return False
    
    @Slot()
    def save_file_as(self):
        """Save the current file with a new name"""
        editor = self.split_view_container.get_current_editor()
        if not editor:
            return False
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "All Files (*)"
        )
        
        if file_path:
            if editor.save_file(file_path):
                # Update tab title
                for tab_id, tabs in self.split_view_container.editor_tabs.items():
                    index = tabs.indexOf(editor)
                    if index >= 0:
                        tabs.setTabText(index, os.path.basename(file_path))
                
                self.status_bar.showMessage(f"Saved {file_path}")
                return True
            else:
                QMessageBox.critical(self, "Error", f"Could not save file")
                return False
        return False
    
    @Slot()
    def undo(self):
        """Undo the last action"""
        editor = self.split_view_container.get_current_editor()
        if editor:
            editor.undo()
    
    @Slot()
    def redo(self):
        """Redo the last undone action"""
        editor = self.split_view_container.get_current_editor()
        if editor:
            editor.redo()
    
    @Slot()
    def cut(self):
        """Cut selected text"""
        editor = self.split_view_container.get_current_editor()
        if editor:
            editor.cut()
    
    @Slot()
    def copy(self):
        """Copy selected text"""
        editor = self.split_view_container.get_current_editor()
        if editor:
            editor.copy()
    
    @Slot()
    def paste(self):
        """Paste text from clipboard"""
        editor = self.split_view_container.get_current_editor()
        if editor:
            editor.paste()
    
    @Slot()
    def find(self):
        """Find text in the current editor"""
        # TODO: Implement find dialog
        pass
    
    @Slot()
    def toggle_explorer(self):
        """Toggle file explorer visibility"""
        self.file_explorer_dock.setVisible(not self.file_explorer_dock.isVisible())
        self.toggle_explorer_action.setChecked(self.file_explorer_dock.isVisible())
    
    @Slot()
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        current_theme = self.settings.get_theme()
        new_theme = "light" if current_theme == "dark" else "dark"
        self.settings.set_theme(new_theme)
    
    @Slot()
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About McpIDE",
            "McpIDE - A VS Code-inspired IDE with MCP integration\n\n"
            "Version: 0.1.0\n"
            "© 2024 McpIDE Team"
        )
    
    @Slot(int, int)
    def _update_cursor_position(self, line, column):
        """Update cursor position in status bar"""
        self.cursor_position_label.setText(f"Line: {line}, Column: {column}")
    
    @Slot()
    def split_horizontal(self):
        """Split the editor view horizontally"""
        self.split_view_container.split_horizontally()
    
    @Slot()
    def split_vertical(self):
        """Split the editor view vertically"""
        self.split_view_container.split_vertically()
    
    @Slot(object)
    def _on_editor_created(self, editor):
        """Handle editor created signal from split view container"""
        # This is called when a new editor is created in any split
        pass
    
    @Slot(object)
    def _on_editor_closed(self, editor):
        """Handle editor closed signal from split view container"""
        # This is called when an editor is closed in any split
        pass
    
    @Slot(object)
    def _on_current_editor_changed(self, editor):
        """Handle current editor changed signal from split view container"""
        # Update UI based on the current editor
        if editor and hasattr(editor, 'cursor_position_changed'):
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self._update_cursor_position(line, column)
    
    def _save_open_files(self):
        """Save the list of open files"""
        open_files = []
        has_welcome_tab = False
        
        for tab_id, tabs in self.split_view_container.editor_tabs.items():
            for i in range(tabs.count()):
                widget = tabs.widget(i)
                tab_text = tabs.tabText(i)
                
                # Check if welcome tab is still open
                if tab_text == "Welcome":
                    has_welcome_tab = True
                    continue
                    
                if hasattr(widget, 'file_path') and widget.file_path and os.path.exists(widget.file_path):
                    open_files.append(widget.file_path)
        
        # Update welcome tab status
        self.settings.set_welcome_tab_closed(not has_welcome_tab)
        
        # Save open files
        qsettings = QSettings()
        qsettings.setValue("editor/open_files", open_files)
    
    def _restore_open_files(self):
        """Restore previously open files"""
        qsettings = QSettings()
        open_files = qsettings.value("editor/open_files", [])
        
        if open_files:
            for file_path in open_files:
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    self._open_file(file_path)
