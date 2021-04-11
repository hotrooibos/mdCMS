# -*- mode: python ; coding: utf-8 -*-
import flask as fk
from flask.helpers import send_from_directory
from threading     import Thread
from time          import sleep, time
from .             import constants, md 
from .jdata        import Jdata as jd

pending_coms = False



def mdcms():
    '''
    MDCMS background job
    '''
    global pending_coms

    while True:
        md.watchdog(pending_coms)
        pending_coms = False
        sleep(constants.CHECK_TIME)     



def check_spam(sender_ip: str) -> int:
    '''
    Comments anti junk
    '''
    banstate = 0

    # Check sender ban state, refuse comment if in bantime
    # State 0  = unknown
    # State 1  = 1 hour ban
    # State 2  = 1 day ban
    # State 3  = 3 days ban
    # State -1 = permanent ban (always refuse comments)
    if sender_ip in jd().jdat['bans']:
        banstate = jd().jdat['bans'][sender_ip]['banstate']
        bantime = jd().jdat['bans'][sender_ip]['bantime']

    if banstate == 1 and (time()-bantime) < 600: #1h
        return 1
    elif banstate == 2 and (time()-bantime) < 172800: #24h
        return 1
    elif banstate in (3) and (time()-bantime) < 259200: #72h
        return 1
    elif banstate == -1:
        return 1

    # Gather all old comments' time recorded from sender
    sender_comments = []

    for v in jd().jdat['comments'].values():
        for i in v:
            if i.get('ip') == sender_ip:
                sender_comments.append(i.get('time'))

    # Tempban him if more than 5 comments in the last 5mn
    if len(sender_comments) > 5:
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
            elif banstate in range(1,3):
                jd().jdat['bans'][sender_ip]['banstate'] += 1
                jd().jdat['bans'][sender_ip]['bantime'] = time()

            # Permanent ban
            elif banstate == 3:
                jd().jdat['bans'][sender_ip]['banstate'] = -1
                jd().jdat['bans'][sender_ip]['bantime'] = time()

            return 1
    
    print(f'Sender has sent {len(sender_comments)} total msg.')
    print('Sent msg:\n', sender_comments)

    return 0



def process_comment(post_id: str,
                    form_data: dict,
                    sender_ip: str):
    '''Create a new comment and add it to pending comments dict'''
    # TODO : js + python : check longueurs
    # TODO : js : check format email (regex)

    global pending_coms

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

    pending_coms = True



def flaskapp():
    '''
    FLASK web application
    '''
    app = fk.Flask(__name__) # Instance de Flask (WSGI application)

    # START mdCMS thread
    Thread(target=mdcms,
           daemon=True).start()


    @app.route('/')         # URL "/" triggers this function
    def main():
        return fk.render_template('pages/index.j2',
                                  posts=jd().jdat['posts'])


    @app.route('/posts')
    def posts():
        return fk.render_template('pages/posts.j2',
                                  posts=jd().jdat['posts'])


    @app.route('/posts/ressources/<path:filename>')
    def post_ressources(filename):
        return send_from_directory(constants.MD_RES_PATH, filename)


    @app.route('/post/<string:url>',
               methods=['GET', 'POST'])
    def post(url):
        # Get wanted post id + content from url
        for k, v in jd().jdat['posts'].items():
            if v.get('url') == url:
                pid = k
                post = v

        # Get comments (old ones + new if POST request)
        coms = None
        for k, v in jd().jdat['comments'].items():
            if k == pid:
                coms = v

        return fk.render_template('pages/post.j2',
                                  post=post,
                                  coms=coms)


    @app.route('/comment',
               methods=['POST'])
    def comment():

        # Build URL from Referer
        referer = fk.request.headers.get("Referer")
        url = referer.split('/')[-1]

        # Get post id from url
        for k, v in jd().jdat['posts'].items():
            if v.get('url') == url:
                pid = k

        sender_ip = fk.request.environ.get('HTTP_X_REAL_IP',
                                           fk.request.remote_addr)

        if check_spam(sender_ip) != 0:
            return

        process_comment(pid, fk.request.form, sender_ip)

        # Get comments including new one
        coms = None
        for k, v in jd().jdat['comments'].items():
            if k == pid:
                coms = v
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