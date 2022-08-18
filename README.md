# mdCMS is a CMS where articles are written in Markdown
A work in progress personal content managing system build on top of Flask and Python.
No admin panel, no database, simple setup : tweak constants.py, run, write Markdown articles and place them in the "MD_PATH".

## Prerequisites
- A running server with root access, eventually a front web server like Nginx
- Python >= 3.7
- Gunicorn, Flask, Markdown packages

## Under the hood
- A Flask web app
- A watchdog loads/updates .md files placed in the MD_PATH, any new or modified .md file triggers the process
- All posts are loaded in memory at startup
- Commenting management with anti junk (ip ban), comments, likes stored in a json file
- More coming...