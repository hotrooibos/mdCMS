import datetime, time
import os
import sys


if __name__ == "__main__":    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mdcms import mdcms, md

    '''Tests'''
    start_time = time.time()
    i = 0
    for i in range(1):

        md.watchdog()

        i += 1
    print(f"--- {(time.time() - start_time)} seconds ---")
    
    
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