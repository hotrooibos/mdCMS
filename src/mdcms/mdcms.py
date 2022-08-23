# MIT License

# Copyright (c) 2022 Antoine Marzin

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import flask as fk
from flask.globals import request
from flask.helpers import send_from_directory
import jinja2
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

"""Mdcms setup
"""

# Markdown posts base
mdb = []    

# Read json data
jd().read()

# Flag for pending writes in json
pending_w = False



def watchdog():
    """Watchdog loop function
    Must be run in a separated thread.

    Jobs :
    - Polls MD_PATH for .md file changes (new or changed)
    comparing with known, in-memory, MD base (mdb)
    - Write data to data.json if new data (comment, bans) are
    pending for writing
    - Returns the updated MD base
    """
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

        # Write pending data into data.json (jd object)
        # And reset flag state
        if pending_w:
            jd().write()
            pending_w = False

        sleep(const.CHECK_TIME)



def valid_form(form: ImmutableMultiDict):
    """Basic form validation
    Raise 403 HTTP error for any invalid format.
    These tests are equally done client-side (JavaScript), so this
    function is basically a second security layer.
    """

    # NAME must be 2-20 characters
    if not (1 < len(form['name']) < 21):
        return fk.abort(403, "Invalid name length")

    # EMAIL must be 0 (blank) or >= 8 chars which is
    # the minimum for a valid email address (xx@zz.yy)
    # TODO regex tests
    if (0 < len(form['email']) < 8):
        return fk.abort(403, "Invalid email format")

    # COMMENT must be 6-1000 chars
    if not (5 < len(form['comment']) < 1001):
        return fk.abort(403, "Invalid text length")



def banned(sender_ip: str) -> bool:
    """Comments anti junk/bot.
    Set different ban states which depends on visitor's (sender)
    comment frequency and ban triggering recidivism.
    Return True if visitor's ip is currently banned.
    """
    global pending_w
    banstate = 0

    # Check sender ban state, refuse comment if in bantime
    # State 0 = no ban
    # State 1 & 2 = 30mn ban
    # State 3 = 1 day ban
    # State 4 = 3 days ban
    # State -1 = permanent ban (always refuse comments)
    if sender_ip in jd().jdat['bans']:
        banstate = jd().jdat['bans'][sender_ip]['banstate']
        bantime = jd().jdat['bans'][sender_ip]['bantime']

        if banstate in (1,2) and (time()-bantime) < 1800:
            return True
        elif banstate == 3 and (time()-bantime) < 172800:
            return True
        elif banstate == 4 and (time()-bantime) < 259200:
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
            pending_w = True           

            # Hide all his previous comments
            for v in jd().jdat['comments'].values():
                for i in v:
                    if i.get('ip') == sender_ip:
                        i['display_status'] = False

            # Newbie, add to json bans, state 1
            if banstate == 0:
                newban = {
                    sender_ip: {
                        "banstate": 1,
                        "bantime": time()
                    }
                }
                jd().jdat['bans'].update(newban)
                return True

            # Ban harder, states 1 & 2
            elif banstate in (1,2,3):
                jd().jdat['bans'][sender_ip]['banstate'] += 1
                jd().jdat['bans'][sender_ip]['bantime'] = time()
                return True

            # Permanent ban
            elif banstate == 4:
                jd().jdat['bans'][sender_ip]['banstate'] = -1
                jd().jdat['bans'][sender_ip]['bantime'] = time()
                return True

    return False # Not banned



def comment_digest(post_id: str,
                   form_data: dict,
                   sender_ip: str):
    """Process a new comment
    Make a json data object with given comment informations
    and prepare for further writting in json file
    """
    global pending_w

    # Create a dict with key:value json format
    # Which will be written in json data file
    comment = {
        "ip":sender_ip,
        "time":time(),
        "name":form_data['name'],
        "mail":form_data['email'],
        "comm":form_data['comment'],
        "display_status":True
    }

    # If this is t the first comment for this post,
    # create a new section in the json for this post
    if not post_id in jd().jdat['comments']:
        comment = {
            post_id: [comment,]
        }
        jd().jdat['comments'].update(comment)

    # Add comment to existing ones for this post
    else:
        jd().jdat['comments'][post_id].append(comment)

    # Activate flag for writing in json in watchdog thread
    pending_w = True



def remote_addr() -> str:
    """Return client IP address even if behind proxy (nginx...)
    """
    if 'X-Forwarded-For' in request.headers:
        remote_addr = request.headers.getlist('X-Forwarded-For')[0].rpartition(' ')[-1]
    else:
        remote_addr = request.remote_addr or 'untrackable'

    return remote_addr



def get_404_alt(url: str) -> list:
    """Return posts (dict of Md objects) which
    url similar to the given 'url' argument.
    """
    url = url.lower()
    alt_mds = []

    # Parses every loaded Mds' url
    # Compare each word of the url with others Md
    # Keep the url if at least 1 word matches
    # Returns a dict of matching urls
    for u in Md.urls:
        i = 0
        for word in u.split('_'):
            if url.find(word) != -1:
                i+= 1

            # 1 word match == url match
            if i == 1:
                for md in mdb:
                    if md.url == u:
                        alt_mds.append(md)
                        break
                break

    return alt_mds



