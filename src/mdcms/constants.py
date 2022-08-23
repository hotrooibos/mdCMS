import os

# Project ROOT directory - DO NOT TOUCH unless you know what you are doing
ROOTDIR = os.path.dirname(os.path.abspath(__file__)) + '/../..'

"""
Constants / configuration

"""

# Markdown files location
MD_PATH = ROOTDIR + '/posts/'

# Posts' ressources location (images, files..)
MD_RES_PATH = ROOTDIR + '/posts/ressources'

# data.json file location
JSON_PATH = ROOTDIR + '/data.json'

# Default posts' author name
DEFAULT_AUTHOR = 'Antoine'

# Time between two watchdog loop in seconds
# Ex : 10 = search for new/modified Markdown every 10 seconds
CHECK_TIME = 10

# Main language you'll write in
# Only used in the case you are going to translate your posts
# Ex : en, fr, de..
DEFAULT_LANG = 'en'

# Maximum URL lenght for posts
# Only used by auto URL building function
URL_LEN = 30