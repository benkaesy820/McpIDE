#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Search and replace dialog for McpIDE.
Provides find and replace functionality for the editor.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt, Signal, Slot, QRegularExpression

class SearchDialog(QDialog):
    """
    Dialog for searching and replacing text in the editor.
    """
    # Signals
    find_next = Signal(str, bool, bool, bool)  # text, case_sensitive, whole_words, regex
    find_previous = Signal(str, bool, bool, bool)  # text, case_sensitive, whole_words, regex
    replace = Signal(str, str, bool, bool, bool)  # find_text, replace_text, case_sensitive, whole_words, regex
    replace_all = Signal(str, str, bool, bool, bool)  # find_text, replace_text, case_sensitive, whole_words, regex
    
    def __init__(self, parent=None, selected_text=""):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
        # Set initial search text if provided
        if selected_text:
            self.search_line_edit.setText(selected_text)
            self.search_line_edit.selectAll()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        
        # Search and replace inputs
        self.grid_layout = QGridLayout()
        
        # Search input
        self.search_label = QLabel("Find:")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setPlaceholderText("Text to find")
        
        # Replace input
        self.replace_label = QLabel("Replace with:")
        self.replace_line_edit = QLineEdit()
        self.replace_line_edit.setPlaceholderText("Replacement text")
        
        # Add to grid layout
        self.grid_layout.addWidget(self.search_label, 0, 0)
        self.grid_layout.addWidget(self.search_line_edit, 0, 1)
        self.grid_layout.addWidget(self.replace_label, 1, 0)
        self.grid_layout.addWidget(self.replace_line_edit, 1, 1)
        
        # Options group
        self.options_group = QGroupBox("Options")
        self.options_layout = QVBoxLayout(self.options_group)
        
        # Case sensitive option
        self.case_sensitive_check = QCheckBox("Case sensitive")
        
        # Whole words option
        self.whole_words_check = QCheckBox("Whole words only")
        
        # Regex option
        self.regex_check = QCheckBox("Regular expression")
        
        # Add options to layout
        self.options_layout.addWidget(self.case_sensitive_check)
        self.options_layout.addWidget(self.whole_words_check)
        self.options_layout.addWidget(self.regex_check)
        
        # Direction group
        self.direction_group = QGroupBox("Direction")
        self.direction_layout = QVBoxLayout(self.direction_group)
        
        # Direction options
        self.forward_radio = QRadioButton("Forward")
        self.backward_radio = QRadioButton("Backward")
        
        # Set forward as default
        self.forward_radio.setChecked(True)
        
        # Add direction options to layout
        self.direction_layout.addWidget(self.forward_radio)
        self.direction_layout.addWidget(self.backward_radio)
        
        # Buttons layout
        self.buttons_layout = QVBoxLayout()
        
        # Find buttons
        self.find_button = QPushButton("Find")
        self.find_button.clicked.connect(self._on_find_clicked)
        
        # Replace buttons
        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self._on_replace_clicked)
        
        # Replace all button
        self.replace_all_button = QPushButton("Replace All")
        self.replace_all_button.clicked.connect(self._on_replace_all_clicked)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        # Add buttons to layout
        self.buttons_layout.addWidget(self.find_button)
        self.buttons_layout.addWidget(self.replace_button)
        self.buttons_layout.addWidget(self.replace_all_button)
        self.buttons_layout.addWidget(self.close_button)
        self.buttons_layout.addStretch()
        
        # Options and buttons layout
        self.options_buttons_layout = QHBoxLayout()
        self.options_buttons_layout.addWidget(self.options_group)
        self.options_buttons_layout.addWidget(self.direction_group)
        self.options_buttons_layout.addLayout(self.buttons_layout)
        
        # Add layouts to main layout
        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addLayout(self.options_buttons_layout)
        
        # Set focus to search input
        self.search_line_edit.setFocus()
    
    def _on_find_clicked(self):
        """Handle find button click"""
        search_text = self.search_line_edit.text()
        if not search_text:
            return
        
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_words = self.whole_words_check.isChecked()
        regex = self.regex_check.isChecked()
        
        if self.forward_radio.isChecked():
            self.find_next.emit(search_text, case_sensitive, whole_words, regex)
        else:
            self.find_previous.emit(search_text, case_sensitive, whole_words, regex)
    
    def _on_replace_clicked(self):
        """Handle replace button click"""
        search_text = self.search_line_edit.text()
        replace_text = self.replace_line_edit.text()
        
        if not search_text:
            return
        
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_words = self.whole_words_check.isChecked()
        regex = self.regex_check.isChecked()
        
        self.replace.emit(search_text, replace_text, case_sensitive, whole_words, regex)
    
    def _on_replace_all_clicked(self):
        """Handle replace all button click"""
        search_text = self.search_line_edit.text()
        replace_text = self.replace_line_edit.text()
        
        if not search_text:
            return
        
        case_sensitive = self.case_sensitive_check.isChecked()
        whole_words = self.whole_words_check.isChecked()
        regex = self.regex_check.isChecked()
        
        self.replace_all.emit(search_text, replace_text, case_sensitive, whole_words, regex)
