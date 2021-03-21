# -*- mode: python ; coding: utf-8 -*-
from datetime import datetime
import hashlib
import jdata
import markdown
from markdown.extensions import Extension
import os

JDAT = jdata.Jdata()
POST_PATH = os.getcwd() + '/posts'
FILES = os.listdir(POST_PATH)


class Md:
    '''
    Markdown document object.

    URL to .md file in argument.
    Usage:
    >>>  mdfile = Md('/home/antoine/readme.md')
    '''
    def __init__(self, mdurl:str):
        with open(mdurl, 'r', encoding='utf-8') as mdf:
            mddat = mdf.read()

        md           = markdown.Markdown(extensions = ['meta','toc','codehilite'])
        self.content = md.convert(mddat)
        md_meta      = md.Meta
        self.id      = None
        self.title   = ''
        self.author = ''
        self.toc     = md.toc
        self.sum     = None

        if md_meta.get('id'):
            self.id = int(md_meta.get('id')[0])
        
        if md_meta.get('title'):
            self.title = md_meta.get('title')[0]
        
        if md_meta.get('author'):
            self.author = md_meta.get('author')[0]

        self.sum = self.refresh_sum()


    def refresh_sum(self) -> str:
        '''
        Refresh and return checksum of (.md title + content)
        '''
        md_sum = hashlib.md5()
        md_sum.update((self.title + self.author + self.content).encode())
        self.sum = md_sum.hexdigest()
        return self.sum



def get_new_posts():
    id = JDAT.last_id + 1

    # .md LOOP
    for f in FILES:
        if f[-3:] == '.md':

            furl = f'{POST_PATH}/{f}'
            
            md = Md(furl)

            # If .md has ID, try to find it in Json
            if md.id != None :
                
                # ID known in Json : update Json with possibly updated data from .md
                if md.id in JDAT.ids:
                    # md.refresh_sum()
                    maj_post(md.id, md.title, md.author, md.content, md.sum)
                    continue                                            # END, process next .md
                
                # ID unknown in Json : remove it from .md & continue to record creation process
                else:
                    print(f'\nID {md.id} unkown in Json, reset {f} ID')
                    with open(furl, 'r', encoding='utf-8') as mdf:  # REMOVE ID (1st line)
                        mdnew = mdf.readlines()[1:]
                    with open(furl, 'w', encoding='utf-8') as mdf:
                        mdf.writelines(mdnew)

            # ↓
            # Json record creation process ↓
            # ↓
            
            # ADD ID in .md
            with open(furl, 'r', encoding='utf-8') as mdf:
                mddat = mdf.read()
            with open(furl, 'w', encoding='utf-8') as mdf:
                mdf.write(f'id:{id}\n{mddat}')

            datecreation = datetime.today().strftime('%Y%m%d%H%M')
            datemaj = datecreation

            # ADD/WRITE record to Json
            new_record = {
                "id":id,
                "sum":md.sum,
                "datecr":datecreation,
                "dateupd":datemaj,
                "title":md.title,
                "author":md.author,
                "content":md.content
            }
            JDAT.jsondat['posts'].append(new_record)
            JDAT.write()

            id += 1
    

def maj_post(md_id, md_title, md_author, md_content, md_sum):
    '''
    UPDATE posts 
    '''
    jsondat = JDAT.jsondat

    # FIND the json record corresponding to .md id, CHECK that
    # content (sum) has changed, then UPDATE json with new .md data
    for record in jsondat['posts']:
        if record['id'] == md_id and record['sum'] != md_sum:
                print(f'\nUpdating .md id{md_id}')
                record['sum'] = md_sum
                record['title']   = md_title
                record['author']  = md_author
                record['content'] = md_content
                record['dateupd'] = datetime.today().strftime('%Y%m%d%H%M')

                JDAT.write() # WRITE changes in Json


def md_checkup():
    '''
    Vérif complète des md.
    TODO Loop sur tous les fichiers md comportant un id, pour vérifier qu'il existe bien un post à l'id correspondant dans le JSON
    S'il existe un id, vérifier que 1) la date de création est ==, 2) le checksum(title + content) est ==
    '''
    for f in FILES:
        furl = f'{POST_PATH}/{f}'

        if f[-3:] == '.md':     
            md = Md(furl)

            # SKIP file if a post with same title or checksum exists in JSON data
            if md.title in JDAT.titles:
                print(f'| A post with title {md.title} already exists in data.json -> skipping {f}')
                continue
            if md.sum in JDAT.sums:
                print(f'| A post with the same content as {f} exists in data.json -> skipping {f}')
                continue