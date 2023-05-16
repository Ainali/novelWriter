"""
novelWriter – Main GUI Editor Class Tester
==========================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import pytest

from shutil import copyfile

from tools import (
    C, cmpFiles, buildTestProject, XML_IGNORE, getGuiItem, writeFile
)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QInputDialog

from novelwriter import CONFIG
from novelwriter.enum import nwItemType, nwView, nwWidget
from novelwriter.constants import nwFiles
from novelwriter.gui.outline import GuiOutlineView
from novelwriter.gui.projtree import GuiProjectTree
from novelwriter.gui.doceditor import GuiDocEditor
from novelwriter.gui.noveltree import GuiNovelView
from novelwriter.dialogs.about import GuiAbout
from novelwriter.dialogs.projload import GuiProjectLoad
from novelwriter.dialogs.editlabel import GuiEditLabel
from novelwriter.tools.projwizard import GuiProjectWizard

KEY_DELAY = 1


@pytest.mark.gui
def testGuiMain_ProjectBlocker(nwGUI):
    """Test the blocking of features when there's no project open.
    """
    # Test no-project blocking
    assert nwGUI.closeProject() is True
    assert nwGUI.saveProject() is False
    assert nwGUI.closeDocument() is False
    assert nwGUI.openDocument(None) is False
    assert nwGUI.openNextDocument(None) is False
    assert nwGUI.saveDocument() is False
    assert nwGUI.viewDocument(None) is False
    assert nwGUI.importDocument() is False
    assert nwGUI.openSelectedItem() is False
    assert nwGUI.editItemLabel() is False
    assert nwGUI.rebuildIndex() is False
    assert nwGUI.showProjectSettingsDialog() is False
    assert nwGUI.showProjectDetailsDialog() is False
    assert nwGUI.showBuildProjectDialog() is False
    assert nwGUI.showProjectWordListDialog() is False
    assert nwGUI.showWritingStatsDialog() is False

# END Test testGuiMain_ProjectBlocker


@pytest.mark.gui
def testGuiMain_Launch(qtbot, monkeypatch, nwGUI, prjLipsum):
    """Test the handling of launch tasks.
    """
    monkeypatch.setattr(GuiProjectLoad, "exec_", lambda *a: None)
    monkeypatch.setattr(GuiProjectLoad, "result", lambda *a: QDialog.Accepted)
    CONFIG.lastNotes = "0x0"

    # Open Lipsum project
    nwGUI.postLaunchTasks(prjLipsum)
    nwGUI.closeProject()

    # Check that release notes opened
    qtbot.waitUntil(lambda: getGuiItem("GuiAbout") is not None, timeout=1000)
    msgAbout = getGuiItem("GuiAbout")
    assert isinstance(msgAbout, GuiAbout)
    assert msgAbout.tabBox.currentWidget() == msgAbout.pageNotes
    msgAbout.accept()

    # Check that project open dialog launches
    nwGUI.postLaunchTasks(None)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)
    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()
    nwLoad.reject()

    # qtbot.stop()

# END Test testGuiMain_Launch


@pytest.mark.gui
def testGuiMain_NewProject(monkeypatch, nwGUI, projPath):
    """Test creating a new project.
    """
    # No data
    with monkeypatch.context() as mp:
        mp.setattr(GuiProjectWizard, "exec_", lambda *a: None)
        assert nwGUI.newProject(projData=None) is False

    # Close project
    with monkeypatch.context() as mp:
        nwGUI.hasProject = True
        mp.setattr(QMessageBox, "question", lambda *a: QMessageBox.No)
        assert nwGUI.newProject(projData={"projPath": projPath}) is False

    # No project path
    assert nwGUI.newProject(projData={}) is False

    # Project file already exists
    projFile = projPath / nwFiles.PROJ_FILE
    writeFile(projFile, "Stuff")
    assert nwGUI.newProject(projData={"projPath": projPath}) is False
    projFile.unlink()

    # An unreachable path should also fail
    stuffPath = projPath / "stuff" / "stuff" / "stuff"
    assert nwGUI.newProject(projData={"projPath": stuffPath}) is False

    # This one should work just fine
    assert nwGUI.newProject(projData={"projPath": projPath}) is True
    assert (projPath / nwFiles.PROJ_FILE).is_file()
    assert (projPath / "content").is_dir()

# END Test testGuiMain_NewProject


@pytest.mark.gui
def testGuiMain_ProjectTreeItems(qtbot, monkeypatch, nwGUI, projPath, mockRnd):
    """Test handling of project tree items based on GUI focus states.
    """
    buildTestProject(nwGUI, projPath)

    sHandle = "000000000000f"
    assert nwGUI.openSelectedItem() is False

    # Project Tree has focus
    nwGUI._changeView(nwView.PROJECT)
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projStack.setCurrentIndex(0)
    with monkeypatch.context() as mp:
        mp.setattr(GuiProjectTree, "hasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle() is None
        nwGUI.projView.projTree._getTreeItem(sHandle).setSelected(True)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle() == sHandle
        assert nwGUI.closeDocument() is True

    # Novel Tree has focus
    nwGUI._changeView(nwView.NOVEL)
    nwGUI.novelView.novelTree.refreshTree(rootHandle=None, overRide=True)
    with monkeypatch.context() as mp:
        mp.setattr(GuiNovelView, "treeHasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle() is None
        selItem = nwGUI.novelView.novelTree.topLevelItem(2)
        nwGUI.novelView.novelTree.setCurrentItem(selItem)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle() == sHandle
        assert nwGUI.closeDocument() is True

    # Project Outline has focus
    nwGUI._changeView(nwView.OUTLINE)
    nwGUI.switchFocus(nwWidget.OUTLINE)
    with monkeypatch.context() as mp:
        mp.setattr(GuiOutlineView, "treeHasFocus", lambda *a: True)
        assert nwGUI.docEditor.docHandle() is None
        selItem = nwGUI.outlineView.outlineTree.topLevelItem(2)
        nwGUI.outlineView.outlineTree.setCurrentItem(selItem)
        nwGUI._keyPressReturn()
        assert nwGUI.docEditor.docHandle() == sHandle
        assert nwGUI.closeDocument() is True

    # qtbot.stop()

# END Test testGuiMain_ProjectTreeItems


@pytest.mark.gui
def testGuiMain_Editing(qtbot, monkeypatch, nwGUI, projPath, tstPaths, mockRnd):
    """Test the document editor.
    """
    monkeypatch.setattr(GuiProjectTree, "hasFocus", lambda *a: True)
    monkeypatch.setattr(GuiDocEditor, "hasFocus", lambda *a: True)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, text: (text, True))
    monkeypatch.setattr(GuiEditLabel, "getLabel", lambda *a, text: (text, True))

    # Create new, save, close project
    buildTestProject(nwGUI, projPath)
    assert nwGUI.saveProject()
    assert nwGUI.closeProject()

    assert len(nwGUI.theProject.tree) == 0
    assert len(nwGUI.theProject.tree._treeOrder) == 0
    assert len(nwGUI.theProject.tree._treeRoots) == 0
    assert nwGUI.theProject.tree.trashRoot() is None
    assert nwGUI.theProject.data.name == ""
    assert nwGUI.theProject.data.title == ""
    assert nwGUI.theProject.data.author == ""
    assert nwGUI.theProject.data.spellCheck is False

    # Check the files
    projFile = projPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "guiEditor_Main_Initial_nwProject.nwx"
    compFile = tstPaths.refDir / "guiEditor_Main_Initial_nwProject.nwx"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=XML_IGNORE)

    # Re-open project
    assert nwGUI.openProject(projPath)

    # Check that we loaded the data
    assert len(nwGUI.theProject.tree) == 8
    assert len(nwGUI.theProject.tree._treeOrder) == 8
    assert len(nwGUI.theProject.tree._treeRoots) == 4
    assert nwGUI.theProject.tree.trashRoot() is None
    assert nwGUI.theProject.data.name == "New Project"
    assert nwGUI.theProject.data.title == "New Novel"
    assert nwGUI.theProject.data.author == "Jane Doe"
    assert nwGUI.theProject.data.spellCheck is False

    # Check that tree items have been created
    assert nwGUI.projView.projTree._getTreeItem(C.hNovelRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hPlotRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hCharRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hWorldRoot) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hTitlePage) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hChapterDir) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hChapterDoc) is not None
    assert nwGUI.projView.projTree._getTreeItem(C.hSceneDoc) is not None

    nwGUI.mainMenu.aSpellCheck.setChecked(True)
    assert nwGUI.mainMenu._toggleSpellCheck()

    # Change some settings
    CONFIG.hideHScroll = True
    CONFIG.hideVScroll = True
    CONFIG.autoScrollPos = 80
    CONFIG.autoScroll = True

    # Add a Character File
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hCharRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Jane Doe":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@tag: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "This is a file about Jane.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Add a Plot File
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hPlotRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Main Plot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@tag: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "This is a file detailing the main plot.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Add a World File
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hWorldRoot).setSelected(True)
    nwGUI.projView.projTree.newTreeItem(nwItemType.FILE, None, isNote=True)
    assert nwGUI.openSelectedItem()

    # Add Some Text
    nwGUI.docEditor.replaceText("Hello World!")
    assert nwGUI.docEditor.getText() == "Hello World!"
    nwGUI.docEditor.replaceText("")

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Main Location":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@tag: Home":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "This is a file describing Jane's home.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Trigger autosaves before making more changes
    nwGUI._autoSaveDocument()
    nwGUI._autoSaveProject()

    # Select the 'New Scene' file
    nwGUI.switchFocus(nwWidget.TREE)
    nwGUI.projView.projTree.clearSelection()
    nwGUI.projView.projTree._getTreeItem(C.hNovelRoot).setExpanded(True)
    nwGUI.projView.projTree._getTreeItem(C.hChapterDir).setExpanded(True)
    nwGUI.projView.projTree._getTreeItem(C.hSceneDoc).setSelected(True)
    assert nwGUI.openSelectedItem()

    # Type something into the document
    nwGUI.switchFocus(nwWidget.EDITOR)
    qtbot.keyClick(nwGUI.docEditor, "a", modifier=Qt.ControlModifier, delay=KEY_DELAY)
    for c in "# Novel":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "## Chapter":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "@pov: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@plot: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "### Scene":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "% How about a comment?":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@pov: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@plot: MainPlot":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    for c in "@location: Home":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "#### Some Section":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "@char: Jane":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "This is a paragraph of nonsense text.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Don't allow Shift+Enter to insert a line separator (issue #1150)
    for c in "This is another paragraph":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Enter, modifier=Qt.ShiftModifier, delay=KEY_DELAY)
    for c in "with a line separator in it.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Auto-Replace
    # ============

    for c in (
        "This is another paragraph of much longer nonsense text. "
        "It is in fact 1 very very NONSENSICAL nonsense text! "
    ):
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    for c in "We can also try replacing \"quotes\", even single 'quotes' are replaced. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    for c in "Isn't that nice? ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    for c in "We can hyphen-ate, make dashes -- and even longer dashes --- if we want. ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    for c in "Ellipsis? Not a problem either ... ":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    for c in "How about three hyphens - -":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Left, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Backspace, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Right, delay=KEY_DELAY)
    for c in "- for long dash? It works too.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "\"Full line double quoted text.\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "'Full line single quoted text.'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    # Insert spaces before and after quotes
    nwGUI.docEditor._typPadBefore = "\u201d"
    nwGUI.docEditor._typPadAfter = "\u201c"

    for c in "Some \"double quoted text with spaces padded\".":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    nwGUI.docEditor._typPadBefore = ""
    nwGUI.docEditor._typPadAfter = ""

    # Insert spaces before colon, but ignore tags and synopsis
    nwGUI.docEditor._typPadBefore = ":"

    for c in "@object: NoSpaceAdded":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "% synopsis: No space before this colon.":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "Add space before this colon: See?":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "But don't add a double space : See?":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    nwGUI.docEditor._typPadBefore = ""

    # Indent and Align
    # ================

    for c in "\t\"Tab-indented text\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">\"Paragraph-indented text\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">>\"Right-aligned text\"":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in "\t'Tab-indented text'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">'Paragraph-indented text'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    for c in ">>'Right-aligned text'":
        qtbot.keyClick(nwGUI.docEditor, c, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)
    qtbot.keyClick(nwGUI.docEditor, Qt.Key_Return, delay=KEY_DELAY)

    nwGUI.docEditor.wCounterDoc.run()

    # Save the document
    assert nwGUI.docEditor.docChanged()
    assert nwGUI.saveDocument()
    assert not nwGUI.docEditor.docChanged()
    nwGUI.rebuildIndex()

    # Open and view the edited document
    nwGUI.switchFocus(nwWidget.VIEWER)
    assert nwGUI.openDocument(C.hSceneDoc)
    assert nwGUI.viewDocument(C.hSceneDoc)
    assert nwGUI.saveProject()
    assert nwGUI.closeDocViewer()

    # Check the files
    projFile = projPath / "nwProject.nwx"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_nwProject.nwx"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_nwProject.nwx"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile, ignoreStart=(*XML_IGNORE, "<spellCheck"))

    projFile = projPath / "content" / "000000000000f.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_000000000000f.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_000000000000f.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = projPath / "content" / "0000000000010.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000010.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000010.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = projPath / "content" / "0000000000011.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000011.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000011.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    projFile = projPath / "content" / "0000000000012.nwd"
    testFile = tstPaths.outDir / "guiEditor_Main_Final_0000000000012.nwd"
    compFile = tstPaths.refDir / "guiEditor_Main_Final_0000000000012.nwd"
    copyfile(projFile, testFile)
    assert cmpFiles(testFile, compFile)

    # qtbot.stop()

# END Test testGuiMain_Editing


@pytest.mark.gui
def testGuiMain_FocusFullMode(qtbot, nwGUI, projPath, mockRnd):
    """Test toggling focus mode in main window.
    """
    buildTestProject(nwGUI, projPath)
    assert nwGUI.isFocusMode is False

    # Focus Mode
    # ==========

    # No document open, so not allowing focus mode
    assert nwGUI.toggleFocusMode() is False

    # Open a file in editor and viewer
    assert nwGUI.openDocument(C.hSceneDoc)
    assert nwGUI.viewDocument(C.hSceneDoc)

    # Enable focus mode
    assert nwGUI.toggleFocusMode() is True
    assert nwGUI.treePane.isVisible() is False
    assert nwGUI.mainStatus.isVisible() is False
    assert nwGUI.mainMenu.isVisible() is False
    assert nwGUI.viewsBar.isVisible() is False
    assert nwGUI.splitView.isVisible() is False

    # Disable focus mode
    assert nwGUI.toggleFocusMode() is True
    assert nwGUI.treePane.isVisible() is True
    assert nwGUI.mainStatus.isVisible() is True
    assert nwGUI.mainMenu.isVisible() is True
    assert nwGUI.viewsBar.isVisible() is True
    assert nwGUI.splitView.isVisible() is True

    # Full Screen Mode
    # ================

    assert CONFIG.isFullScreen is False
    nwGUI.toggleFullScreenMode()
    assert CONFIG.isFullScreen is True
    nwGUI.toggleFullScreenMode()
    assert CONFIG.isFullScreen is False

    # qtbot.stop()

# END Test testGuiMain_FocusFullMode
