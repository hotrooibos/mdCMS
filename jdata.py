# -*- mode: python ; coding: utf-8 -*-
import json
import os

JSON_PATH = os.getcwd() + '/posts/data.json'


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
    def __init__(self, json_file=JSON_PATH):
        self.jsonf = json_file
        self.jsondat = None
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
        with open(file=self.jsonf, mode='r', encoding='utf-8') as jsonf:
            self.jsondat = json.load(jsonf)
        
        for record in self.jsondat['posts']:
            self.ids.append(record['id'])
            self.sums.append(record['sum'])
            self.titles.append(record['title'])

        self.last_id = max(self.ids) if len(self.ids) > 0 else -1


    def check(self):
        '''
        CHECK JSON : each id must be unique
        '''
        for id in self.ids:
            if self.ids.count(id) > 1:
                print(f'JSON CHECK FAILED : several {id} in data.json')


    def write(self):
        '''
        WRITE 'jsonf' JSON file
        '''
        with open(file=JSON_PATH, mode='w', encoding='utf-8') as jsonf:
            # json.dump(self.jsondat, jsonf)
            json.dump(self.jsondat, jsonf, indent=4)