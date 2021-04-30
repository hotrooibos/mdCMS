# -*- mode: python ; coding: utf-8 -*-
import flask as fk
from flask.globals import request
from flask.helpers import send_from_directory
import logging
from os import listdir, stat
from threading import Thread
from time import sleep, time, strftime, localtime
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from . import constants as const
from .md import Md
from .jdata import Jdata as jd



# Logging setup
t = time()
date = strftime('%Y_%m', localtime(t))
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=f'logs/{date}_mdcms.log',
                    filemode='a',
                    format=log_format,
                    datefmt='%Y%m%d %H:%M:%S',
                    level=logging.INFO)
log = logging.getLogger(__name__)

# Mdcms setup
mdb = []            # Markdown posts base
jd().read()         # Read json data
pending_w = False   # Pending writes in json



def watchdog():
    '''Polling MD_PATH for .md file change
   comparing with known MD base (mdb).

    Also, if new data (comment, bans) are
    pending for writing, then write them to json

    Returns the updated MD Base
    '''
    global mdb
    global pending_w

    while True:
        # Initial execution -> process all md
        populate = True if len(mdb) < 1 else False

        # Get all known post url (id) in memory
        known_mds = []
        mdb_last = 0

        for md in mdb:
            known_mds.append(md.url)
            if md.mtime > mdb_last:
                mdb_last = md.mtime

        # Loop over each .md file
        for f in listdir(const.MD_PATH):
            if f[-3:] == '.md':
                fpath = f'{const.MD_PATH}/{f}'
                fmtime = stat(fpath).st_mtime

                # File not updated -> skip
                if not populate and fmtime <= mdb_last:
                    continue

                # Update post in memory
                md = Md(f, fpath)

                if md.url in known_mds:
                    if md.mtime > mdb_last:
                        log.info(f'Update post "{f}"')
                        i = known_mds.index(md.url)
                        mdb[i] = md
                    else:
                        continue

                # Add post in mem
                else:
                    mdb.insert(0, md)
                    log.info(f'Add post "{f}"')

                    # Sort posts by ctime at populate time
                    if populate:
                        mdb.sort(key=lambda x: x.ctime,
                                reverse=True)

        if pending_w:
            jd().write()        # WRITE json
            pending_w = False   # Reset pending

        sleep(const.CHECK_TIME)



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
    
    Return True if IP@ is banned
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
    sender_comtime = []

    for v in jd().jdat['comments'].values():
        for i in v:
            if i.get('ip') == sender_ip:
                sender_comtime.append(i.get('time'))

    # Ban if 5th comment within 5 last minutes
    if len(sender_comtime) > 4:
        deltatime = time() - sender_comtime[-5]

        # If time between now (last comment) and
        # 5th last comment time < 5mn, ban sender
        # and hide ALL his previous comments
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

            # Hide all his previous comments
            for v in jd().jdat['comments'].values():
                for i in v:
                    if i.get('ip') == sender_ip:
                        i['display_status'] = False

            pending_w = True           
            return True

    return False



def process_comment(post_id: str,
                    form_data: dict,
                    sender_ip: str):
    '''Create a new comment
    '''
    global pending_w

    comment = {
        "ip":sender_ip,
        "time":time(),
        "name":form_data['name'],
        "mail":form_data['email'],
        "comm":form_data['comment'],
        "display_status":True
    }

    # First comment for this post
    if not post_id in jd().jdat['comments']:
        comment = {
            post_id: [comment,]
        }
        jd().jdat['comments'].update(comment)

    # Add comment to existing ones for this post
    else:
        jd().jdat['comments'][post_id].append(comment)

    pending_w = True



def remote_addr() -> str:
    '''Return client IP adress even if behind proxy (nginx...)
    '''
    if 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'
    return remote_addr



def get_404_alt(url: str) -> list:
    '''Return posts which url similar to the given 'url' argument.
    '''
    url = url.lower()
    alts = [] # List of Md objects

    for u in Md.urls:
        i = 0
        for word in u.split('_'):
            if url.find(word) != -1:
                i+= 1

            if i == 1: # 1 word match==url match
                for md in mdb:
                    if md.url == u:
                        alts.append(md)
                        break
                break

    return alts



