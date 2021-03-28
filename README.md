# Work in progress

# mdCMS is a Markdown-based CMS w/ Flask

## In a nutshell
A lazy and darn simple content managing system. No admin panel, no database setup. Install and run it on your server (change html/css templates to match your tastes), write articles in .md files and upload them in /posts, mdCMS will do the rest.

## How to run / prerequisites
- A running server with root access (ssh...)
- A running front web server like Nginx
- Python 3, obviously
- A running WSGI server like Gunicorn

## How does it work ?
A python thread watch for any file change in /posts folder, which triggers the .md processing.
The .md processing reads new or (already known) modified .md files to inject/update their content in data.json with some added (modifiable) metadatas.
Besides that, it's a Flask micro framework application running and reading this data.json.