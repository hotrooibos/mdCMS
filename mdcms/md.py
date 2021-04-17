# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import utils
from .jdata import Jdata as jd
from markdown import Markdown
import os
from time import time
import uuid



class Md:
    '''Markdown document class.

    File name and URL strings to .md file in argument.
    
    Usage:

        mdfile = Md('readme.md', '/home/antoine/readme.md')
    '''
    urls = []

    def __init__(self, fname: str, mdurl: str):

        # Read .md file and make attributes from its content
        with open(file=mdurl,
                  mode='r',
                  encoding='utf-8') as mdf:
            mddat = mdf.read()

        wmd = [] # Datas to write to .md
        md = Markdown(extensions=['meta','toc','extra','codehilite'])
        
        self.furl = mdurl
        self.content = md.convert(mddat)
        self.toc = md.toc
        self.id = None
        self.title = None
        self.author = const.DEFAULT_AUTHOR
        self.url = None
        self.datecr = None
        self.dateup = os.stat(self.furl).st_mtime
        self.lang = const.DEFAULT_LANG
        self.originpost = None
        self.cat = None

        # Build ID
        if md.Meta.get('id'):
            if self.checkid(md.Meta.get('id')[0]) == 0:
                self.id = md.Meta.get('id')[0]
            else:
                self.id = str(uuid.uuid4())
                wmd.append(('id', self.id))
                # TODO et l'ancien ID pourri n'est pas suppr ?
        else:
            self.id = str(uuid.uuid4())
            wmd.append(('id', self.id))

        # Get or build title
        if md.Meta.get('title'):
            self.title = md.Meta.get('title')[0]
        else:
            self.title = self.build_title()
            wmd.append(('title', self.title))

        # Build perma URL from title
        self.url = self.build_url()

        # Get author from file or consts
        if md.Meta.get('author'):
            self.author = md.Meta.get('author')[0]
        else:
            wmd.append(('author', const.DEFAULT_AUTHOR))

        # Get language (optional)
        if md.Meta.get('lang'):
            self.lang = md.Meta.get('lang')[0]

            # Get original/translated post UUID if post lang
            # is different from the default CMS writing
            # language (cconst.DEFAULT_LANG)
            if self.lang != const.DEFAULT_LANG[:2]:
                if md.Meta.get('originpost'):
                    self.originpost = md.Meta.get('originpost')[0]
                else:
                    wmd.append(('originpost', ""))
        else:
            wmd.append(('lang', const.DEFAULT_LANG[:2]))

        # Get categories (optional)
        if md.Meta.get('categories'):
            self.cat = md.Meta.get('categories')[0]
        else:
            wmd.append(('categories', ""))

        # Write datecr from file stats into
        # md body if not given in metadatas
        if md.Meta.get('datecr'):
            self.datecr = md.Meta.get('datecr')[0]
            if type(self.datecr) == str:
                self.datecr = utils.to_epoch(self.datecr)
        else:
            self.datecr = os.stat(self.furl).st_mtime
            wmd.append(('datecr', utils.to_datestr(self.datecr)))

        if len(wmd) > 0:
            self.write(wmd)



    @staticmethod
    def checkid(id) -> int:
        '''Check .md ID format.

        Return 0 if UUID compliant.
        '''
        try:
            if uuid.UUID(id).version == 4:
                return 0
            else:
                return 1

        except ValueError:
            return 1



    def write(self, data_to_write: list):
        '''Write metadatas to .md file
        '''
        w = data_to_write

        # WRITE ctime(datecr) to .md metadata header
        with open(self.furl,
                  mode='r+',
                  encoding='utf-8') as md:
            mdl = md.readlines()

            # Loop into list of data to be written in md
            # d = tuples (tag, data)
            # example : ("title", "My first post !")
            for d in data_to_write:

                # ID to be written ?
                # Remove any already-present ID
                if d[0] == 'id':
                    for i, l in enumerate(mdl):
                        if l[:3] == 'id:':
                            mdl.pop(i)

                mdl.insert(0, f'{d[0]}:{d[1]}\n')

            mdl = ''.join(mdl)
            md.seek(0)
            md.write(mdl)



    def build_url(self) -> str:
        '''Build URL from the title

        Replaces spaces by underscores, clear trash
        words and dashes, makes it short, process dupes
        and translated posts the right way.'''

        tw = ('with','avec','under',        # "Trash words" list
              'sous','the', 'for')

        url = self.title
        url = url.replace('-', '')          # Remove dashes
        wds = url.split(' ')                # Make list from str

        for w in list(wds):                 # Parse words
            if (len(w) < 3) or (w in tw):   # Rm short / trash words
                wds.remove(w)

        url = '_'.join(wds)                 # Make string
        url = url[:20]                      # Limit length

        # Clean '_' and 1-letter endings
        while (url[-1:] == '_') or (url[-2:-1] == '_'):
            url = url[:-1]

        url = url.lower()                   # Lower case

        # Dupe detection
        urlf = url

        if url in Md.urls:

            # If translation of another post
            # Might never be used as the title is supposed
            # to be translated too
            if self.lang and self.lang != const.DEFAULT_LANG:
                urlf = f'{self.lang[:2]}_{url}'
            
            # True duplicate : add a number
            else:
                nb = Md.urls.count(url)
                urlf = f'{url}{nb}'         # Add count to name

        Md.urls.append(url)                 # Add to url list

        return urlf



    def build_title(self):
        with open(self.furl,
                  mode='r+',
                  encoding='utf-8') as md:
            mdl = md.readlines()

        titl = None

        for l in mdl:
            if l[:2] == '# ':
                titl = l[2:]
                break
            elif l[:3] == '## ':
                titl = l[3:]
                break
            elif l[:4] == '### ':
                titl = l[4:]
                break
            elif l[:5] == '#### ':
                titl = l[5:]
                break
        
        if titl:
            titl = titl.replace('\n','')
            return titl

        # Not a single title in .md, rly ?
        else:
            return f'Post id {self.id}'



