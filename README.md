# Work in progress

# mdCMS is a Markdown-based cms

## In a nutshell
A lazy and darn simple content managing system. No admin panel, no database setup. Install and run on your server (change html/css templates to match your tastes), write articles in .md files and upload them in /posts, mdCMS will do the rest.

## How to run / prerequisites
- A running server with root access (ssh...)
- A running front web server (Nginx)
- Python >=3.7
- A running WSGI server (Gunicorn)

## Under the hood ?
A python thread watch for any file change in /posts folder. Any new or modified .md file triggers the process.
The .md processing reads new or (already known) modified .md files to inject/update their content in data.json with some added (modifiable) metadatas.
Alonside that, it's a Flask app gathering in-memory data from data.json.