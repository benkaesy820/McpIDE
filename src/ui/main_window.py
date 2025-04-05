#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QTabWidget, QToolBar, QStatusBar,
    QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QFileDialog,
    QMenu, QMenuBar, QMessageBox
)
from PySide6.QtGui import QIcon, QKeySequence, QAction
from PySide6.QtCore import Qt, QSize, QSettings, Slot


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
        self.theme_manager = ThemeManager(settings)

        # Set window properties
        self.setObjectName("MainWindow")
        self.setWindowTitle("McpIDE")
        self.setMinimumSize(800, 600)

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
        """Set up the main UI components"""
        # Central widget with splitter
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.main_splitter)

        # File explorer dock
        self.file_explorer_dock = QDockWidget("Explorer", self)
        self.file_explorer_dock.setObjectName("file_explorer_dock")
        self.file_explorer_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.file_explorer = FileExplorer(self.settings)
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

        # Add welcome tab if needed
        if self.settings.should_show_welcome_screen() and not self.settings.is_welcome_tab_closed():
            self._add_welcome_tab()

    def _add_welcome_tab(self):
        """Add a welcome tab to the editor"""
        self.welcome_screen = WelcomeScreen(self.settings)

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
        """Create the application menus"""
        # Main menu bar
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
        """Create the application toolbars"""
        # Main toolbar
        self.main_toolbar = QToolBar("Main Toolbar")
        self.main_toolbar.setObjectName("main_toolbar")
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.main_toolbar)

        # Add actions to toolbar
        self.main_toolbar.addAction(self.new_file_action)
        self.main_toolbar.addAction(self.open_file_action)
        self.main_toolbar.addAction(self.save_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.undo_action)
        self.main_toolbar.addAction(self.redo_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.toggle_theme_action)

    def _create_statusbar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
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

        # View actions
        self.toggle_explorer_action.triggered.connect(self.toggle_explorer)
        self.split_horizontal_action.triggered.connect(self.split_horizontal)
        self.split_vertical_action.triggered.connect(self.split_vertical)
        self.toggle_theme_action.triggered.connect(self.toggle_theme)

        # Help actions
        self.about_action.triggered.connect(self.show_about)

        # Editor tabs
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)

        # Settings
        self.settings.theme_changed.connect(self.theme_manager.apply_theme)

        # File explorer
        self.file_explorer.file_activated.connect(self._open_file)

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

        # Check for unsaved changes in all tabs
        for i in range(self.editor_tabs.count()):
            tab_text = self.editor_tabs.tabText(i)
            if tab_text.endswith('*'):
                response = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    f"There are unsaved changes in '{tab_text}'. Do you want to save them before closing?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )

                if response == QMessageBox.Save:
                    self.editor_tabs.setCurrentIndex(i)
                    if not self.save_file():
                        event.ignore()
                        return
                elif response == QMessageBox.Cancel:
                    event.ignore()
                    return
                # If Discard, continue with the next tab

        event.accept()

    @Slot()
    def new_file(self):
        """Create a new file"""
        editor = CodeEditor(self.settings)

        # Connect editor signals
        editor.textChanged.connect(lambda: self._on_editor_text_changed(editor))
        editor.cursorPositionChanged.connect(lambda: self._on_cursor_position_changed(editor))

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
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'file_path') and widget.file_path == file_path:
                self.editor_tabs.setCurrentIndex(i)
                return

        # Open the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            editor = CodeEditor(self.settings)
            editor.set_file_path(file_path)  # Use the new method to set file path and update lexer
            editor.setPlainText(content)

            file_name = os.path.basename(file_path)

            # Connect editor signals
            editor.textChanged.connect(lambda: self._on_editor_text_changed(editor))
            editor.cursorPositionChanged.connect(lambda: self._on_cursor_position_changed(editor))

            # Add to split view container
            self.split_view_container.add_editor(editor, file_name)

            self.status_bar.showMessage(f"Opened {file_path}")
        except UnicodeDecodeError:
            QMessageBox.critical(self, "Error", f"Could not open file: {file_path}\nThe file appears to be a binary file or uses an unsupported encoding.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

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
        editor = self.editor_tabs.currentWidget()
        if not editor or not hasattr(editor, 'file_path'):
            return self.save_file_as()

        if not editor.file_path:
            return self.save_file_as()

        try:
            with open(editor.file_path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())

            # Update tab title to remove unsaved indicator
            index = self.editor_tabs.indexOf(editor)
            if index >= 0:
                current_text = self.editor_tabs.tabText(index)
                if current_text.endswith('*'):
                    self.editor_tabs.setTabText(index, current_text[:-1])

            self.status_bar.showMessage(f"Saved {editor.file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False

    @Slot()
    def save_file_as(self):
        """Save the current file with a new name"""
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return False

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())

                editor.set_file_path(file_path)  # Use the new method to set file path and update lexer
                file_name = os.path.basename(file_path)
                self.editor_tabs.setTabText(self.editor_tabs.currentIndex(), file_name)

                self.status_bar.showMessage(f"Saved {file_path}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                return False
        return False

    @Slot(int)
    def close_tab(self, index):
        """Close a tab"""
        # This method is now primarily used for the welcome tab
        # Other tabs are handled by the split view container

        # Check if this is the welcome tab
        widget = self.editor_tabs.widget(index)
        tab_text = self.editor_tabs.tabText(index)

        if tab_text == "Welcome":
            # Mark welcome tab as closed
            self.settings.set_welcome_tab_closed(True)
            self.editor_tabs.removeTab(index)
            return

        # For other tabs, check for unsaved changes
        if tab_text.endswith('*'):
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"The file '{tab_text}' has unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if response == QMessageBox.Save:
                # If it's an existing file
                if hasattr(widget, 'file_path') and widget.file_path:
                    self.editor_tabs.setCurrentIndex(index)
                    self.save_file()
                else:
                    self.editor_tabs.setCurrentIndex(index)
                    if not self.save_file_as():
                        return  # Cancel close if save was cancelled
            elif response == QMessageBox.Cancel:
                return  # Cancel close

        self.editor_tabs.removeTab(index)

    def _on_editor_text_changed(self, editor):
        """Handle text changes in the editor"""
        # Update tab title to show unsaved changes
        index = self.editor_tabs.indexOf(editor)
        if index >= 0:
            current_text = self.editor_tabs.tabText(index)
            if not current_text.endswith('*'):
                self.editor_tabs.setTabText(index, current_text + '*')

    def _on_cursor_position_changed(self, editor):
        """Update status bar with cursor position"""
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.status_bar.showMessage(f"Line: {line}, Column: {column}")

    @Slot()
    def split_horizontal(self):
        """Split the editor view horizontally"""
        self.split_view_container.split_horizontally()

    @Slot()
    def split_vertical(self):
        """Split the editor view vertically"""
        self.split_view_container.split_vertically()

    @Slot(CodeEditor)
    def _on_editor_created(self, editor):
        """Handle editor created signal from split view container"""
        # This is called when a new editor is created in any split
        pass

    @Slot(CodeEditor)
    def _on_editor_closed(self, editor):
        """Handle editor closed signal from split view container"""
        # This is called when an editor is closed in any split
        pass

    def _save_open_files(self):
        """Save the list of open files"""
        open_files = []
        has_welcome_tab = False

        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            tab_text = self.editor_tabs.tabText(i)

            # Check if welcome tab is still open
            if tab_text == "Welcome":
                has_welcome_tab = True
                continue

            if hasattr(widget, 'file_path') and widget.file_path and os.path.exists(widget.file_path):
                open_files.append(widget.file_path)

        # Update welcome tab status
        self.settings.set_welcome_tab_closed(not has_welcome_tab)

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

    @Slot(bool)
    def toggle_explorer(self, checked):
        """Toggle the file explorer visibility"""
        self.file_explorer_dock.setVisible(checked)

    @Slot()
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.settings.get_theme()
        new_theme = "light" if current_theme == "dark" else "dark"
        self.settings.set_theme(new_theme)

    @Slot()
    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About McpIDE",
            "McpIDE - A VS Code-inspired IDE with future support for Minecraft Pocket Edition scripts and addons."
        )
