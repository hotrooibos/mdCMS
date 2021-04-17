# -*- mode: python ; coding: utf-8 -*-
import flask as fk
from flask.helpers import send_from_directory
from threading import Thread
from time import sleep, time

from flask.wrappers import Response
from werkzeug.datastructures import ImmutableMultiDict
from . import constants, md
from .jdata import Jdata as jd


mdb = []            # Markdown posts base
jd().read()         # Read json data
pending_w = False   # Comments/bans to be written in json



def mdcms():
    '''CMS background job
    '''
    global mdb
    global pending_w

    while True:
        md.watchdog(mdb, pending_w)
        pending_w = False           # Reset pending
        sleep(constants.CHECK_TIME)



def valid_form(form: ImmutableMultiDict):
    '''Form validation
    
    Raise 403 HTTP errors for any wrong format
    '''

    # NAME must be 2-20 chars
    if not (1 < len(form['name']) < 21):
        return fk.abort(403, "Wrong name length")

    # EMAIL must be 0 (blank), or > 7 chars
    # TODO regex tests
    if (0 < len(form['email']) < 8):  # 8 chars = xx@zz.yy
        return fk.abort(403, "Wrong email format")

    # COMMENT must be 6-1000 chars
    if not (5 < len(form['comment']) < 1001):
        return fk.abort(403, "Wrong text length")



def banned(sender_ip: str) -> bool:
    '''Comments anti junk
    
    Return True if IP@ is banned, False if not
    '''
    global pending_w
    banstate = 0

    # Check sender ban state, refuse comment if in bantime
    # State 0  = no ban
    # State 1 & 2  = 30mn ban
    # State 3  = 1 day ban
    # State 4  = 3 days ban
    # State -1 = permanent ban (always refuse comments)
    if sender_ip in jd().jdat['bans']:
        banstate = jd().jdat['bans'][sender_ip]['banstate']
        bantime = jd().jdat['bans'][sender_ip]['bantime']

        if banstate in (1,2) and (time()-bantime) < 1800: #30mn
            return True
        elif banstate == 3 and (time()-bantime) < 172800: #24h
            return True
        elif banstate == 4 and (time()-bantime) < 259200: #72h
            return True
        elif banstate == -1:
            return True

    # Gather all old comments' time recorded from sender
    sender_comments = []

    for v in jd().jdat['comments'].values():
        for i in v:
            if i.get('ip') == sender_ip:
                sender_comments.append(i.get('time'))

    print(f'Sender has {len(sender_comments)} total msg.')

    # Ban if 5th comment within 5 last minutes
    if len(sender_comments) > 4:
        deltatime = time() - sender_comments[-5]
        print("delta:",deltatime)

        # If time between now (last comment) and
        # 5th last comment time < 5mn, ban sender
        if deltatime < 300:
            # Newbie, add to json bans, state 1
            if banstate == 0:
                newban = {
                    sender_ip: {
                        "banstate": 1,
                        "bantime": time()
                    }
                }
                jd().jdat['bans'].update(newban)

            # Ban harder, states 1 & 2
            elif banstate in (1,2,3):
                jd().jdat['bans'][sender_ip]['banstate'] += 1
                jd().jdat['bans'][sender_ip]['bantime'] = time()

            # Permanent ban
            elif banstate == 4:
                jd().jdat['bans'][sender_ip]['banstate'] = -1
                jd().jdat['bans'][sender_ip]['bantime'] = time()

            pending_w = True           
            return True

    return False



def process_comment(post_id: str,
                    form_data: dict,
                    sender_ip: str):
    '''Create a new comment and add it to pending comments dict
    '''
    global pending_w

    comment = {
        "ip":sender_ip,
        "time":time(),
        "name":form_data['name'],
        "mail":form_data['email'],
        "comm":form_data['comment'],
    }

    if post_id in jd().jdat['comments']:
        jd().jdat['comments'][post_id].append(comment)

    else:
        comment = {                             # Else, CREATE THE ID in the pending
            post_id: [comment,]                 # and add the comment to it
        }
        jd().jdat['comments'].update(comment)

    pending_w = True



def flaskapp():
    '''FLASK web app
    '''
    app = fk.Flask(__name__) # Instance de Flask (WSGI application)

    # START mdCMS thread
    Thread(target=mdcms, daemon=True).start()


    @app.route('/')
    def index():
        return fk.render_template('pages/index.j2',
                                  posts=mdb)


    @app.route('/fullposts')
    def fullposts():
        return fk.render_template('pages/fullposts.j2',
                                  posts=mdb)


    @app.route('/posts')
    def posts():
        return fk.render_template('pages/posts.j2',
                                  posts=mdb)


    @app.route('/posts/ressources/<path:filename>')
    def post_ressources(filename):
        return send_from_directory(constants.MD_RES_PATH, filename)


    @app.route('/post/<string:url>', methods=['GET', 'POST'])
    def post(url):
        global mdb

        # Get md wanted in url
        post = next((p for p in mdb if p.url == url), None)

        # Get comments (old ones + new if POST request)
        coms = None
        for k, v in jd().jdat['comments'].items():
            if k == post.id:
                coms = v

        return fk.render_template('pages/post.j2',
                                  post=post,
                                  coms=coms)


    @app.route('/comment', methods=['POST'])
    def comment():
        '''Perform comment request from XHR (AJAX)

        Security, anti junk check, comment processing
        '''
        sender_ip = fk.request.environ.get('HTTP_X_REAL_IP',
                                           fk.request.remote_addr)

        if banned(sender_ip) == True:
            return fk.abort(403, "Banned")

        form = fk.request.form              # FORM datas

        # Check form validity
        # Already done in JS (client-side) but redo it
        # in Python (server-side) as a security layer
        valid_form(form)
            
        # Build URL from Referer
        referer = fk.request.headers.get("Referer")
        url = referer.split('/')[-1]

        # Get post ID from URL
        pid = next((p.id for p in mdb if p.url == url), None)

        process_comment(pid, form, sender_ip)

        # Get comments including new one
        coms = None
        for k, v in jd().jdat['comments'].items():
            if k == pid:
                coms = v

        # All is OK, return comments
        return fk.render_template('layouts/partials/_comments.j2',
                                  coms=coms)


    @app.route('/git')
    def git():
        return fk.redirect('https://github.com/hotrooibos')


    @app.route('/about')
    def about():
        return fk.render_template('pages/about.j2')


    @app.errorhandler(404)
    def page_not_found(error):
        return fk.render_template('errors/404.j2'), 404


    return app