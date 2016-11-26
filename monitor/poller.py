'''
Created on Dec 31, 2014

@author: alon
'''
import time
import os
import re
import copy
import sockinfoprocess
from utils import logger as log
import sim
import sockinfoparser
import ophandler
from __builtin__ import True
    
numOfBstUcQueues = 1480
BSTTriggerSent = True
dropsInfoSent = True
dummyIterCnt = 0

class cPoller(object):
    '''
    Polls every specified seconds a given set of counters for a specified interface list
     Or
    Polls any other status register and acts accordingly
    '''

    def __init__(self, name, monitorName, command, params, \
                 interval, readFunc, parseFunc, processFunc, runFunc, additionalInfo, asroot, simfile, init):
        '''
        Constructor
        '''
        self.name = name
        self.monitorName = monitorName
        self.interval = interval
        self.command = command
        self.params = params
        self.readFunc = readFunc
        self.parseFunc = parseFunc
        self.processFunc = processFunc
        self.runFunc = runFunc
        self.init = init
        self.interval = interval
        
        self.additionalInfo = additionalInfo
        self.asroot = asroot
        self.simfile = simfile
        self.pollerInit()
        self.lastPollTime = 0
        
    def pollerInit(self):
        pass
        
        if self.init is not None:
            self.init(self)

    def pollerRun(self, time):
        #check if poller interval has passed
        if (time-self.lastPollTime)*1000 > self.interval:
            self.lastPollTime = time
            info = self.readFunc(self.command, self.simfile, self.params, self.asroot)
            self.parseFunc(info)
            reportToController, info = self.processFunc(info)
            return reportToController, info
        #poller interval has not passed yet
        else:
            return False, {}


hostPollers = {'sockinfo':{'name':"sockinfo", 'list':[], 'command':'./netlink-diag',\
                      'params':None,'rfunc':ophandler.run_command, 'parsefunc':sockinfoparser.parseSocketOutput, \
                      'pfunc':sockinfoprocess.sockInfoProcess,'runFunc':cPoller.pollerRun, 'pid':'', \
                      'additionalInfo':{}, 'asroot':False, 'simfile':'./sockinfofile','init':None, \
                      'interval':1000}
                }


pollers={"host":hostPollers,"sim":hostPollers}


