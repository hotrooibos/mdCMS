import os
import sys


if __name__ == "__main__":    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mdcms import mdcms, md

    ''' Timit tests '''
    # import timeit
    # print ('Watchdog:', timeit.timeit('md.watchdog()',
    #                                   setup = "from mdcms import mdcms, md",
    #                                   number = 1000))
    
    ''''''
    # import threading
    # watchdog = threading.Timer(10, lambda: md.watchdog()).start()
    
    '''Run flask with Werkzeug WSGI test server'''
    # mdcms.app().run(threaded = True,
    #                 hos     = 'localhost',
    #                 port     = 8080,
    #                 debug    = False)