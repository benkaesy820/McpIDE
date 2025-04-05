#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Theme manager for McpIDE.
Handles application-wide theming and provides dark and light mode.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

class ThemeManager:
    """
    Manages application themes (dark/light)
    """
    def __init__(self, settings):
        self.settings = settings
        
        # Define color schemes
        self.dark_palette = self._create_dark_palette()
        self.light_palette = self._create_light_palette()
        
        # Define theme colors for programmatic access
        self.colors = {
            "dark": {
                "background": QColor(30, 30, 30),
                "foreground": QColor(212, 212, 212),
                "selection": QColor(42, 130, 218),
                "accent": QColor(0, 122, 204),
                "border": QColor(60, 60, 60),
                "active_tab": QColor(37, 37, 38),
                "inactive_tab": QColor(45, 45, 45),
                "sidebar": QColor(37, 37, 38),
                "line_number": QColor(120, 120, 120),
                "current_line": QColor(40, 40, 40),
                "error": QColor(224, 108, 117),
                "warning": QColor(229, 192, 123),
                "info": QColor(97, 175, 239),
                "success": QColor(152, 195, 121)
            },
            "light": {
                "background": QColor(255, 255, 255),
                "foreground": QColor(0, 0, 0),
                "selection": QColor(173, 214, 255),
                "accent": QColor(0, 120, 215),
                "border": QColor(213, 213, 213),
                "active_tab": QColor(255, 255, 255),
                "inactive_tab": QColor(240, 240, 240),
                "sidebar": QColor(243, 243, 243),
                "line_number": QColor(120, 120, 120),
                "current_line": QColor(245, 245, 245),
                "error": QColor(205, 49, 49),
                "warning": QColor(203, 145, 47),
                "info": QColor(0, 120, 215),
                "success": QColor(0, 133, 62)
            }
        }
    
    def _create_dark_palette(self):
        """Create dark theme palette"""
        palette = QPalette()
        
        # Set colors for dark theme
        palette.setColor(QPalette.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
        palette.setColor(QPalette.Text, QColor(212, 212, 212))
        palette.setColor(QPalette.Button, QColor(45, 45, 45))
        palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        
        return palette
    
    def _create_light_palette(self):
        """Create light theme palette"""
        palette = QPalette()
        
        # Set colors for light theme
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(233, 233, 233))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 120, 120))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
        
        return palette
    
    def apply_theme(self, theme):
        """Apply the specified theme to the application"""
        app = QApplication.instance()
        
        if theme == "dark":
            app.setPalette(self.dark_palette)
            app.setStyle("Fusion")  # Fusion style works well with custom palettes
            app.setStyleSheet(self._get_dark_stylesheet())
        else:
            app.setPalette(self.light_palette)
            app.setStyle("Fusion")
            app.setStyleSheet(self._get_light_stylesheet())
    
    def get_color(self, name, theme=None):
        """Get a color from the current theme"""
        if theme is None:
            theme = self.settings.get_theme()
        
        if theme in self.colors and name in self.colors[theme]:
            return self.colors[theme][name]
        
        # Return a default color if not found
        return QColor(0, 0, 0) if theme == "light" else QColor(255, 255, 255)
    
    def _get_dark_stylesheet(self):
        """Get dark theme stylesheet"""
        return """
        QToolTip {
            color: #d4d4d4;
            background-color: #1e1e1e;
            border: 1px solid #3e3e3e;
        }
        
        QTabWidget::pane {
            border: 1px solid #3e3e3e;
        }
        
        QTabBar::tab {
            background: #2d2d2d;
            color: #d4d4d4;
            padding: 5px;
            border: 1px solid #3e3e3e;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background: #1e1e1e;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        
        QStatusBar {
            background: #2d2d2d;
            color: #d4d4d4;
        }
        
        QMenuBar {
            background-color: #2d2d2d;
            color: #d4d4d4;
        }
        
        QMenuBar::item {
            background: transparent;
        }
        
        QMenuBar::item:selected {
            background: #3e3e3e;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #d4d4d4;
            border: 1px solid #3e3e3e;
        }
        
        QMenu::item:selected {
            background-color: #3e3e3e;
        }
        
        QToolBar {
            background: #2d2d2d;
            border: none;
        }
        
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }
        
        QDockWidget::title {
            text-align: center;
            background: #2d2d2d;
            padding-left: 5px;
        }
        
        QLineEdit {
            background: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3e3e3e;
            border-radius: 2px;
            padding: 2px;
        }
        
        QTreeView {
            background-color: #1e1e1e;
            alternate-background-color: #2d2d2d;
            color: #d4d4d4;
        }
        
        QTreeView::item:hover {
            background: #3e3e3e;
        }
        
        QTreeView::item:selected {
            background: #2a82da;
        }
        
        QSplitter::handle {
            background-color: #3e3e3e;
        }
        
        QSplitter::handle:horizontal {
            width: 1px;
        }
        
        QSplitter::handle:vertical {
            height: 1px;
        }
        
        QScrollBar:vertical {
            background: #2d2d2d;
            width: 12px;
            margin: 12px 0 12px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #5d5d5d;
            min-height: 20px;
            border-radius: 3px;
        }
        
        QScrollBar::add-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """
    
    def _get_light_stylesheet(self):
        """Get light theme stylesheet"""
        return """
        QToolTip {
            color: #000000;
            background-color: #ffffff;
            border: 1px solid #c0c0c0;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
        }
        
        QTabBar::tab {
            background: #f0f0f0;
            color: #000000;
            padding: 5px;
            border: 1px solid #c0c0c0;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background: #ffffff;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        
        QStatusBar {
            background: #f0f0f0;
            color: #000000;
        }
        
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
        }
        
        QMenuBar::item {
            background: transparent;
        }
        
        QMenuBar::item:selected {
            background: #e0e0e0;
        }
        
        QMenu {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #c0c0c0;
        }
        
        QMenu::item:selected {
            background-color: #e0e0e0;
        }
        
        QToolBar {
            background: #f0f0f0;
            border: none;
        }
        
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }
        
        QDockWidget::title {
            text-align: center;
            background: #f0f0f0;
            padding-left: 5px;
        }
        
        QLineEdit {
            background: #ffffff;
            color: #000000;
            border: 1px solid #c0c0c0;
            border-radius: 2px;
            padding: 2px;
        }
        
        QTreeView {
            background-color: #ffffff;
            alternate-background-color: #f7f7f7;
            color: #000000;
        }
        
        QTreeView::item:hover {
            background: #e0e0e0;
        }
        
        QTreeView::item:selected {
            background: #0078d7;
        }
        
        QSplitter::handle {
            background-color: #c0c0c0;
        }
        
        QSplitter::handle:horizontal {
            width: 1px;
        }
        
        QSplitter::handle:vertical {
            height: 1px;
        }
        
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 12px;
            margin: 12px 0 12px 0;
        }
        
        QScrollBar::handle:vertical {
            background: #c0c0c0;
            min-height: 20px;
            border-radius: 3px;
        }
        
        QScrollBar::add-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """
