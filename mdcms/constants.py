# -*- mode: python ; coding: utf-8 -*-
import os

# Do not touch this unless you know what you are doing
ROOTDIR        = os.path.dirname(os.path.abspath(__file__)) + '/..'

# CUSTOMIZE THESE CONSTANTS
MD_PATH        = ROOTDIR + '/posts/'            # .md posts location
MD_RES_PATH    = ROOTDIR + '/posts/ressources'  # Posts' ressources location (images, files..)
JSON_PATH      = ROOTDIR + '/mdcms/data.json'   # data.json location
DEFAULT_AUTHOR = "Antoine"
CHECK_TIME     = 10                             # .md watch loop sleep time (seconds)
DEFAULT_LANG   = "en"                           # en, fr, de..