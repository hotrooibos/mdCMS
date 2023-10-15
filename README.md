# mdCMS

mdCMS is a simple content managing system built in Python.

No admin panel, no database, simple setup :
1) tweak constants.py
2) run with Gunicorn (```$ gunicorn -c gunicorn.conf.py 'src.mdcms.mdcms:flaskapp()'```)
3) write some articles in Markdown .md files, and place them in the "MD_PATH"

Voila, posts are published.

## Prerequisites
- A running server with root access (Apache, Nginx, Caddy...)
- Python >= 3.7
- Packages : Gunicorn, Flask, Markdown

## Under the hood
- A Flask web app
- A watchdog thread watches for updated/new .md files placed in the MD_PATH
- Posts are loaded in memory at startup
- Commenting management with anti junk (ip ban), comments, likes stored in a json file
- And more features coming...