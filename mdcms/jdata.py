# -*- mode: python ; coding: utf-8 -*-
from . import constants as const
from . import utils
import json
from json.decoder import JSONDecodeError
import logging
import os
from time import time

log = logging.getLogger(__name__)


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
        log.info('Read json...')

        try:
            with open(file=jsonf,
                      mode='r',
                      encoding='utf-8') as jsonf:
                self.jdat = json.load(jsonf)
                
        except (JSONDecodeError, FileNotFoundError) as e:
            log.info(f'jdata.py: {e}: creating new JSON')
            self.make_default()



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
        log.info('Write json')

        if not jdat:
            jdat = self.jdat

        with open(file=jsonf,
                  mode='w',
                  encoding='utf-8') as jfile:
            json.dump(jdat, jfile, indent=4)

        self.read()



    # def check(self):
    #     '''Check for id duplicates
    #     '''
    #     for id in self.ids:
    #         if self.ids.count(id) > 1:
    #             log.info(f'JSON CHECK FAILED : several {id} in data.json')
    #             # TODO ne conserver en mémoire que
    #             # le post le plus récent (mtime)