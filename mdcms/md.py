# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import jdata
from . import utils
import zlib
import markdown
from   markdown.extensions import Extension
import os
import time

JDAT = jdata.Jdata()
JDAT.read()

# TODO Ajouter un paramètre dans data.json : "ressource_path".
# TODO  Si dans le .md un ![](machin.jpg/png..) (cf fonction regex infra),
# TODO  faire la concaténation de ressource_path et de machin.jpg pour trouver les ressources



class Md:
    '''
    Markdown document object.

    File name and URL strings to .md file in argument.

    Usage:
    >>>  mdfile = Md('readme.md', '/home/antoine/readme.md')
    '''
    def __init__(self, fname: str, mdurl: str):

        # Read .md file and make attributes from its content
        with open(file     = mdurl,
                  mode     = 'r',
                  encoding = 'utf-8') as mdf:
            __mddat = mdf.read()

        __md = markdown.Markdown(extensions=['meta','toc','extra'])
        
        self.furl    = mdurl
        self.content = __md.convert(__mddat)

        if __md.Meta.get('title'):
            self.title = __md.Meta.get('title')[0]
        else:
            self.title = self.content[:15]

        if __md.Meta.get('author'):
            self.author = __md.Meta.get('author')[0]

        if __md.Meta.get('categories'):
            self.cat = __md.Meta.get('categories')[0]

        if __md.Meta.get('date') :          
            self.datecr = __md.Meta.get('date')[0]
            if type(self.datecr) == str:
                self.datecr = utils.to_epoch(self.datecr)

        self.dateup  = os.stat(mdurl).st_mtime # Update date = file last mod time
        self.toc     = __md.toc

        # ID and URL = file name
        self.url = fname[:-3]    # Remove .md extension
        self.url = self.url[:15] # Limit length
        self.url = self.url.lower()
        self.url = utils.replacemany(self.url,
                                     (' ','-'),
                                     '_')

        __id = zlib.crc32(fname.encode('utf-8'))
        self.id = str(__id)

        # ADD creation date from file stats if not given in metadatas
        if not hasattr(self, 'datecr'):
            self.datecr = os.stat(mdurl).st_ctime # c(reation)time is OS tied, see os.stat doc



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