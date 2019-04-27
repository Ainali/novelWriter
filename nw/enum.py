# -*- coding: utf-8 -*-
"""novelWriter Enums

 novelWriter – Enums
=====================
 All enum values

 File History:
 Created: 2018-11-02 [0.0.1]

"""

from enum import Enum

class nwItemType(Enum):

    NO_TYPE     = 0
    ROOT        = 1
    FOLDER      = 2
    FILE        = 3
    TRASHFOLDER = 4
    TRASHFILE   = 5

# END Enum nwItemType

class nwItemClass(Enum):

    NO_CLASS  = 0
    NOVEL     = 1
    PLOT      = 2
    CHARACTER = 3
    WORLD     = 4
    TIMELINE  = 5
    OBJECT    = 6
    CUSTOM    = 7

# END Enum nwItemClass

class nwItemLayout(Enum):

    NO_LAYOUT   = 0
    TITLE_PAGE  = 1
    SIMPLE_PAGE = 2
    PARTITION   = 3
    CHAPTER     = 4
    SCENE       = 5
    NOTE        = 6

# END Enum nwItemLayout

class nwItemAction(Enum):

    NO_ACTION   = 0
    ADD_ROOT    = 1
    ADD_FOLDER  = 2
    ADD_FILE    = 3
    MOVE_UP     = 4
    MOVE_DOWN   = 5
    MOVE_TO     = 6
    MOVE_TRASH  = 7
    SPLIT       = 8
    MERGE       = 9
    DELETE      = 10
    DELETE_ROOT = 11
    EMPTY_TRASH = 12
    RENAME      = 13

# END Enum nwItemAction

class nwDocAction(Enum):

    NO_ACTION = 0
    UNDO      = 1
    REDO      = 2
    CUT       = 3
    COPY      = 4
    PASTE     = 5
    BOLD      = 6
    ITALIC    = 7
    U_LINE    = 8
    S_QUOTE   = 9
    D_QUOTE   = 10
    SEL_ALL   = 11
    SEL_PARA  = 12

# END Enum nwDocAction