def flaskapp():
    '''FLASK web app
    '''
    app = fk.Flask(__name__) # Instance de Flask (WSGI application)
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # START mdCMS thread
    Thread(target=watchdog, daemon=True).start()


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
        # Hide translation posts from list
        posts = []
        for p in mdb:
            if p.lang == const.DEFAULT_LANG[:2] or \
                    not p.originpost:
                posts.append(p)
        
        return fk.render_template('pages/posts.j2',
                                  posts=posts)


    @app.route('/posts/ressources/<path:filename>')
    def post_ressources(filename):
        return send_from_directory(const.MD_RES_PATH, filename)


    @app.route('/post/<string:url>', methods=['GET'])
    def post(url):
        global mdb

        # Get md wanted in url
        post = next((p for p in mdb if p.url == url), None)
        
        if not post:
            alt = get_404_alt(url)
            fk.abort(404, ("This post doesn't exist", alt))

        # Get translations of this post
        transl = [] # List of translation posts

        for p in mdb:
            # We are in original post, get translated
            if post.lang == const.DEFAULT_LANG[:2] and \
                    p.originpost == post.url and \
                    p.lang != const.DEFAULT_LANG[:2]:
                transl.append(p)

            # We are in a translated post, get original
            elif post.lang != const.DEFAULT_LANG[:2] and \
                    p.url == post.originpost:
                transl.append(p)

        # Get comments (old ones + new if POST request)
        coms = []
        for url, v in jd().jdat['comments'].items():
            if url == post.url:
                coms = v
                # TODO coms_filt = (c for c in v.items() if c.get('display_status') == True)

                break
        

        # Get like count
        likecounter = 0
        for k, v in jd().jdat['likes'].items():
            if k == post.url:
                likecounter = len(v)
            
        return fk.render_template('pages/post.j2',
                                  post=post,
                                  transl=transl,
                                  coms=coms,
                                  likecounter=likecounter)


    @app.route('/comment', methods=['POST'])
    def comment():
        '''Perform comment request from XHR (AJAX)

        Security, anti junk check, comment processing
        '''
        sender_ip = remote_addr()

        if banned(sender_ip) == True:
            return fk.abort(403, "Banned due to suspicious activity")

        form = fk.request.form # FORM DATA

        # Check form validity
        # Already done in JS (client-side) but redo it
        # in Python (server-side) as a security layer
        valid_form(form)
            
        # Get URL from Referer
        referer = fk.request.headers.get("Referer")
        post_url = referer.split('/')[-1]
        
        process_comment(post_url, form, sender_ip)

        # Get comments (olds + new one if valid)
        coms = []
        for url, v in jd().jdat['comments'].items():
            if url == post_url:
                coms = v
                break

        return fk.render_template('layouts/partials/_comments.j2',
                                  coms=coms)


    @app.route('/like', methods=['POST'])
    def like():
        global pending_w

        sender_ip = remote_addr()

        # Get post url from Referer
        referer = fk.request.headers.get("Referer")
        post_url = referer.split('/')[-1]

        likecount = 0

        # First like ever
        if not post_url in jd().jdat['likes'].keys():
            jd().jdat['likes'].update({post_url:[sender_ip]})
            likecount += 1
        # Like / unlike
        else:
            for k, v in jd().jdat['likes'].items():
                if k == post_url:
                    likecount = len(v)

                    # Visitor already liked this post -> unlike
                    if sender_ip in v:
                        v.remove(sender_ip)
                        likecount -= 1

                    # -> like
                    else:
                        v.append(sender_ip)
                        likecount += 1

        pending_w = True # Write un/like in json

        return (str(likecount), 200)


    @app.route('/git')
    def git():
        return fk.redirect('https://github.com/hotrooibos')


    @app.route('/about')
    def about():            
        return fk.render_template('pages/about.j2')


    @app.errorhandler(HTTPException)
    def http_err_handler(error):

        if type(error.description) is str:
            return fk.render_template('errors/error.j2',
                                    code=error.code,
                                    desc=error.description)

        # Tuple = (description, alt posts propositions when 404)
        elif type(error.description) is tuple:
            return fk.render_template('errors/error.j2',
                        code=error.code,
                        desc=error.description[0],
                        alt=error.description[1])

    return app