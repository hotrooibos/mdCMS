# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import utils
import json
from json.decoder import JSONDecodeError
import os
from time import time



class Singleton:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)

        return cls.instance



class Jdata(Singleton):
    '''JSON data class
    '''
        
    def read(self,
             jsonf:str=const.JSON_PATH):
        '''
        READ JSON data file, load and check the content
        '''
        print('Read json...')
        
        self.ids = []
        self.titles = []
        self.last_chdate = 0

        try:
            with open(file=jsonf,
                      mode='r',
                      encoding='utf-8') as jsonf:
                self.jdat = json.load(jsonf)

            # FILL object lists
            for k, v in self.jdat['posts'].items():
                self.ids.append(k) # k(ey) = id string
                self.titles.append(v.get('title'))
                
                if self.last_chdate < v.get('dateup'):
                    self.last_chdate =  v.get('dateup')
        except JSONDecodeError:
            print("jdata.py: JSONDecodeError: creating new JSON")
            self.make_default()

        # JSON checkup
        self.check()

        # SORT posts by dateup, then datecr
        self.jdat['posts'] = dict(sorted(self.jdat['posts'].items(),
                                         key=self.sorter,
                                         reverse=True))



    def make_default(self):
        '''Create an empty structured json data file
        '''
        path = const.JSON_PATH

        # If a json exists and is not empty, backup it
        if os.path.isfile(path) and os.stat(path).st_size != 0:
            date = int(time())
            os.rename(path,
                      f'{path}-{date}.bak')

        # Create structure & write to new file
        self.jdat = {
            "posts": {
            },
            "comments": {
            },
            "bans": {
            }
        }
        
        self.write()



    def write(self,
              jdat: dict=None,
              jsonf: str=const.JSON_PATH):
        '''
        WRITE 'jdat' dict to 'jsonf' JSON file
        '''
        print('Write json')

        if not jdat:
            jdat = self.jdat

        with open(file=jsonf,
                  mode='w',
                  encoding='utf-8') as jfile:
            json.dump(jdat, jfile, indent=4)

        self.read()

        

    def sorter(self, i):
        '''Function called as a key when sorting posts with .sorted()

        Sort by post update date, then post creation date
        '''
        # __dateup = i[1]['dateup']
        # return (__dateup, __datecr)
        datecr = i[1]['datecr']

        return (datecr)



    def check(self):
        '''Check for id duplicates
        '''
        for id in self.ids:
            if self.ids.count(id) > 1:
                print(f'JSON CHECK FAILED : several {id} in data.json')
                # TODO ne conserver en mémoire que
                # le post le plus récent (mtime)