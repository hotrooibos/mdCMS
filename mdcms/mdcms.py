# -*- mode: python ; coding: utf-8 -*-
from time import sleep
from flask import Flask, render_template, redirect, request
from flask.helpers import send_from_directory
from . import jdata
import time

def app():
    app    = Flask(__name__)                   # Instance de Flask = WSGI application
    jposts = jdata.Jdata().jdat['posts'] # Données (articles)
    
    
    # CONVERT all dates to jj Mon yyyy in jposts to be human-readable
    for v in jposts.values():
        v.update({
            'datecr': time.strftime('%d %b %Y', time.localtime(v.get('datecr'))),
            'dateup': time.strftime('%d %b %Y', time.localtime(v.get('dateup')))
        })


    @app.route('/', methods=['GET', 'POST'])         # URL "/" triggers this function
    def main():
        return render_template('pages/index.j2', posts=jposts)


    @app.route('/posts')
    def posts():
        return render_template('pages/posts.j2', posts=jposts)


    @app.route('/posts/ressources/<path:path>')
    def post_ressources(path):
        return send_from_directory(f'posts/ressources/', path)


    @app.route('/posts/<int:id>')
    def post(id):
        post = jposts[str(id)]
        return render_template('pages/post.j2', post = post)


    @app.route('/git')
    def git():
        return redirect('https://github.com/hotrooibos')


    @app.route('/about')
    def about():
        return render_template('pages/about.j2')


    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.j2'), 404


    return app