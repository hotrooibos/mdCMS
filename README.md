# mdCMS
A simple content managing system built in Python.
No admin panel, no database, simple setup :
1) tweak constants.py
2) run with Gunicorn
3) write some articles in Markdown .md files, and place them in the "MD_PATH"

Voilà, posts are published.

## Prerequisites
- A running server with root access, eventually a front web server like Nginx
- Python >= 3.7
- Gunicorn, Flask, Markdown packages

## Under the hood
- A Flask web app
- A watchdog thread watches for updated/new .md files placed in the MD_PATH
- All posts are loaded in memory at startup
- Commenting management with anti junk (ip ban), comments, likes stored in a json file
- More coming...