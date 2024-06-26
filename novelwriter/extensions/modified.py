"""
novelWriter – Custom Widget: Modified Widgets
=============================================

File History:
Created: 2024-02-01 [2.3b1] NComboBox
Created: 2024-02-01 [2.3b1] NSpinBox
Created: 2024-02-01 [2.3b1] NDoubleSpinBox
Created: 2024-05-01 [2.5b1] NToolDialog
Created: 2024-05-01 [2.5b1] NNonBlockingDialog

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QDialog, QDoubleSpinBox, QSpinBox, QToolButton,
    QWidget
)

from novelwriter import CONFIG, SHARED

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain


class NToolDialog(QDialog):

    def __init__(self, parent: GuiMain) -> None:
        super().__init__(parent=parent)
        self.setModal(False)
        if CONFIG.osDarwin:
            self.setWindowFlag(Qt.WindowType.Tool)
        return

    def activateDialog(self) -> None:
        """Helper function to activate dialog on various systems."""
        self.show()
        if CONFIG.osWindows:
            self.activateWindow()
        self.raise_()
        QApplication.processEvents()
        return

# END Class NToolDialog


class NNonBlockingDialog(QDialog):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setModal(True)
        return

    def activateDialog(self) -> None:
        """Helper function to activate dialog on various systems."""
        self.show()
        if CONFIG.osWindows:
            self.activateWindow()
        self.raise_()
        QApplication.processEvents()
        return

# END Class NNonBlockingDialog


class NComboBox(QComboBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
        return

    def setCurrentData(self, data: str | Enum, default: str | Enum) -> None:
        """Set the current index from data, with a fallback."""
        idx = self.findData(data)
        self.setCurrentIndex(self.findData(default) if idx < 0 else idx)
        return

# END Class NComboBox


class NSpinBox(QSpinBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
        return

# END Class NSpinBox


class NDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()
        return

# END Class NDoubleSpinBox


class NIconToolButton(QToolButton):

    def __init__(self, parent: QWidget, iconSize: QSize, icon: str | None = None) -> None:
        super().__init__(parent=parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(iconSize)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        if icon:
            self.setThemeIcon(icon)
        return

    def setThemeIcon(self, iconKey: str) -> None:
        """Set an icon from the current theme."""
        self.setIcon(SHARED.theme.getIcon(iconKey))
        return

# END Class NIconToolButton


class NIconToggleButton(QToolButton):

    def __init__(self, parent: QWidget, iconSize: QSize, icon: str | None = None) -> None:
        super().__init__(parent=parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.setIconSize(iconSize)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setCheckable(True)
        self.setStyleSheet("border: none; background: transparent;")
        if icon:
            self.setThemeIcon(icon)
        return

    def setThemeIcon(self, iconKey: str) -> None:
        """Set an icon from the current theme."""
        iconSize = self.iconSize()
        self.setIcon(SHARED.theme.getToggleIcon(iconKey, (iconSize.width(), iconSize.height())))
        return

# END Class NUnfoldButton
