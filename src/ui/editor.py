#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, Slot, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat, QFont, QFontMetrics, QTextCursor
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, Python3Lexer
from pygments.formatters import HtmlFormatter
import os

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
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.file_path = None
        self.lexer = None

        self._setup_editor()
        self._setup_line_numbers()
        self._connect_signals()
        self._setup_context_menu()

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

        # Enable auto-indentation
        self.setAutoIndentation(True)

        # Set cursor width
        self.setCursorWidth(2)

        # Set placeholder text
        self.setPlaceholderText("Type your code here...")

    def _setup_line_numbers(self):
        """Set up line number area"""
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def _connect_signals(self):
        """Connect signals to slots"""
        # Connect settings changes
        self.settings.theme_changed.connect(self._on_theme_changed)

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
        if self.settings.get_theme() == "dark":
            painter.fillRect(event.rect(), QColor("#2d2d2d"))
        else:
            painter.fillRect(event.rect(), QColor("#f0f0f0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        # Set text color based on theme
        if self.settings.get_theme() == "dark":
            painter.setPen(QColor("#8f8f8f"))
        else:
            painter.setPen(QColor("#2d2d2d"))

        font = painter.font()
        font.setBold(False)
        painter.setFont(font)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(),
                                Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    @Slot(str)
    def _on_theme_changed(self, theme):
        """Handle theme change"""
        # Update line numbers
        self.update()
        self.line_number_area.update()

    def setAutoIndentation(self, enabled):
        """Enable or disable auto-indentation"""
        self._auto_indent = enabled

    def keyPressEvent(self, event):
        """Handle key press events for auto-indentation and other features"""
        # Auto-indentation for Enter key
        if hasattr(self, '_auto_indent') and self._auto_indent and event.key() == Qt.Key_Return:
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

    def _setup_context_menu(self):
        """Set up the context menu for the editor"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, position):
        """Show the context menu"""
        menu = self.createStandardContextMenu()
        menu.exec_(self.viewport().mapToGlobal(position))

    def set_file_path(self, file_path):
        """Set the file path and update lexer"""
        self.file_path = file_path
        self._update_lexer()

    def _update_lexer(self):
        """Update the lexer based on file extension"""
        if not self.file_path:
            self.lexer = Python3Lexer()  # Default to Python
            return

        try:
            self.lexer = get_lexer_for_filename(self.file_path, stripall=True)
        except Exception:
            # Default to Python if no lexer is found
            self.lexer = Python3Lexer()
