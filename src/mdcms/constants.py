import os

# DO NOT TOUCH this unless you know what you are doing
ROOTDIR        = os.path.dirname(os.path.abspath(__file__)) + '/../..'

# Constants / configuration
MD_PATH        = ROOTDIR + '/posts/'            # .md posts location
MD_RES_PATH    = ROOTDIR + '/posts/ressources'  # Posts' ressources location (images, files..)
JSON_PATH      = ROOTDIR + '/data.json'   # data.json location
DEFAULT_AUTHOR = 'Antoine'
CHECK_TIME     = 10                             # .md watch loop sleep time (seconds)
DEFAULT_LANG   = 'en'                           # en, fr, de..