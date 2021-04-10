# -*- mode: python ; coding: utf-8 -*-
from flask         import Flask, render_template, redirect, request
from flask.helpers import send_from_directory
from threading     import Thread
from time          import sleep, time
from .             import constants, md, jdata 

pending_coms = {}



def mdcms():
    '''
    MDCMS background job
    '''
    while True:
        md.watchdog(pending_coms)       # Execute watchdog and send ending
        pending_coms.clear()            # comments if any, then clear pending
        sleep(constants.CHECK_TIME)     



def process_comment(post_id: str, form_data: dict):
    '''Create a new comment and add it to pending comments dict'''
    
    # TODO : js + python : check longueurs
    # TODO : js : check format email (regex)

    comment = {
        "time":time(),
        "name":form_data['name'],
        "mail":form_data['email'],
        "comm":form_data['comment'],
    }

    if post_id in pending_coms:                 # If there is comments for this id
        pending_coms[post_id].append(comment)   # in current pending, then just ADD
                                                # comment TO EXISTING comments for that id
    else:
        comment = {                             # Else, CREATE THE ID in the pending
            post_id: [comment,]                 # and add the comment to it
        }
        pending_coms.update(comment)



def flaskapp():
    '''
    FLASK web application
    '''
    app = Flask(__name__) # Instance de Flask (WSGI application)

    # START mdCMS thread
    Thread(target=mdcms,
           daemon=True).start()


    @app.route('/')         # URL "/" triggers this function
    def main():
        return render_template('pages/index.j2',
                               posts=jdata.Jdata().jdat['posts'])


    @app.route('/posts')
    def posts():
        return render_template('pages/posts.j2',
                               posts=jdata.Jdata().jdat['posts'])


    @app.route('/posts/ressources/<path:filename>')
    def post_ressources(filename):
        return send_from_directory(constants.MD_RES_PATH, filename)


    @app.route('/post/<string:url>', methods=['GET', 'POST'])
    def post(url):

        for k, v in jdata.Jdata().jdat['posts'].items():
            if v.get('url') == url:
                pid = k
                post = v

        coms = None

        for k, v in jdata.Jdata().jdat['comments'].items():
            if k == pid:
                coms = v

        if request.method == "POST":
            process_comment(pid, request.form)

        return render_template('pages/post.j2',
                               post=post,
                               coms=coms)


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