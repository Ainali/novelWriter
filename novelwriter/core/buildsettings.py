"""
novelWriter – Build Settings Class
==================================
A class to hold build settings for the build tool

File History:
Created: 2023-02-14 [2.1b1]

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
from __future__ import annotations

import uuid
import logging

from enum import Enum

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from novelwriter.common import checkUuid, isHandle
from novelwriter.constants import nwHeadingFormats
from novelwriter.core.item import NWItem
from novelwriter.core.project import NWProject

logger = logging.getLogger(__name__)

# The Settings Template
# =====================
# Each entry contains a tuple on the form:
# (type, default, [min value, max value])

SETTINGS_TEMPLATE = {
    "filter.includeNovel":    (bool, True),
    "filter.includeNotes":    (bool, False),
    "filter.includeInactive": (bool, False),
    "headings.fmtTitle":      (str, nwHeadingFormats.TITLE),
    "headings.fmtChapter":    (str, nwHeadingFormats.TITLE),
    "headings.fmtUnnumbered": (str, nwHeadingFormats.TITLE),
    "headings.fmtScene":      (str, "* * *"),
    "headings.fmtSection":    (str, ""),
    "headings.hideScene":     (bool, False),
    "headings.hideSection":   (bool, True),
    "text.includeSynopsis":   (bool, False),
    "text.includeComments":   (bool, False),
    "text.includeKeywords":   (bool, False),
    "text.includeBody":       (bool, True),
    "format.buildLang":       (str, "en_GB"),
    "format.textFont":        (str, ""),
    "format.textSize":        (int, 12),
    "format.lineHeight":      (float, 1.15, 0.75, 3.0),
    "format.justifyText":     (bool, False),
    "format.stripUnicode":    (bool, False),
    "odt.addColours":         (bool, True),
    "html.addStyles":         (bool, False),
}

SETTINGS_LABELS = {
    "filter":                 QT_TRANSLATE_NOOP("Builds", "Document Types"),
    "filter.includeNovel":    QT_TRANSLATE_NOOP("Builds", "Novel Documents"),
    "filter.includeNotes":    QT_TRANSLATE_NOOP("Builds", "Project Notes"),
    "filter.includeInactive": QT_TRANSLATE_NOOP("Builds", "Inactive Documents"),

    "headings":               QT_TRANSLATE_NOOP("Builds", "Headings"),
    "headings.fmtTitle":      QT_TRANSLATE_NOOP("Builds", "Title Heading"),
    "headings.fmtChapter":    QT_TRANSLATE_NOOP("Builds", "Chapter Heading"),
    "headings.fmtUnnumbered": QT_TRANSLATE_NOOP("Builds", "Unnumbered Heading"),
    "headings.fmtScene":      QT_TRANSLATE_NOOP("Builds", "Scene Heading"),
    "headings.fmtSection":    QT_TRANSLATE_NOOP("Builds", "Section Heading"),
    "headings.hideScene":     QT_TRANSLATE_NOOP("Builds", "Hide Scene"),
    "headings.hideSection":   QT_TRANSLATE_NOOP("Builds", "Hide Section"),

    "text":                   QT_TRANSLATE_NOOP("Builds", "Text Content"),
    "text.includeSynopsis":   QT_TRANSLATE_NOOP("Builds", "Synopsis"),
    "text.includeComments":   QT_TRANSLATE_NOOP("Builds", "Comments"),
    "text.includeKeywords":   QT_TRANSLATE_NOOP("Builds", "Keywords"),
    "text.includeBody":       QT_TRANSLATE_NOOP("Builds", "Body Text"),

    "format":                 QT_TRANSLATE_NOOP("Builds", "Text Format"),
    "format.buildLang":       QT_TRANSLATE_NOOP("Builds", "Build Language"),
    "format.textFont":        QT_TRANSLATE_NOOP("Builds", "Font Family"),
    "format.textSize":        QT_TRANSLATE_NOOP("Builds", "Font Size"),
    "format.lineHeight":      QT_TRANSLATE_NOOP("Builds", "Line Height"),
    "format.justifyText":     QT_TRANSLATE_NOOP("Builds", "Justify Text Margins"),
    "format.stripUnicode":    QT_TRANSLATE_NOOP("Builds", "Replace Unicode Characters"),

    "odt":                    QT_TRANSLATE_NOOP("Builds", "Open Document"),
    "odt.addColours":         QT_TRANSLATE_NOOP("Builds", "Add Highlight Colours"),

    "html":                   QT_TRANSLATE_NOOP("Builds", "HTML"),
    "html.addStyles":         QT_TRANSLATE_NOOP("Builds", "Add CSS Styles"),
}


class FilterMode(Enum):

    UNKNOWN  = 0
    FILTERED = 1
    INCLUDED = 2
    EXCLUDED = 3
    SKIPPED  = 4

# END Enum FilterMode


class BuildSettings:

    def __init__(self):
        self._name = ""
        self._uuid = str(uuid.uuid4())
        self._skipRoot = set()
        self._excluded = set()
        self._included = set()
        self._settings = {k: v[1] for k, v in SETTINGS_TEMPLATE.items()}
        self._changed = False
        return

    ##
    #  Properties
    ##

    @property
    def name(self) -> str:
        return self._name

    @property
    def buildID(self) -> str:
        return self._uuid

    @property
    def changed(self) -> bool:
        return self._changed

    ##
    #  Getters
    ##

    @staticmethod
    def getLabel(key: str) -> str:
        """Extract the label for a specific item.
        """
        return SETTINGS_LABELS.get(key, "ERROR")

    def getValue(self, key: str) -> str | int | bool | float:
        """Get the value for a specific item, or return the default.
        """
        return self._settings.get(key, SETTINGS_TEMPLATE.get(key, (None, None)[1]))

    ##
    #  Setters
    ##

    def setName(self, name: str):
        """Set the build setting display name.
        """
        self._name = str(name)
        return

    def setBuildID(self, value: str | uuid.UUID):
        """Set a UUID build ID.
        """
        value = checkUuid(value, "")
        if not value:
            self._uuid = str(uuid.uuid4())
        elif value != self._uuid:
            self._uuid = value
        return

    def setFiltered(self, tHandle: str):
        """Set an item as filtered.
        """
        self._excluded.discard(tHandle)
        self._included.discard(tHandle)
        self._changed = True
        return

    def setIncluded(self, tHandle: str):
        """Set an item as explicitly included.
        """
        self._excluded.discard(tHandle)
        self._included.add(tHandle)
        self._changed = True
        return

    def setExcluded(self, tHandle: str):
        """Set an item as explicitly excluded.
        """
        self._excluded.add(tHandle)
        self._included.discard(tHandle)
        self._changed = True
        return

    def setSkipRoot(self, tHandle: str, state: bool):
        """Set a specific root folder as skipped or not.
        """
        if state is True:
            self._skipRoot.discard(tHandle)
            self._changed = True
        elif state is False:
            self._skipRoot.add(tHandle)
            self._changed = True
        return

    def setValue(self, key: str, value: str | int | bool | float) -> bool:
        """Set a specific value for a build setting.
        """
        if key not in SETTINGS_TEMPLATE:
            return False
        definition = SETTINGS_TEMPLATE[key]
        if not isinstance(value, definition[0]):
            return False
        if len(definition) == 4:
            value = min(max(value, definition[2]), definition[3])
        self._changed = value != self._settings[key]
        self._settings[key] = value
        logger.debug(f"Build Setting '{key}' set to: {value}")
        return True

    ##
    #  Methods
    ##

    def isFiltered(self, tHandle: str) -> bool:
        return tHandle not in self._included and tHandle not in self._excluded

    def isIncluded(self, tHandle: str) -> bool:
        return tHandle in self._included

    def isExcluded(self, tHandle: str) -> bool:
        return tHandle in self._excluded

    def isRootAllowed(self, tHandle: str) -> bool:
        return tHandle not in self._skipRoot

    def buildItemFilter(self, project: NWProject) -> dict:
        """Return a dictionary of item handles with filter decissions
        applied.
        """
        result: dict[str, tuple[bool, FilterMode]] = {}
        if not isinstance(project, NWProject):
            return result

        incNovel = bool(self.getValue("filter.includeNovel"))
        incNotes = bool(self.getValue("filter.includeNotes"))
        incInactive = bool(self.getValue("filter.includeInactive"))

        for item in project.tree:
            tHandle = item.itemHandle
            if not tHandle:
                continue
            if not isinstance(item, NWItem):
                result[tHandle] = (False, FilterMode.UNKNOWN)
                continue
            if item.isInactiveClass() or (item.itemRoot in self._skipRoot):
                result[tHandle] = (False, FilterMode.SKIPPED)
                continue
            if not item.isFileType():
                result[tHandle] = (False, FilterMode.SKIPPED)
                continue
            if tHandle in self._included:
                result[tHandle] = (True, FilterMode.INCLUDED)
                continue
            if tHandle in self._excluded:
                result[tHandle] = (False, FilterMode.EXCLUDED)
                continue

            isNote = item.isNoteLayout()
            isNovel = item.isDocumentLayout()
            isActive = item.isActive

            byActive = isActive or (not isActive and incInactive)
            byLayout = (isNote and incNotes) or (isNovel and incNovel)

            isAllowed = byActive and byLayout

            result[tHandle] = (isAllowed, FilterMode.FILTERED)

        return result

    def resetChangedState(self):
        """This must be called when the changes to this class has been
        safely saved to file or passed on.
        """
        self._changed = False
        return

    def pack(self) -> dict:
        """Pack all content into a JSON compatible dictionary.
        """
        logger.debug("Collecting build setting for '%s'", self._name)
        return {
            "name": self._name,
            "uuid": self._uuid,
            "settings": self._settings.copy(),
            "included": list(self._included),
            "excluded": list(self._excluded),
            "skipRoot": list(self._skipRoot),
        }

    def unpack(self, data: dict):
        """Unpack a dictionary and populate the class.
        """
        included = data.get("included", [])
        excluded = data.get("excluded", [])
        skipRoot = data.get("skipRoot", [])
        settings = data.get("settings", {})

        self.setName(data.get("name", ""))
        self.setBuildID(data.get("uuid", ""))
        if isinstance(included, list):
            self._included = set([h for h in included if isHandle(h)])
        if isinstance(excluded, list):
            self._excluded = set([h for h in excluded if isHandle(h)])
        if isinstance(skipRoot, list):
            self._skipRoot = set([h for h in skipRoot if isHandle(h)])

        self._settings = {k: v[1] for k, v in SETTINGS_TEMPLATE.items()}
        if isinstance(settings, dict):
            for key, value in settings.items():
                self.setValue(key, value)

        self._changed = False

        return

# END Class BuildSettings
