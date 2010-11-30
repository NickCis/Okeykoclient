#   This file is part of emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys

DIR_SEP = os.sep

if hasattr(sys, "frozen"):
    APP_PATH = os.path.dirname(sys.executable) + DIR_SEP
else:
    APP_PATH = os.path.abspath(os.path.dirname(__file__)) + DIR_SEP

if (os.name != 'nt'): 
    HOME_DIR = os.path.expanduser('~') + DIR_SEP
else:
    HOME_DIR = os.path.expanduser("~").decode(sys.getfilesystemencoding()) + DIR_SEP

CONF_DIR_NAME = '.config' + DIR_SEP + 'Okeykoclient0' + DIR_SEP
CONFIG_DIR = HOME_DIR + CONF_DIR_NAME
CONFIG_DIR_GLOBAL = APP_PATH + 'config' + DIR_SEP
    
THEME_HOME_PATH = CONFIG_DIR + 'themes' + DIR_SEP
THEME_SYSTEM_WIDE_PATH = APP_PATH + 'themes' + DIR_SEP

DEFAULT_THEME_PATH_HOME = THEME_HOME_PATH + 'default' + DIR_SEP
DEFAULT_THEME_PATH = THEME_SYSTEM_WIDE_PATH + 'default' + DIR_SEP


SOUNDS_PATH = THEME_SYSTEM_WIDE_PATH

del os, sys
