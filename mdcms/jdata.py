# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import utils
import json
# from datetime import date, datetime


class Singleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)

        return cls.__instance



class Jdata(Singleton):
    '''
    JSON data file
    '''
        
    def read(self,
             jsonf: str = const.JSON_PATH):
        '''
        READ JSON data file, load and check the content
        '''
        print('Read json file')
        
        self.ids = []
        self.titles = []
        self.last_chdate = 0

        with open(file     = jsonf,
                  mode     = 'r',
                  encoding = 'utf-8') as jsonf:
            self.jdat = json.load(jsonf)

        # FILL object lists
        for k, v in self.jdat['posts'].items():
            self.ids.append(k) # k(ey) = id string
            self.titles.append(v.get('title'))
            
            if self.last_chdate < v.get('dateup'):
                self.last_chdate =  v.get('dateup')

        # JSON checkup
        self.__check()

        # SORT posts by dateup, then datecr
        self.jdat['posts'] = dict(sorted(self.jdat['posts'].items(),
                                         key     = self.__sorter,
                                         reverse = True))

        # Testing dict sort
        # for i in self.jdat['posts'].values():
        #     print(i['title'], '---', i['dateup'], i['datecr'])

        # CONVERT dates format for front display
        # if const.TIME_FORMAT:
        #     self.__format_time(const.TIME_FORMAT)



    def write(self,
              jdat: dict = None,
              jsonf: str = const.JSON_PATH):
        '''
        WRITE 'jdat' dict to 'jsonf' JSON file
        '''
        if not jdat:
            jdat = self.jdat

        with open(file=jsonf, mode='w', encoding='utf-8') as jfile:
            json.dump(jdat, jfile, indent=4)

        self.read()

        

    def __sorter(self, i):
        '''
        Function called as a key when sorting posts with .sorted()
        Sort by post update date, then post creation date
        '''
        __dateup = i[1]['dateup']
        __datecr = i[1]['datecr']

        return (__dateup, __datecr)



    def __check(self):
        '''
        Check json for id doublons
        '''
        for id in self.ids:
            if self.ids.count(id) > 1:
                print(f'JSON CHECK FAILED : several {id} in data.json')
                # TODO ne conserver en mémoire que
                # le post le plus récent (mtime)



    def __format_time(self, __format: str):
        '''
        Convert posts timestamps to the given __format
        '''
        for k, v in self.jdat['posts'].items():
            self.jdat['posts'][k]['datecr'] = v.get('datecr')
            self.jdat['posts'][k]['dateup'] = v.get('dateup')