def load_md(mds: list):
    '''Load/update md datas in memory
    '''

    for md in mds:

        # ID already loaded -> update post in mem
        if md.id in Md.ids:
            update(md)
            continue # END, process next .md

        # Unknown ID in mem -> ADD new md post in mem
        md_dateup = os.stat(md.furl).st_mtime # m(odification)time

        new_record = {
            md.id: {
            "title":md.title,
            "author":md.author,
            "url":md.url,
            "datecr":md.datecr,
            "dateup":md_dateup,
            "lang":md.lang,
            "originpost":md.originpost,
            "cat":md.cat,
            "content":md.content,
            }
        }
        Md.mdb.update(new_record)



def watchdog(mdb: list=[],
             pending_w: bool=None) -> list:
    '''Polling MD_PATH for .md file change
   comparing with known MD base (mdb).

    Also, if new data (comment, bans) are
    pending for writing, then write them to json

    Returns the updated MD Base
    '''
    # Populate (1st watchdog execution) -> process all md
    populate = True if len(mdb) < 1 else False

    # Get all known post ids in memory
    mdb_ids = []
    mdb_last = 0

    for md in mdb:
        mdb_ids.append(md.id)
        if md.dateup > mdb_last:
            mdb_last = md.dateup

    # Loop over each .md file
    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':

            fpath = f'{const.MD_PATH}/{f}'
            fdateup = os.stat(fpath).st_mtime

            if not populate and fdateup < mdb_last:
                continue      # File not updated -> skip

            md = Md(f, fpath)
            
            # Update post in memory
            if md.id in mdb_ids:
                if md.dateup > mdb_last:
                    print(f'Watchdog: update {f}')
                    i = mdb_ids.index(md.id)
                    mdb[i] = md
                else:
                    continue
            
            # Add post in mem
            else:
                mdb.insert(0, md)
                print(f'Watchdog: new post {f}')

                # Sort posts by datecr at populate time
                if populate:
                    mdb.sort(key=lambda x: x.datecr,
                             reverse=True)

    print(f'{utils.to_datestr(time())} - {len(mdb)} posts in mdb')

    if pending_w:
        jd().write()    # WRITE json

    return mdb    


    

    # def md_checkup():
    '''
    Vérif complète des md.

    TODO Loop sur tous les fichiers md comportant un id, pour vérifier qu'il
    existe bien un post à l'id correspondant dans le JSON
    S'il existe un id, vérifier que 1) la date de création est ==,
    2) le checksum(title + content) est ==
    '''
    # for f in os.listdir(const.MD_PATH):
    #     mdurl = f'{const.MD_PATH}/{f}'

    #     if f[-3:] == '.md':     
    #         md = Md(mdurl)

    #         # SKIP file if a post with same title or checksum exists in JSON data
    #         if md.title in jd().titles:
    #             print(f'| A post with title {md.title} already exists in data.json -> skipping {f}')
    #             continue
    #         if md.sum in jd().sums:
    #             print(f'| A post with the same content as {f} exists in data.json -> skipping {f}')
    #             continue


    # @staticmethod
    # def process_ressources(content):
    '''
    Lire le contenu du .md, puis vérifier la présence de lignes
    au format ![*](*.png/jpg/gif/svg)
    '''
    # In content, find regex ![*](*.jpg) or one of the others formats
    # The * preceding extension only accepts alphanumeric, dash and underscore chars
    # The goal here is to detect simple filenames (without url format like https://...)
    #  which means they are local images
    # Ex : ![](hellow.svg), ![A landscape](landsc.png), etc.
        # import re
        # x = re.findall("!\[.*\]\([a-zA-ZÀ-ÿ0-9_-]*\.(?:jpg|gif|png|svg)\)", content)

        # for i in x:
        #     print(i, 'non traité')