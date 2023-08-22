#!/usr/bin/env python3

# MIT License

# Copyright (c) 2023 Antoine Marzin

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
from json.decoder import JSONDecodeError
from time import time

from . import constants as const
from .logger import log


class Singleton:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls, *args, **kwargs)

        return cls.instance



class Jdata(Singleton):
    """JSON data class
    Loaded from JSON data file or created 
    with no data if file doesn't exists.
    """
    def read(self,
             json_file: str=const.JSON_PATH):
        """Read JSON data file and load it in memory as a
        Jdata object or, if file does not exists, make a new one
        """
        log.info(f"Read {const.JSON_PATH}")
        try:
            with open(file=json_file,
                      mode='r',
                      encoding='utf-8') as json_file:
                self.jdat = json.load(json_file)
                
        except (JSONDecodeError, FileNotFoundError) as e:
            log.info(f"{e}: creating new JSON")
            self.make_default()



    def make_default(self):
        """Create an empty json structure,
        and write it into json file.
        """
        path = const.JSON_PATH

        # If a json exists and is not empty, backup it
        if os.path.isfile(path) and os.stat(path).st_size != 0:
            date = int(time())
            os.rename(path,
                      f'{path}-{date}.bak')

        # Create structure without data
        self.jdat = {
            "comments": {
            },
            "bans": {
            },
            "likes": {
            }
        }
        
        # Write the empty structure to json file
        self.write()



    def write(self,
              jdat: dict=None,
              json_file: str=const.JSON_PATH):
        """Write 'jdat' dict into 'jsonf' JSON file
        """
        log.info(f"jdata.py: Write JSON")

        if not jdat:
            jdat = self.jdat

        with open(file=json_file,
                  mode='w',
                  encoding='utf-8') as jsonfile:
            json.dump(jdat, jsonfile, indent=4)

        self.read()



    # TODO def check(self):
    #     """Check for id duplicates
    #     """
    #     for id in self.ids:
    #         if self.ids.count(id) > 1:
    #             log.info(f'JSON CHECK FAILED : several {id} in data.json')
    #             # ne conserver en mémoire que
    #             # le post le plus récent (mtime)