def flaskapp():
    """Flask web application
    Application entry point, used as Gunicorn parameter.
    Example :
        gunicorn  -c ./gunicorn.conf.py 'mdcms.mdcms:flaskapp()'
    """
    # Create instance WSGI application (Flask)
    app = fk.Flask(__name__)

    # Jinja presets to avoid weird HTML formating
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Start a separate thread for the watchdog loop function
    Thread(target=watchdog, daemon=True).start()


    @app.context_processor
    def utility_processor():
        """Flask utility "global" variables,
        callable from any template
        """
        utilvars = {
            "curr_year": strftime('%Y')
        }

        return dict(utilvars=utilvars)


    @app.route('/')
    def index():
        """Website home/root route
        """
        return fk.render_template('pages/index.j2',
                                  posts=mdb)


    @app.route('/<string:url>')
    def page(url):
        """Default page renderer
        Render requested page (url) if it exists,
        except for "index" which is used for home/root
        """
        try:
            if url == 'index':
                return fk.abort(404)
                
            return fk.render_template(f'pages/{url}.j2')
        
        except jinja2.exceptions.TemplateNotFound:
            fk.abort(404)
            

    @app.route('/fullposts')
    def fullposts():
        """/fullposts url route
        """
        return fk.render_template('pages/fullposts.j2',
                                  posts=mdb)


    @app.route('/posts')
    def posts():
        """/posts url route, list of all published posts
        Hide translation posts from the list.
        """
        posts = []
        for p in mdb:
            if p.lang == const.DEFAULT_LANG[:2] or \
                    not p.originpost:
                posts.append(p)
        
        return fk.render_template('pages/posts.j2',
                                  posts=posts)


    @app.route('/posts/ressources/<path:filename>')
    def post_ressources(filename):
        """Route for ressources (images, videos...)
        """
        return send_from_directory(const.MD_RES_PATH, filename)


    @app.route('/post/<string:url>', methods=['GET'])
    def post(url):
        """Route for specific post.
        """
        global mdb

        # Get post/md specified in url
        post = next((p for p in mdb if p.url == url), None)
        
        # Return 404 if not found
        if not post:
            alt = get_404_alt(url)
            fk.abort(404, ("This post doesn't exist", alt))

        # Loop over existing posts and get
        # translations for this post, if any
        transl = []
        for p in mdb:
            # Visitor is in original post -> get translated
            if post.lang == const.DEFAULT_LANG[:2] and \
                    p.originpost == post.url and \
                    p.lang != const.DEFAULT_LANG[:2]:
                transl.append(p)

            # Visitor is in a translated post -> get original
            elif post.lang != const.DEFAULT_LANG[:2] and \
                    p.url == post.originpost:
                transl.append(p)

        # Get visitor's ban state
        sender_ip = remote_addr()
        ban = banned(sender_ip)

        # Get this post comments (unfiltered)
        unfltrd_coms = []
        for url, v in jd().jdat['comments'].items():
            if url == post.url:
                unfltrd_coms = v
                break

        # Gather comments to display (e.g. skip banned)
        coms = []
        for c in unfltrd_coms:
            if not c['display_status']:
                continue
            coms.append(c)      

        # Get like count
        likecounter = 0
        for k, v in jd().jdat['likes'].items():
            if k == post.url:
                likecounter = len(v)

        # Return rendered post with translation link (if any),
        # visitor's ban state, comments and like counter
        return fk.render_template('pages/post.j2',
                                  post=post,
                                  transl=transl,
                                  ban=ban,
                                  coms=coms,
                                  likecounter=likecounter)


    @app.route('/comment', methods=['POST'])
    def comment():
        """Perform comment request from XHR (AJAX)
        Security, anti junk check, comment digest.
        """
        sender_ip = remote_addr()
        ban = banned(sender_ip)

        if ban == True:
            httpcode = 403
        else:
            httpcode = 200

        # Get form raw data
        form = fk.request.form

        # Check form validity
        # Already done in JS (client-side) but redo it
        # in Python (server-side) as a security layer
        valid_form(form)
            
        # Get URL from Referer
        referer = fk.request.headers.get('Referer')
        post_url = referer.split('/')[-1]
        
        # Process comment only if user is not banned
        if httpcode == 200 :
            comment_digest(post_url, form, sender_ip)

        # Get comments (olds + new if not banned)
        coms = []
        for url, v in jd().jdat['comments'].items():
            if url == post_url:
                coms = v
                break
        
        # Return comment flow + http code (ban status)
        return fk.render_template('layouts/partials/_comflow.j2',
                                  coms=coms), httpcode


    @app.route('/like', methods=['POST'])
    def like():
        """Perform like request from XHR (AJAX)
        """
        global pending_w

        sender_ip = remote_addr()

        # Get post url from Referer
        referer = fk.request.headers.get('Referer')
        post_url = referer.split('/')[-1]

        likecount = 0

        # Very first like for this post, so create a new
        # section for this post's likes in json structure
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

        # Set flag for writing in json
        pending_w = True

        # Return the like count as a string
        return (str(likecount), 200)


    @app.route('/git')
    def git():
        """Route for /git, a simple redirection
        """
        return fk.redirect('https://github.com/hotrooibos')


    @app.errorhandler(HTTPException)
    def http_err_handler(error):
        """HTTP errors handler
        Return rendered template for errors.
        """
        # If the error's description is a string,
        # render a simple error page
        if type(error.description) is str:
            return fk.render_template('errors/error.j2',
                                    code=error.code,
                                    desc=error.description)

        # If the error's description is a tuple (description, alt
        # posts propositions when 404), render error page
        # with other posts propositions.
        elif type(error.description) is tuple:
            return fk.render_template('errors/error.j2',
                        code=error.code,
                        desc=error.description[0],
                        alt=error.description[1])


    return app