import os
import sys
import threading


if __name__ == "__main__":    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


    from mdcms import mdcms
    from mdcms import md

    watchdog = threading.Timer(10, lambda: md.watchdog()).start()
    mdcms.app().run(threaded=True, host='localhost', port=8080, debug=True)