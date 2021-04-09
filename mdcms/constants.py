# -*- mode: python ; coding: utf-8 -*-
import os

print (os.getcwd())
MD_PATH     = os.getcwd() + '/posts/'           # .md posts location
MD_RES_PATH = os.getcwd() + '/posts/ressources' # ressources location (images, files..)
JSON_PATH   = os.getcwd() + '/mdcms/data.json'  # data.json location
CHECK_TIME  = 10                                # .md watch loop sleep time