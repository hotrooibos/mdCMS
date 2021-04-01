# -*- mode: python ; coding: utf-8 -*-
import os

MD_PATH     = os.path.dirname(os.path.realpath(__file__)) + '/posts'    # The current directory of constants.py + /posts
JSON_PATH   = MD_PATH + '/data.json'                                    # File data.json inside MD_PATH
CHECK_TIME  = 600                                                       # Check for new/updated .md every n seconds