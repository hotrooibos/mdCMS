# -*- mode: python ; coding: utf-8 -*-
from datetime import datetime
import hashlib
import jdata
import markdown
from markdown.extensions import Extension
import os
import re


JDAT    = jdata.Jdata()
MD_PATH = os.getcwd() + '/posts'


class Md:
    '''
    Markdown document object.

    URL to .md file in argument.

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
        self.id      = int(md_meta.get('id')[0]) if md_meta.get('id') else None
        self.title   = md_meta.get('title')[0] if md_meta.get('title') else ''
        self.author  = md_meta.get('author')[0] if md_meta.get('author') else ''
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


    # @staticmethod
    # def process_ressources(content):
    #     '''
    #     Lire le contenu du .md, puis vérifier la présence de lignes
    #     au format ![*](*.png/jpg/gif/svg)
    #     '''
    #     # In content, find regex ![*](*.jpg) or one of the others formats
    #     # The * preceding extension only accepts alphanumeric, dash and underscore chars
    #     # The goal here is to detect simple filenames (without url format like https://...)
    #     #  which means they are local images
    #     # Ex : ![](hellow.svg), ![A landscape](landsc.png), etc.
    #     x = re.findall("!\[.*\]\([a-zA-ZÀ-ÿ0-9_-]*\.(?:jpg|gif|png|svg)\)", content)
 

    #     for i in x:
    #         print(i, 'non traité')



def process_md():
    id = JDAT.last_id + 1

    # .md LOOP
    for f in os.listdir(MD_PATH):
        if f[-3:] == '.md':

            mdurl = f'{MD_PATH}/{f}'
            
            md = Md(mdurl)

            # If .md has ID, try to find it in Json
            if md.id != None :
                
                # ID known in Json : update Json with possibly updated data from .md
                if md.id in JDAT.ids:
                    # md.refresh_sum()
                    maj_post(md.id, md.title, md.author, md.content, md.sum, os.stat(mdurl).st_mtime)
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

            datecreation = os.stat(mdurl).st_ctime  # c(reation)time is OS tied, see os.stat doc
            datemaj = os.stat(mdurl).st_mtime

            # ADD/WRITE record to Json
            new_record = {
                id: {
                "sum":md.sum,
                "datecr":datecreation,
                "dateupd":datemaj,
                "title":md.title,
                "author":md.author,
                "content":md.content
                }
            }
            JDAT.jsondat['posts'].update(new_record)
            JDAT.write()

            id += 1
    


def maj_post(md_id,
             md_title,
             md_author,
             md_content,
             md_sum,
             md_modtime):
    '''
    UPDATE posts 
    '''
    jsondat = JDAT.jsondat
    md_id = str(md_id)

    # FIND the json record corresponding to .md id, CHECK that
    # content (sum) has changed, then UPDATE json with new .md data
    
    if jsondat['posts'][md_id]['sum'] != md_sum:
        print(f'\nUpdating .md id{md_id}')
        jsondat['posts'][md_id]['sum'] = md_sum
        jsondat['posts'][md_id]['title']   = md_title
        jsondat['posts'][md_id]['author']  = md_author
        jsondat['posts'][md_id]['content'] = md_content
        jsondat['posts'][md_id]['dateupd'] = md_modtime

        JDAT.write() # WRITE changes in Json



def md_checkup():
    '''
    Vérif complète des md.

    TODO Loop sur tous les fichiers md comportant un id, pour vérifier qu'il existe bien un post à l'id correspondant dans le JSON
    
    S'il existe un id, vérifier que 1) la date de création est ==, 2) le checksum(title + content) est ==
    '''
    for f in os.listdir(MD_PATH):
        mdurl = f'{MD_PATH}/{f}'

        if f[-3:] == '.md':     
            md = Md(mdurl)

            # SKIP file if a post with same title or checksum exists in JSON data
            if md.title in JDAT.titles:
                print(f'| A post with title {md.title} already exists in data.json -> skipping {f}')
                continue
            if md.sum in JDAT.sums:
                print(f'| A post with the same content as {f} exists in data.json -> skipping {f}')
                continue



def watchdog():
    '''
    Check any article change
    '''
    print('Watchdog is watching...')
    # Create a dict with .md files url as keys, and their last mod time as values
    # ex: {'/opt/hellow.md': 1616622618.280879, '/opt/neatpost.md': 1616622594.959593, ...}
    sorted_md = {}
    for f in os.listdir(MD_PATH):
        if f[-3:] == '.md':
            mdurl = f'{MD_PATH}/{f}'
            cur_mtime = os.stat(mdurl).st_mtime
            sorted_md.update({mdurl:cur_mtime})

    # Reverse sort by value (most recent mtime first)
    sorted_md = sorted(sorted_md.items(), key=lambda item: item[1], reverse=True)
    
    # Loop in the sorted list, so most recently modified files will be comparated first
    for record in sorted_md:
        mdurl = record[0]
        mdid = str(Md(mdurl).id)                            # TODO gérer le cas où l'id n'existe pas (nouvel article à intégrer)

        cur_mtime = record[1]

        if mdid in JDAT.jsondat['posts']:
            json_mtime = JDAT.jsondat['posts'][mdid]['dateupd'] # TODO gérer le cas où l'id n'existe pas (nouvel article à intégrer)
            
            # If file mtime equals known (json) mtime = no change = skip
            if cur_mtime == json_mtime:
                continue
        
        process_md()
        return


    # Non-sorted algorithm (XXX for future performance test) :
    #
    # for f in os.listdir(MD_PATH):
    #     if f[-3:] == '.md':

    #         mdurl = f'{MD_PATH}/{f}'
    #         mdid = str(Md(mdurl).id)
    #         json_mtime = JDAT.jsondat['posts'][mdid]['dateupd']
    #         cur_mtime = os.stat(mdurl).st_mtime
        
        
    #         if cur_mtime != json_mtime:
    #             print(f'CHANGE DETECTED FOR {mdid} : {cur_mtime} - {json_mtime}')
    #             process_md()
    #             return