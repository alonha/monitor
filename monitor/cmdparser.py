'''
Created on Dec 31, 2014

@author: alon
'''
from utils import logger as log

supportedPlatforms=["controller", "sim", "host", "standalone"]

def printHelpRotine():
    print("use:  mainmonitor.py -e= -d= -n= -t=")
    print("e - entity ['host'/'sim'/'controller/standalone']\r\nd - verbosity [DEBUG/INFO/ERROR]\r\nt - polling interval in seconds")
    

def validateParams(uargs):
    if 'e' in uargs.keys():
        if uargs['e'] in supportedPlatforms:
            pass
        else:
            log.error( "Unsupported platform")
            printHelpRotine()
            return -1
    else:
        print "no location specified, default 'sim'('all'in-one')"
        uargs['e'] = 'sim'
    
    if 't' in uargs.keys():
        pass
    else:
        print("no time interval specified, default 200 msec")
        uargs['t'] = 1000
     
    
def parseCommandLine(clargv):
    ldict = {}
    for farg in clargv:
            if farg.startswith('-'):
                (arg,val) = farg.split("=")
                arg = arg[1:]
    
                if arg in ldict:
                    ldict[arg].append(val)
                else:
                    ldict[arg] = val
    return ldict  