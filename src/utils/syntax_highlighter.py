#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Syntax highlighter for McpIDE.
Uses Pygments for syntax highlighting of various programming languages.
"""

import os
from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.token import Token
from pygments.util import ClassNotFound

class PygmentsSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter that uses Pygments for code highlighting.
    """
    def __init__(self, document, theme_manager):
        super().__init__(document)
        self.theme_manager = theme_manager
        self.lexer = None
        self.formats = {}
        
        # Initialize token formats
        self._create_formats()
    
    def _create_formats(self):
        """Create text formats for different token types"""
        # Default format
        self.formats[Token] = self._create_format()
        
        # String formats
        self.formats[Token.Literal.String] = self._create_format(foreground=QColor(152, 195, 121))
        self.formats[Token.Literal.String.Doc] = self._create_format(foreground=QColor(152, 195, 121))
        self.formats[Token.Literal.String.Single] = self._create_format(foreground=QColor(152, 195, 121))
        self.formats[Token.Literal.String.Double] = self._create_format(foreground=QColor(152, 195, 121))
        self.formats[Token.Literal.String.Backtick] = self._create_format(foreground=QColor(152, 195, 121))
        self.formats[Token.Literal.String.Escape] = self._create_format(foreground=QColor(209, 154, 102))
        
        # Number formats
        self.formats[Token.Literal.Number] = self._create_format(foreground=QColor(209, 154, 102))
        self.formats[Token.Literal.Number.Integer] = self._create_format(foreground=QColor(209, 154, 102))
        self.formats[Token.Literal.Number.Float] = self._create_format(foreground=QColor(209, 154, 102))
        self.formats[Token.Literal.Number.Hex] = self._create_format(foreground=QColor(209, 154, 102))
        
        # Keyword formats
        self.formats[Token.Keyword] = self._create_format(foreground=QColor(198, 120, 221), bold=True)
        self.formats[Token.Keyword.Constant] = self._create_format(foreground=QColor(198, 120, 221), bold=True)
        self.formats[Token.Keyword.Declaration] = self._create_format(foreground=QColor(198, 120, 221), bold=True)
        self.formats[Token.Keyword.Namespace] = self._create_format(foreground=QColor(198, 120, 221), bold=True)
        self.formats[Token.Keyword.Reserved] = self._create_format(foreground=QColor(198, 120, 221), bold=True)
        self.formats[Token.Keyword.Type] = self._create_format(foreground=QColor(224, 108, 117), bold=True)
        
        # Name formats
        self.formats[Token.Name] = self._create_format()
        self.formats[Token.Name.Class] = self._create_format(foreground=QColor(224, 108, 117), bold=True)
        self.formats[Token.Name.Function] = self._create_format(foreground=QColor(97, 175, 239))
        self.formats[Token.Name.Builtin] = self._create_format(foreground=QColor(224, 108, 117))
        self.formats[Token.Name.Builtin.Pseudo] = self._create_format(foreground=QColor(224, 108, 117))
        self.formats[Token.Name.Exception] = self._create_format(foreground=QColor(224, 108, 117), bold=True)
        self.formats[Token.Name.Decorator] = self._create_format(foreground=QColor(97, 175, 239))
        self.formats[Token.Name.Namespace] = self._create_format(foreground=QColor(224, 108, 117))
        self.formats[Token.Name.Constant] = self._create_format(foreground=QColor(209, 154, 102))
        
        # Comment formats
        self.formats[Token.Comment] = self._create_format(foreground=QColor(92, 99, 112), italic=True)
        self.formats[Token.Comment.Single] = self._create_format(foreground=QColor(92, 99, 112), italic=True)
        self.formats[Token.Comment.Multiline] = self._create_format(foreground=QColor(92, 99, 112), italic=True)
        self.formats[Token.Comment.Preproc] = self._create_format(foreground=QColor(92, 99, 112))
        
        # Operator formats
        self.formats[Token.Operator] = self._create_format(foreground=QColor(86, 182, 194))
        self.formats[Token.Operator.Word] = self._create_format(foreground=QColor(86, 182, 194), bold=True)
        
        # Punctuation formats
        self.formats[Token.Punctuation] = self._create_format(foreground=QColor(86, 182, 194))
        
        # Error formats
        self.formats[Token.Error] = self._create_format(foreground=QColor(224, 108, 117), underline=True)
        
        # Generic formats
        self.formats[Token.Generic.Heading] = self._create_format(foreground=QColor(97, 175, 239), bold=True)
        self.formats[Token.Generic.Subheading] = self._create_format(foreground=QColor(97, 175, 239), bold=True)
        self.formats[Token.Generic.Deleted] = self._create_format(foreground=QColor(224, 108, 117))
        self.formats[Token.Generic.Inserted] = self._create_format(foreground=QColor(152, 195, 121))
        self.formats[Token.Generic.Error] = self._create_format(foreground=QColor(224, 108, 117), underline=True)
        self.formats[Token.Generic.Emph] = self._create_format(italic=True)
        self.formats[Token.Generic.Strong] = self._create_format(bold=True)
    
    def _create_format(self, foreground=None, background=None, bold=False, italic=False, underline=False):
        """Create a QTextCharFormat with the given attributes"""
        text_format = QTextCharFormat()
        
        if foreground:
            text_format.setForeground(foreground)
        
        if background:
            text_format.setBackground(background)
        
        if bold:
            text_format.setFontWeight(QFont.Bold)
        
        if italic:
            text_format.setFontItalic(True)
        
        if underline:
            text_format.setFontUnderline(True)
        
        return text_format
    
    def set_theme(self, theme):
        """Update formats based on theme"""
        # TODO: Implement theme-based highlighting
        pass
    
    def set_lexer_from_filename(self, filename):
        """Set the lexer based on the file extension"""
        try:
            self.lexer = get_lexer_for_filename(filename, stripall=True)
        except ClassNotFound:
            # Default to Python lexer if no specific lexer is found
            self.lexer = TextLexer()
        
        # Rehighlight the document
        self.rehighlight()
    
    def set_lexer_from_language(self, language):
        """Set the lexer based on the language name"""
        try:
            self.lexer = get_lexer_by_name(language, stripall=True)
        except ClassNotFound:
            # Default to Python lexer if no specific lexer is found
            self.lexer = TextLexer()
        
        # Rehighlight the document
        self.rehighlight()
    
    def highlightBlock(self, text):
        """Highlight a block of text"""
        if not self.lexer:
            return
        
        # Get the current block's state
        current_state = self.previousBlockState()
        
        # Process the text with Pygments
        tokens = list(self.lexer.get_tokens(text))
        
        # Apply formatting
        position = 0
        for token_type, token_text in tokens:
            length = len(token_text)
            
            # Find the most specific format for this token type
            token_format = self._get_format_for_token(token_type)
            
            if token_format:
                self.setFormat(position, length, token_format)
            
            position += length
    
    def _get_format_for_token(self, token_type):
        """Get the most specific format for a token type"""
        while token_type not in self.formats:
            token_type = token_type.parent
            if token_type is None:
                return self.formats[Token]
        
        return self.formats[token_type]


def detect_language_from_filename(filename):
    """Detect the programming language from a filename"""
    try:
        lexer = get_lexer_for_filename(filename)
        return lexer.name
    except ClassNotFound:
        # Default to plain text if no specific lexer is found
        return "Text"


def get_supported_languages():
    """Get a list of supported programming languages"""
    from pygments.lexers import get_all_lexers
    
    languages = []
    for lexer in get_all_lexers():
        languages.append(lexer[0])
    
    return sorted(languages)
