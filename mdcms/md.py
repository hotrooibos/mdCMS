# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import jdata
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

    URL string to .md file in argument.

    Usage:
    >>>  mdfile = Md('/home/antoine/readme.md')
    '''
    def __init__(self, mdurl:str):

        # Read .md file and make attributes from its content
        with open(file     = mdurl,
                  mode     = 'r',
                  encoding = 'utf-8') as mdf:
            
            mddat = mdf.read()

        __md           = markdown.Markdown(extensions = ['meta','toc','codehilite'])
        self.content = __md.convert(mddat)

        self.title   = __md.Meta.get('title')[0]      if __md.Meta.get('title')      else self.content[:15]
        self.author  = __md.Meta.get('author')[0]     if __md.Meta.get('author')     else ''
        self.cat     = __md.Meta.get('categories')[0] if __md.Meta.get('categories') else None
        self.datecr  = __md.Meta.get('date')[0]       if __md.Meta.get('date')       else None
        self.dateup  = int(os.stat(mdurl).st_mtime) # Update date = file last mod time
        self.toc     = __md.toc

        # ID = title checksum
        __id = zlib.crc32(self.title.encode('utf-8'))
        self.id = str(__id)

        # ADD creation date from file stats if not given in metadatas
        if not self.datecr:
            self.datecr = os.stat(mdurl).st_ctime                     # c(reation)time is OS tied, see os.stat doc
            self.datecr = time.strftime('%Y-%m-%d %H:%M:%S',          # CONVERT epoch to datetime
                                        time.localtime(self.datecr))



def process_md():
    '''
    Read all .md files, get and transform
    their data, inject datas in data.json
    '''

    # .md LOOP
    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':
            mdurl = f'{const.MD_PATH}/{f}'
            md = Md(mdurl)

            
            # ID KNOWN in json : update json with
            # possibly updated data from .md
            if md.id in JDAT.ids:
                # md.refresh_sum()
                maj_post(md.id,
                         md.title,
                         md.author,
                         md.content,
                         md.datecr,
                         os.stat(mdurl).st_mtime)

                continue # END, process next .md

            
            # ID UNKNOWN in json
            # JSON record CREATION
            md_dateup = os.stat(mdurl).st_mtime                         # m(odification)time
            md_dateup = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(md_dateup))

            # ADD new record to dict
            new_record = {
                md.id: {
                "datecr":md.datecr,
                "dateup":md_dateup,
                "title":md.title,
                "author":md.author,
                "content":md.content
                }
            }
            JDAT.jdat['posts'].update(new_record)

    # WRITE JSON FILE
    JDAT.write()



def maj_post(id,
             title,
             author,
             content,
             datecr,
             dateup):
    '''
    UPDATE posts 
    '''

    dateup = time.strftime('%Y-%m-%d %H:%M:%S',
                           time.localtime(dateup))

    # FIND the json record corresponding to .md
    # id, CHECK that content (sum) has changed,
    # then UPDATE json with new .md data

    JDAT.jdat['posts'][id]['title']   = title
    JDAT.jdat['posts'][id]['author']  = author
    JDAT.jdat['posts'][id]['content'] = content
    JDAT.jdat['posts'][id]['datecr']  = datecr
    JDAT.jdat['posts'][id]['dateup']  = dateup



def watchdog():
    '''
    Polling MD_PATH for .md file change
    '''

    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':

            mdurl = f'{const.MD_PATH}/{f}'
            md    = Md(mdurl)
            
            # If the .md isn't newer than last known post update
            if md.dateup <= JDAT.last_chdate:
                if str(md.id) in JDAT.ids:
                    continue

            print(f'Watchdog: process_md from {f}')
            process_md()
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