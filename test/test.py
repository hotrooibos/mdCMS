import datetime
import os
import sys
import time

# import hashlib, zlib


if __name__ == "__main__":    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # from src.mdcms.mdcms import constants, jdata, md, utils

    # Start execution timer
    start_time = time.time()
    i = 0
    for i in range(1): # Change value with n to execute n times


        '''Tests'''
        currdir = os.path.dirname(os.path.abspath(__file__))
        print(f"{currdir} MTIME -> {os.stat(currdir).st_mtime}")


        # while True:
        #     md.watchdog()
        #     time.sleep(constants.CHECK_TIME)


      
        # mdtest = md.Md('hello.md',
        #             '/home/toleda/Documents/Dev/Python/Marzin.org/posts/hello.md')
        # print(mdtest.title)



        '''Run flask with Werkzeug WSGI test server'''
        # mdcms.app().run(threaded = True,
        #                 hos     = 'localhost',
        #                 port     = 8080,
        #                 debug    = False)


        '''time'''
        # extime = 1617427715.1339917  # Example of epoch time from os.stat().st_ctime/st_mtime
        # exiso = "2021-04-03 07:28:35"

        # # EPOCH->ISO
        # iso = time.strftime('%Y-%m-%d %H:%M:%S',
        #                              time.localtime(extime))

        # # ISO->EPOCH #1
        # epoch = datetime.datetime.strptime(iso,'%Y-%m-%d %H:%M:%S')
        # epoch = datetime.datetime.timestamp(epoch)

        # print (int(epoch), iso)


        '''Hash'''
        # strtest = 'Ceci est un texte court'

        #hashlibs
        # hash = hashlib.blake2b()
        # hash.update(strtest.encode())
        # hash = hash.hexdigest()

        #crc
        # crc = hex(zlib.crc32(strtest.encode('utf-8')) & 0xffffffff)



    # End timer
        i += 1
    print(f"--- {(time.time() - start_time)} seconds ---")