# -*- mode: python ; coding: utf-8 -*-
from time import sleep
from flask import Flask, render_template, redirect, request
import jdata
import md
import threading
import time

app = Flask(__name__)   # Instance de Flask = WSGI application
jdat = jdata.Jdata()    # Données (articles)


@app.route('/', methods=['GET', 'POST'])         # URL "/" triggers this function
def main():
    return render_template('pages/index.j2', posts=jdat.jsondat['posts'])

@app.route('/posts')
def posts():
    return render_template('pages/posts.j2', posts=jdat.jsondat['posts'])

@app.route('/post/<int:id>')
def post(id):
    post = jdat.jsondat['posts'][str(id)]
    return render_template('pages/post.j2',
                           title   = post['title'],
                           datecr  = time.strftime('%Y-%m-%d %H:%M', time.localtime(post['datecr'])),
                           dateupd = time.strftime('%Y-%m-%d %H:%M', time.localtime(post['dateupd'])),
                           author  = post['author'],
                           content = post['content'])

@app.route('/git')
def git():
    return redirect('https://github.com/hotrooibos')

@app.route('/about')
def about():
    return render_template('pages/about.j2')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.j2'), 404


if __name__ == "__main__":    

    t = threading.Timer(1, md.watchdog)
    t.start()

    
    app.run(host="localhost", port=8080, debug=True)



    # p1 = Process(target=lambda: print, args=('lol',))
    # p2 = Process(target=tez, args=('julien',))
    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()