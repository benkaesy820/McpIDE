#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code editor component for McpIDE.
Provides syntax highlighting, line numbers, and other editing features.
"""

import os
import re
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PySide6.QtCore import Qt, Signal, Slot, QRect, QSize, QRegularExpression
from PySide6.QtGui import QColor, QPainter, QFont, QTextCursor, QTextCharFormat, QTextDocument

from src.utils.syntax_highlighter import PygmentsSyntaxHighlighter, detect_language_from_filename

class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """
    Code editor widget with line numbers and syntax highlighting
    """
    cursor_position_changed = Signal(int, int)  # line, column
    file_dropped = Signal(str)  # Emitted when a file is dropped onto the editor
    search_finished = Signal(bool)  # Emitted when search is finished (found or not)

    def __init__(self, settings, theme_manager):
        super().__init__()
        self.settings = settings
        self.theme_manager = theme_manager
        self.file_path = None
        self._auto_indent = True

        self._setup_editor()
        self._setup_line_numbers()
        self._setup_context_menu()
        self._connect_signals()

        # Set parent tab widget for later reference
        self._parent_tab_widget = None

        # Initialize syntax highlighter
        self.highlighter = PygmentsSyntaxHighlighter(self.document(), theme_manager)

    def _setup_editor(self):
        """Set up editor properties"""
        # Set font
        font = QFont(self.settings.get_font_family(), self.settings.get_font_size())
        font.setFixedPitch(True)
        self.setFont(font)

        # Set tab size
        tab_size = self.settings.get_tab_size()
        self.setTabStopDistance(tab_size * self.fontMetrics().horizontalAdvance(' '))

        # Set word wrap
        try:
            # For newer PySide6 versions
            self.setWordWrapMode(Qt.TextWrapMode.NoWrap)
            if self.settings.get_word_wrap():
                self.setWordWrapMode(Qt.TextWrapMode.WidgetWidth)
        except AttributeError:
            # For older PySide6 versions
            from PySide6.QtGui import QTextOption
            self.setWordWrapMode(QTextOption.NoWrap)
            if self.settings.get_word_wrap():
                self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        # Set cursor width
        self.setCursorWidth(2)

        # Set placeholder text
        self.setPlaceholderText("Type your code here...")

        # Enable drag and drop
        self.setAcceptDrops(True)

    def _setup_line_numbers(self):
        """Set up line number area"""
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def _setup_context_menu(self):
        """Set up the context menu for the editor"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _connect_signals(self):
        """Connect signals to slots"""
        # Connect settings changes
        self.settings.theme_changed.connect(self._on_theme_changed)
        self.settings.editor_font_changed.connect(self._on_font_changed)

        # Connect cursor position change
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)

    def line_number_area_width(self):
        """Calculate width of line number area"""
        if not self.settings.get_show_line_numbers():
            return 0

        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        """Update line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update line number area on scroll"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        if not self.settings.get_show_line_numbers():
            return

        painter = QPainter(self.line_number_area)

        # Set background color based on theme
        theme = self.settings.get_theme()
        bg_color = self.theme_manager.get_color("sidebar", theme)
        text_color = self.theme_manager.get_color("line_number", theme)

        painter.fillRect(event.rect(), bg_color)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        # Set text color
        painter.setPen(text_color)

        font = painter.font()
        font.setBold(False)
        painter.setFont(font)

        # Highlight current line number
        cursor = self.textCursor()
        current_line = cursor.blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)

                # Use bold for current line number
                if block_number == current_line:
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)

                    # Use different color for current line
                    if theme == "dark":
                        painter.setPen(QColor("#ffffff"))
                    else:
                        painter.setPen(QColor("#000000"))
                else:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)
                    painter.setPen(text_color)

                painter.drawText(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(),
                                Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def keyPressEvent(self, event):
        """Handle key press events for auto-indentation and other features"""
        # Auto-indentation for Enter key
        if self._auto_indent and event.key() == Qt.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            indent = ''

            # Get the indentation of the current line
            for char in text:
                if char == ' ' or char == '\t':
                    indent += char
                else:
                    break

            # Add extra indentation if line ends with a colon
            if text.rstrip().endswith(':'):
                if self.settings.get_use_spaces():
                    indent += ' ' * self.settings.get_tab_size()
                else:
                    indent += '\t'

            # Insert new line with indentation
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        # Handle tab key for spaces
        if event.key() == Qt.Key_Tab and self.settings.get_use_spaces():
            spaces = ' ' * self.settings.get_tab_size()
            self.insertPlainText(spaces)
            return

        super().keyPressEvent(event)

    def _show_context_menu(self, position):
        """Show the context menu"""
        menu = self.createStandardContextMenu()
        menu.exec_(self.viewport().mapToGlobal(position))

    def set_file_path(self, file_path):
        """Set the file path"""
        self.file_path = file_path

        # Set syntax highlighter based on file extension
        if file_path:
            self.highlighter.set_lexer_from_filename(file_path)

    @Slot(str)
    def _on_theme_changed(self, theme_name):
        """Handle theme change"""
        # Update line numbers
        self.update()
        self.line_number_area.update()

        # Update syntax highlighter theme
        self.highlighter.set_theme(theme_name)

    @Slot(str, int)
    def _on_font_changed(self, family, size):
        """Handle font change"""
        font = QFont(family, size)
        font.setFixedPitch(True)
        self.setFont(font)

        # Update tab size
        tab_size = self.settings.get_tab_size()
        self.setTabStopDistance(tab_size * self.fontMetrics().horizontalAdvance(' '))

        # Update line numbers
        self.update_line_number_area_width(0)

    @Slot()
    def _on_cursor_position_changed(self):
        """Handle cursor position change"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)

    def load_file(self, file_path):
        """Load a file into the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.setPlainText(content)
            self.set_file_path(file_path)
            self.document().setModified(False)
            return True
        except UnicodeDecodeError:
            # Handle binary files
            return False
        except Exception:
            # Handle other errors
            return False

    def save_file(self, file_path=None):
        """Save the editor content to a file"""
        if file_path is None:
            file_path = self.file_path

        if not file_path:
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())

            self.set_file_path(file_path)
            self.document().setModified(False)
            return True
        except Exception:
            # Handle errors
            return False

    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        # Check if the drag contains URLs (files)
        if event.mimeData().hasUrls():
            # Accept the drag event to allow dropping
            event.acceptProposedAction()
        else:
            # For text drops, use the default behavior
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        """Handle drop event"""
        # Check if the drop contains URLs (files)
        if event.mimeData().hasUrls():
            # Get the first URL (we only handle one file at a time)
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()

            # Check if it's a file
            if os.path.isfile(file_path):
                # If we have a parent tab widget, use it as the target
                if hasattr(self, '_parent_tab_widget') and self._parent_tab_widget:
                    # This will ensure the file opens in the same split view
                    from PySide6.QtCore import QCoreApplication
                    app = QCoreApplication.instance()
                    if hasattr(app, 'main_window'):
                        # Get the main window and set the target tab widget
                        main_window = app.main_window
                        if hasattr(main_window, 'split_view_container'):
                            main_window.split_view_container._last_drop_target = self._parent_tab_widget

                # Emit signal with the file path
                self.file_dropped.emit(file_path)

                # Accept the drop event
                event.acceptProposedAction()
                return

        # For text drops, use the default behavior
        super().dropEvent(event)

    def find_text(self, text, case_sensitive=False, whole_words=False, regex=False, forward=True):
        """Find text in the document"""
        # Create find flags
        flags = QTextDocument.FindFlags()

        if case_sensitive:
            flags |= QTextDocument.FindCaseSensitively

        if whole_words:
            flags |= QTextDocument.FindWholeWords

        if not forward:
            flags |= QTextDocument.FindBackward

        # Use regex if specified
        if regex:
            try:
                pattern = QRegularExpression(text)
                if not case_sensitive:
                    pattern.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                found = self.document().find(pattern, self.textCursor(), flags)
            except Exception:
                # Invalid regex
                self.search_finished.emit(False)
                return False
        else:
            # Use plain text search
            found = self.document().find(text, self.textCursor(), flags)

        # If not found, try wrapping around
        if found.isNull():
            # Move cursor to start or end of document
            cursor = self.textCursor()
            if forward:
                cursor.movePosition(QTextCursor.Start)
            else:
                cursor.movePosition(QTextCursor.End)

            self.setTextCursor(cursor)

            # Try search again
            if regex:
                pattern = QRegularExpression(text)
                if not case_sensitive:
                    pattern.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
                found = self.document().find(pattern, self.textCursor(), flags)
            else:
                found = self.document().find(text, self.textCursor(), flags)

        # If found, select the text
        if not found.isNull():
            self.setTextCursor(found)
            self.search_finished.emit(True)
            return True

        # Not found
        self.search_finished.emit(False)
        return False

    def replace_text(self, find_text, replace_text, case_sensitive=False, whole_words=False, regex=False):
        """Replace selected text if it matches the find text"""
        # Get the selected text
        cursor = self.textCursor()
        selected_text = cursor.selectedText()

        # Check if the selected text matches the find text
        if not selected_text:
            # No text selected, try to find the text first
            if not self.find_text(find_text, case_sensitive, whole_words, regex):
                return False

            # Get the selected text again
            cursor = self.textCursor()
            selected_text = cursor.selectedText()

        # Check if the selected text matches the find text
        matches = False
        if regex:
            try:
                pattern = re.compile(find_text, re.IGNORECASE if not case_sensitive else 0)
                matches = bool(pattern.fullmatch(selected_text))
            except Exception:
                # Invalid regex
                return False
        else:
            if case_sensitive:
                matches = selected_text == find_text
            else:
                matches = selected_text.lower() == find_text.lower()

        # If it matches, replace it
        if matches:
            cursor.insertText(replace_text)
            return True

        # Try to find the text first
        if not self.find_text(find_text, case_sensitive, whole_words, regex):
            return False

        # Replace the found text
        cursor = self.textCursor()
        cursor.insertText(replace_text)
        return True

    def replace_all(self, find_text, replace_text, case_sensitive=False, whole_words=False, regex=False):
        """Replace all occurrences of the find text"""
        # Save the current cursor position
        original_cursor = self.textCursor()

        # Move to the start of the document
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.setTextCursor(cursor)

        # Count replacements
        count = 0

        # Start a single undo operation for all replacements
        cursor.beginEditBlock()

        # Replace all occurrences
        while self.find_text(find_text, case_sensitive, whole_words, regex):
            cursor = self.textCursor()
            cursor.insertText(replace_text)
            count += 1

        # End the edit block
        cursor.endEditBlock()

        # Restore the original cursor position
        self.setTextCursor(original_cursor)

        return count
