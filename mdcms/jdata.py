# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
import json
import time



class Singleton:
    __instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_.__instance, class_):
            class_.__instance = object.__new__(class_, *args, *kwargs)

        return class_.__instance



class Jdata(Singleton):
    '''
    JSON data file
    '''
    def __init__(self, json_file: str = const.JSON_PATH):
        self.jsonf = json_file
        self.jdat = None
        self.ids = []
        self.last_id = None
        self.sums = []
        self.titles = []
        
        self.read()
        self.check()



    def read(self):
        '''
        READ JSON data file, load and check the content
        '''
        with open(file     = self.jsonf,
                  mode     = 'r',
                  encoding = 'utf-8') as jsonf:
            self.jdat = json.load(jsonf)
        
        # FILL object lists
        for k, v in self.jdat['posts'].items():
            self.ids.append(int(k))
            self.sums.append(v.get('sum'))
            self.titles.append(v.get('title'))

        self.last_id = max(self.ids) if len(self.ids) > 0 else -1



    def check(self):
        '''
        CHECK JSON : each id must be unique
        '''
        for id in self.ids:
            if self.ids.count(id) > 1:
                print(f'JSON CHECK FAILED : several {id} in data.json')



    def write(self, jdat: dict = None):
        '''
        WRITE 'jdat' dict to 'jsonf' JSON file
        '''
        if not jdat:
            jdat = self.jdat

        with open(file=const.JSON_PATH, mode='w', encoding='utf-8') as jsonf:
            json.dump(jdat, jsonf, indent=4)