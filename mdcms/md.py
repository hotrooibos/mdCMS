# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import jdata
import hashlib
import markdown
from   markdown.extensions import Extension
import os
import time

JDAT    = jdata.Jdata()
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
        with open(file     = mdurl,
                  mode     = 'r',
                  encoding = 'utf-8') as mdf:
            
            mddat = mdf.read()

        md           = markdown.Markdown(extensions = ['meta','toc','codehilite'])
        self.content = md.convert(mddat)
        md_meta      = md.Meta
        
        self.id      = int(md_meta.get('id')[0])  if md_meta.get('id')       else None
        self.title   = md_meta.get('title')[0]    if md_meta.get('title')    else ''
        self.author  = md_meta.get('author')[0]   if md_meta.get('author')   else ''
        self.cat     = md_meta.get('category')[0] if md_meta.get('category') else None
        self.datecr  = md_meta.get('date')[0]     if md_meta.get('date')     else None
        self.dateup  = int(os.stat(mdurl).st_ctime)
        self.toc     = md.toc
        self.sum     = self.refresh_sum()



    def refresh_sum(self) -> str:
        '''
        Refresh and return checksum of (.md title + content)
        '''
        md_sum = hashlib.md5()
        md_sum.update((self.title + self.author + self.content).encode())
        self.sum = md_sum.hexdigest()
        return self.sum



def process_md():
    id = JDAT.last_id + 1

    # .md LOOP
    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':

            mdurl = f'{const.MD_PATH}/{f}'
            
            md = Md(mdurl)

            # If .md has ID, try to find it in Json
            if md.id != None :
                
                # ID known in Json : update Json with possibly updated data from .md
                if md.id in JDAT.ids:
                    # md.refresh_sum()
                    maj_post(md.id,
                             md.title,
                             md.author,
                             md.content,
                             md.datecr,
                             os.stat(mdurl).st_mtime,
                             md.sum)
                    
                    continue                                            # END, process next .md
                
                # ID unknown in Json : remove it from .md & continue to record creation process
                else:
                    print(f'\nID {md.id} unkown in Json, reset {f} ID')
                    with open(mdurl, 'r', encoding='utf-8') as mdf:  # REMOVE ID (1st line)
                        mdnew = mdf.readlines()[1:]
                    with open(mdurl, 'w', encoding='utf-8') as mdf:
                        mdf.writelines(mdnew)

            # ↓
            # Json record creation process ↓
            # ↓
            
            # ADD ID in .md
            with open(mdurl, 'r', encoding='utf-8') as mdf:
                mddat = mdf.read()
            with open(mdurl, 'w', encoding='utf-8') as mdf:
                mdf.write(f'id:{id}\n{mddat}')

            # ADD creation date from file stats if not given in metadatas
            if not md.datecr:
                md_datecr = os.stat(mdurl).st_ctime                     # c(reation)time is OS tied, see os.stat doc
                md_datecr = time.strftime('%Y-%m-%d %H:%M:%S',          # CONVERT epoch to time
                                        time.localtime(md_datecr))
            else:
                md_datecr = md.datecr

            md_dateup = os.stat(mdurl).st_mtime                         # m(odification)time
            md_dateup = time.strftime('%Y-%m-%d %H:%M:%S',
                                      time.localtime(md_dateup))

            # ADD/WRITE record to Json
            new_record = {
                id: {
                "sum":md.sum,
                "datecr":md_datecr,
                "dateup":md_dateup,
                "title":md.title,
                "author":md.author,
                "content":md.content
                }
            }
            JDAT.jdat['posts'].update(new_record)

            id += 1
    
    # WRITE changes in json file
    JDAT.write()



def maj_post(md_id,
             md_title,
             md_author,
             md_content,
             md_datecr,
             md_dateup,
             md_sum):
    '''
    UPDATE posts 
    '''
    md_id = str(md_id)
 
    md_dateup = time.strftime('%Y-%m-%d %H:%M:%S',
                              time.localtime(md_dateup))

    # FIND the json record corresponding to .md id, CHECK that
    # content (sum) has changed, then UPDATE json with new .md data

    JDAT.jdat['posts'][md_id]['sum']     = md_sum
    JDAT.jdat['posts'][md_id]['title']   = md_title
    JDAT.jdat['posts'][md_id]['author']  = md_author
    JDAT.jdat['posts'][md_id]['content'] = md_content
    JDAT.jdat['posts'][md_id]['datecr']  = md_datecr
    JDAT.jdat['posts'][md_id]['dateup']  = md_dateup



def watchdog():
    '''
    Check any article change
    '''

    for f in os.listdir(const.MD_PATH):
        if f[-3:] == '.md':

            mdurl = f'{const.MD_PATH}/{f}'
            md    = Md(mdurl)
            
            # If the .md isn't newer than last known post update
            if md.dateup <= JDAT.last_chdate:
                if md.id in JDAT.ids:
                    # if md.sum == JDAT.jdat['posts'][str(md.id)]['sum']:
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