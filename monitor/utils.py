'''
Created on Jan 14, 2015

@author: alon
'''
'''
Created on Jan 14, 2015

@author: alon
'''
import logging
import threading
import sys



logger = logging.getLogger('switch-agent-logger')
logLvl = {'ERROR':logging.ERROR, 'WARNING':logging.WARNING, 'INFO':logging.INFO,'DEBUG':logging.DEBUG}
event = threading.Event()

def uInit(lvl):
    '''
    Constructor
    '''
    #create Logger and set logging level
    if not lvl in logLvl.keys():
        print "Wrong logging level"
        return
    logger.setLevel(logLvl[lvl])
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    event.clear()
        
