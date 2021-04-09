# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import jdata
from . import utils
import markdown
from   markdown.extensions import Extension
import os
import zlib

JDAT = jdata.Jdata()
JDAT.read()
# TODO Ajouter paramètre dans data.json : "ressource_path".
# TODO  Si dans .md existe ![](machin.jpg/png..) (cf fonction regex infra),
# TODO  faire la concat de ressource_path et de machin.jpg



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
        md = markdown.Markdown(extensions=['meta','toc','extra','codehilite'])
        
        self.furl    = mdurl
        self.content = md.convert(mddat)

        # Build perma URL
        self.__build_url(fname)

        # Build ID
        if md.Meta.get('id'):
            self.id = md.Meta.get('id')
        else:
            self.__build_id()
            w.append('id')

        # Get or build title
        if md.Meta.get('title'):
            self.title = md.Meta.get('title')[0]
        else:
            self.__build_title()

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
                mdl.insert(0, f'id:{self.id}\n')

            mdl = ''.join(mdl)
            md.seek(0)
            md.write(mdl)



    def __build_id(self):
        '''ID = crc of perma url'''
        n_id = zlib.crc32(self.url.encode('utf-8'))
        self.id = str(n_id)



    def __build_url(self, file_name: str):
        tw = ('with','avec','under',        # "Trash" words list
                'sous','the', 'for')

        url = file_name[:-3]                # Remove .md extension
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



def process_md(__mds: list):
    '''
    Read .md file, get, transform and
    inject its data in data.json
    '''

    for __md in __mds:

        # KNOWN ID in json : update json with
        # possibly updated data from .md
        if __md.id in JDAT.ids:
            maj_post(__md)
            continue # END, process next .md

        
        # UNKNOWN ID in json
        # CREATE json record

        md_dateup = os.stat(__md.furl).st_mtime # m(odification)time

        new_record = {
            __md.id: {
            "title":__md.title,
            "author":__md.author,
            "url":__md.url,
            "datecr":__md.datecr,
            "dateup":md_dateup,
            "content":__md.content
            }
        }
        JDAT.jdat['posts'].update(new_record)


    # WRITE json file
    JDAT.write()



def maj_post(__md: Md):
    '''
    UPDATE posts 
    '''
    JDAT.jdat['posts'][__md.id]['title']   = __md.title
    JDAT.jdat['posts'][__md.id]['author']  = __md.author
    JDAT.jdat['posts'][__md.id]['content'] = __md.content
    JDAT.jdat['posts'][__md.id]['datecr']  = __md.datecr
    JDAT.jdat['posts'][__md.id]['dateup']  = __md.dateup



def watchdog():
    '''
    Polling MD_PATH for .md file change


    '''
    __md_to_process = []

    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':

            __mdurl = f'{const.MD_PATH}/{f}'

            # crée systématiquement un objet pour chaque fichier MD...
            # vérifier plutôt les dates de modif des fichiers ?
            __md    = Md(f, __mdurl)
            
            if str(__md.id) in JDAT.ids:
                # If the .md isn't newer than last known post update
                if __md.dateup <= JDAT.last_chdate:
                        continue
                print(f'Watchdog: update {f}')
            
            else:
                print(f'Watchdog: new post {f}')

            __md_to_process.append(__md)

    if len(__md_to_process) > 0:
        process_md(__md_to_process)
        print(len(__md_to_process), 'post(s) processed')
        
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
    #         if md.title in JDAT.titles:
    #             print(f'| A post with title {md.title} already exists in data.json -> skipping {f}')
    #             continue
    #         if md.sum in JDAT.sums:
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