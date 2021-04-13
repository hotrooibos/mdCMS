# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import utils
from .jdata              import Jdata as jd
from markdown            import Markdown
import os
import uuid

jd().read()



class Md:
    '''
    Markdown document object.

    File name and URL strings to .md file in argument.

    Usage:
    >>>  mdfile = Md('readme.md', '/home/antoine/readme.md')
    '''
    __urls = []


    def __init__(self, fname: str, mdurl: str):

        # Read .md file and make attributes from its content
        with open(file     = mdurl,
                  mode     = 'r',
                  encoding = 'utf-8') as mdf:
            mddat = mdf.read()

        w = [] # Datas to write to .md
        md = Markdown(extensions=['meta','toc','extra','codehilite'])
        
        self.furl    = mdurl
        self.content = md.convert(mddat)

        # Build ID
        if md.Meta.get('id'):
            if self.checkid(md.Meta.get('id')[0]) == 0:
                self.id = md.Meta.get('id')[0]
            else:
                self.id = str(uuid.uuid4())
                w.append('id')
        else:
            self.id = str(uuid.uuid4())
            w.append('id')

        # Get or build title
        if md.Meta.get('title'):
            self.title = md.Meta.get('title')[0]
        else:
            self.__build_title()

        # Build perma URL from title
        self.__build_url()

        # Get author from file or consts
        if md.Meta.get('author'):
            self.author = md.Meta.get('author')[0]
        else:
            self.author = const.DEFAULT_AUTHOR

        # Get categories (optional)
        if md.Meta.get('categories'):
            self.cat = md.Meta.get('categories')[0]

        self.dateup  = os.stat(self.furl).st_mtime
        self.toc     = md.toc

        # Add creation date from file stats if not given in metadatas
        if md.Meta.get('datecr'):
            self.datecr = md.Meta.get('datecr')[0]
            if type(self.datecr) == str:
                self.datecr = utils.to_epoch(self.datecr)
        else:
            self.datecr = os.stat(self.furl).st_ctime
            w.append('datecr')

        if len(w) > 0:
            self.__write(w)



    @staticmethod
    def checkid(id) -> int:
        ''' Check .md ID format.

        Return 0 if UUID compliant.
        '''
        try:
            if uuid.UUID(id).version == 4:
                return 0
            else:
                return 1

        except ValueError:
            return 1



    def __write(self, data_to_write: list):
        w = data_to_write

        # WRITE ctime(datecr) to .md metadata header
        with open(self.furl,
                  mode='r+',
                  encoding='utf-8') as md:
            mdl = md.readlines()

            if 'datecr' in w:
                datestr = utils.to_datestr(self.datecr)
                mdl.insert(0, f'datecr:{datestr}\n')

            if 'id' in w:
                for i, l in enumerate(mdl):
                    if l[:3] == 'id:':
                        mdl.pop(i)
                mdl.insert(0, f'id:{self.id}\n')

            mdl = ''.join(mdl)
            md.seek(0)
            md.write(mdl)



    def __build_url(self):
        tw = ('with','avec','under',        # "Trash" words list
                'sous','the', 'for')

        url = self.title
        url = url.replace('-', '')          # Remove dashes
        wds = url.split(' ')                # Make list from str

        for w in list(wds):
            if (len(w) < 3) or (w in tw):   # Rm short / trash words
                wds.remove(w)
        
        url = '_'.join(wds)                 # Make string
        url = url[:20]                      # Limit length

        # Clean '_' and 1-letter endings
        while (url[-1:] == '_') or (url[-2:-1] == '_'):
            url = url[:-1]

        url = url.lower()                   # Lower case

        # Dupe workaround
        urlf = url
        if url in Md.__urls:
            __nb = Md.__urls.count(url)
            urlf = f'{url}{__nb}'           # Add count to name

        Md.__urls.append(url)               # Add to url list

        self.url = urlf



    def __build_title(self):
        with open(self.furl,
                  mode='r+',
                  encoding='utf-8') as md:
            mdl = md.readlines()

        for l in mdl:
            if l[:2] == '# ':
                self.title = l[2:]
                break
            elif l[:3] == '## ':
                self.title = l[3:]
                break
            elif l[:4] == '### ':
                self.title = l[4:]
                break
            elif l[:5] == '#### ':
                self.title = l[5:]
                break

            # Not a single title in .md ?
            self.title = f'Post id {self.id}'



def process_md(mds: list):
    '''
    Read .md file, get, transform and
    inject its data in data.json
    '''

    for md in mds:

        # KNOWN ID in json : update json with
        # possibly updated data from .md
        if md.id in jd().ids:
            maj_post(md)
            continue # END, process next .md

        # UNKNOWN ID in json
        # CREATE json record

        md_dateup = os.stat(md.furl).st_mtime # m(odification)time

        new_record = {
            md.id: {
            "title":md.title,
            "author":md.author,
            "url":md.url,
            "datecr":md.datecr,
            "dateup":md_dateup,
            "content":md.content,
            "comments":[]
            }
        }
        jd().jdat['posts'].update(new_record)

    # WRITE json file
    jd().write()



def maj_post(md: Md):
    '''
    UPDATE posts 
    '''
    jd().jdat['posts'][md.id]['title']   = md.title
    jd().jdat['posts'][md.id]['author']  = md.author
    jd().jdat['posts'][md.id]['content'] = md.content
    jd().jdat['posts'][md.id]['datecr']  = md.datecr
    jd().jdat['posts'][md.id]['dateup']  = md.dateup



def watchdog(pending_write: bool):
    '''
    Polling MD_PATH for .md file change

    Also, if new data (comment, bans..) are
    pending for writing, then write them to json
    '''
    __md_to_process = []

    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':

            __mdurl = f'{const.MD_PATH}/{f}'

            # crée systématiquement un objet pour chaque fichier MD...
            # vérifier plutôt les dates de modif des fichiers ?
            __md    = Md(f, __mdurl)
            
            if str(__md.id) in jd().ids:
                # If the .md isn't newer than last known post update
                if __md.dateup <= jd().last_chdate:
                        continue
                print(f'Watchdog: update {f}')
            
            else:
                print(f'Watchdog: new post {f}')

            __md_to_process.append(__md)

    if len(__md_to_process) > 0:
        process_md(__md_to_process)
        print(len(__md_to_process), 'post(s) processed')
    
    if pending_write:
        jd().write()    # WRITE json

    return
    


    
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