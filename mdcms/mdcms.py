# -*- mode: python ; coding: utf-8 -*-
from time import sleep
from flask import Flask, render_template, redirect, request
from flask.helpers import send_from_directory
from . import jdata
import time

def app(testing: bool = False):
    app = Flask(__name__)   # Instance de Flask = WSGI application
    jdat = jdata.Jdata()    # Données (articles)


    @app.before_request
    def my_method():
        remote_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        print("remote ip :", remote_ip)


    @app.route('/', methods=['GET', 'POST'])         # URL "/" triggers this function
    def main():
        return render_template('pages/index.j2', posts=jdat.jsondat['posts'])


    @app.route('/posts')
    def posts():
        return render_template('pages/posts.j2', posts=jdat.jsondat['posts'])


    @app.route('/posts/ressources/<path:path>')
    def post_ressources(path):
        return send_from_directory(f'posts/ressources/', path)


    @app.route('/posts/<int:id>')
    def post(id):
        post = jdat.jsondat['posts'][str(id)]
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