# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
import json
from datetime import datetime
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
        
        self.read()
        self.__check()
        
        if const.TIME_FORMAT:
            self.__format_time(const.TIME_FORMAT)



    def read(self):
        '''
        READ JSON data file, load and check the content
        '''
        self.ids = []
        self.sums = []
        self.titles = []
        self.last_id = None
        self.last_chdate = 0

        with open(file     = self.jsonf,
                  mode     = 'r',
                  encoding = 'utf-8') as jsonf:
            self.jdat = json.load(jsonf)
        
        # FILL object lists
        for k, v in self.jdat['posts'].items():
            self.ids.append(int(k))
            self.sums.append(v.get('sum'))
            self.titles.append(v.get('title'))
            
            __last_chdate = datetime.strptime(v.get('dateup'), '%Y-%m-%d %H:%M:%S')
            __last_chdate = datetime.timestamp(__last_chdate)

            if self.last_chdate < __last_chdate:
                self.last_chdate =  int(__last_chdate)
        
        self.last_id = max(self.ids) if len(self.ids) > 0 else -1



    def __check(self):
        '''
        CHECK JSON : each id must be unique
        '''
        for id in self.ids:
            if self.ids.count(id) > 1:
                print(f'JSON CHECK FAILED : several {id} in data.json')



    def __format_time(self, format:str):
        '''
        Format time stamps to the given format
        '''
        for k, v in self.jdat['posts'].items():
            datecr = datetime.strptime(v.get('datecr'), '%Y-%m-%d %H:%M:%S')
            dateup = datetime.strptime(v.get('dateup'), '%Y-%m-%d %H:%M:%S')
            self.jdat['posts'][k]['datecr'] = datecr.strftime(format)
            self.jdat['posts'][k]['dateup'] = dateup.strftime(format)



    def write(self, jdat: dict = None):
        '''
        WRITE 'jdat' dict to 'jsonf' JSON file
        '''
        if not jdat:
            jdat = self.jdat

        with open(file=const.JSON_PATH, mode='w', encoding='utf-8') as jsonf:
            json.dump(jdat, jsonf, indent=4)
        
        self.read()
        self.__check()
        
        if const.TIME_FORMAT:
            self.__format_time(const.TIME_FORMAT)