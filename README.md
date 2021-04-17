# mdCMS is a Markdown-based cms
A work in progress personal content managing system made in Python and Flask.
No admin panel, no database setup.
Simple setup : tweak constants.py, run, write Mardown articles stored in the MD_PATH, Done.

## Prerequisites
- A running server with root access
- A running front web server (Nginx)
- Python >=3.7

## Under the hood ?
- A Flask web app.
- A thread load/update .md files placed in the MD_PATH. Any new or modified .md file triggers the process.
All posts are stored in memory at startup.
- Commenting management with anti junk, comments stored in a json file
- IP ban management, stored in json
- More coming