# -*- mode: python ; coding: utf-8 -*-
from flask import Flask, render_template, redirect, request
import jdata
import md

app = Flask(__name__)   # Instance de Flask = WSGI application
jdat = jdata.Jdata()    # Données (articles)


@app.route('/', methods=['GET', 'POST'])         # URL "/" triggers this function
def main():
    return render_template('pages/index.html', posts=jdat.jsondat['posts'])

@app.route('/posts')
def posts():
    return render_template('pages/posts.html', posts=jdat.jsondat['posts'])

@app.route('/post/<int:id>')
def post(id):
    for record in jdat.jsondat['posts']:
        if record['id'] == id:
            return render_template('pages/post.html', post=record)

@app.route('/git')
def git():
    return redirect('https://github.com/hotrooibos')

@app.route('/about')
def about():
    return render_template('pages/about.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


if __name__ == "__main__":    
    md.get_new_posts() # TODO refresh every x hours, ou watch changement dans le dossier des posts
    app.run(host="localhost", port=8080, debug=True)