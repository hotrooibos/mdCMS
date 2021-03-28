# mdCMS is a Markdown-based CMS w/ Flask

## In a nutshell
It's a lazy and darn simple content managing system. No admin panel, no database setup.
Write articles in .md files
While it runs, just put new .md files or update existing ones in /posts folder to update the online content.
That's it.

## How to run / prequerisites
- A running server with root access (ssh...)
- A running front web server like Nginx
- Python 3
- A WSGI server like Gunicorn to run Python apps

## How does it works ?
It's simple.
When one updates the /posts folder, things happen. Actually, a python thread watch for any file change in this folder, and then run the .md processing.
The .md processing reads new or modified .md files to inject/update their content in data.json with some added (modifiable) metadata.
Alongside these things, it's just a Flask microframework application running and reading this data.json.