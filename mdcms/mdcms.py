# -*- mode: python ; coding: utf-8 -*-
from flask         import Flask, render_template, redirect, request
from flask.helpers import send_from_directory
from threading     import Thread
from time          import sleep
from .             import constants, md, jdata 



def mdcms():
    '''
    MDCMS background job
    '''
    while True:
        md.watchdog()
        sleep(constants.CHECK_TIME)



def flaskapp():
    '''
    FLASK web application
    '''
    app = Flask(__name__) # Instance de Flask (WSGI application)

    # START mdCMS thread
    Thread(target=mdcms,
           daemon=True).start()


    @app.route('/', methods=['GET', 'POST'])         # URL "/" triggers this function
    def main():
        return render_template('pages/index.j2',
                               posts=jdata.Jdata().jdat['posts'])


    @app.route('/posts')
    def posts():
        return render_template('pages/posts.j2',
                               posts=jdata.Jdata().jdat['posts'])


    @app.route('/posts/ressources/<path:path>')
    def post_ressources(path):
        return send_from_directory(f'posts/ressources/', path)


    @app.route('/post/<string:__url>')
    def post(__url):

        for v in jdata.Jdata().jdat['posts'].values():
            if v.get('url') == __url:
                return render_template('pages/post.j2',
                                       post=v)

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