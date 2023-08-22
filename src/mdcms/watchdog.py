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

from os import listdir, stat
from time import sleep

from . import constants as const
from .logger import log
from .md import Md


def watchdog(mdb, jd, pending_w):
    """Watchdog loop

    Every "const.CHECK_TIME" seconds,

    - Polls MD_PATH for .md files I/O operations (add,rm,mod)
    - Builds and update MD objects from .md files
    - Maintain an MD object base (list) in-memory up to date
    - Run data.json I/O operations if new data (comment, bans) are
      pending for writing
    """
    mdb_last_time = 0

    # Last time /posts dir was modified
    posts_mtime = stat(const.MD_PATH).st_mtime

    while True:
        # populate is a flag for initial execution
        # If populate == True, process all .md
        populate = True if len(mdb) < 1 else False

        # List of actual files in MD_PATH, we compare it
        # to the md objects dict (mdb) and deleted md/posts
        f_list = []

        # Loop over each .md file
        for f in (f for f in listdir(const.MD_PATH) if f[-3:] == '.md'):
            f_url = f"{const.MD_PATH}/{f}"
            f_mtime = stat(f_url).st_mtime

            # SKIP .md file
            # if it's is already known and has no change
            if not populate \
            and f_mtime <= mdb_last_time:
                
                if f not in f_list:
                    f_list.append(f)
                
                continue
            
            # UPDATE post
            # if .md file has reference in mdb and its
            # mod time > to the last known modification
            if not populate \
            and f in f_list \
            and f_mtime > mdb_last_time:
                log.info(f'Update post "{md.url}" ({f})')
                md = Md(f, f_url)
                
                for k,v in enumerate(mdb):

                    if v.url == md.url:
                        mdb[k] = md
                
                mdb_last_time = f_mtime

            # CREATE NEW post
            # if .md file's unknown from mdb
            elif f not in f_list:
                try:
                    # Create Md object from file
                    md = Md(f, f_url)

                    # Add post in mem if file is
                    # unknown from mdb
                    log.info(f'Add post "{md.url}" ({f})')
                    mdb.append(md)
                    
                    if f_mtime > mdb_last_time:
                        mdb_last_time = f_mtime
                    
                except Exception as e:
                    log.warning(e)

                f_list.append(f)

        # REMOVE post from mdb
        # if its corresponding .md file
        # is missing (deleted, moved, renamed...)
        if stat(const.MD_PATH).st_mtime > posts_mtime:

            for md in mdb:
                if md.f_name not in f_list:
                    log.info(f'Remove post "{md.url}" ({f} missing)')

                    # Recalculate mdb_last_time, in case the
                    # missing .md was the most recent file
                    if md.m_time == mdb_last_time:
                        mdb_last_time = 0
                        
                        for f in listdir(const.MD_PATH):
                            if f[-3:] == '.md' \
                            and f_mtime > mdb_last_time:
                                mdb_last_time = f_mtime
                
                    mdb.remove(md)

                posts_mtime = stat(const.MD_PATH).st_mtime

        # Sort posts
        mdb.sort(key=lambda x: x.ctime,
                reverse=True)

        # Write pending data into data.json (jd object)
        # And reset flag state
        if pending_w:
            jd().write()
            pending_w = False

        sleep(const.CHECK_TIME)