#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        if theme == "dark":
            QApplication.setPalette(self.dark_palette)
            QApplication.setStyle("Fusion")  # Fusion style works well with custom palettes
        else:
            QApplication.setPalette(self.light_palette)
            QApplication.setStyle("Fusion")

        # Apply stylesheet for additional styling
        app = QApplication.instance()
        if theme == "dark":
            app.setStyleSheet(self._get_dark_stylesheet())
        else:
            app.setStyleSheet(self._get_light_stylesheet())

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
        """