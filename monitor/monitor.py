'''
Created on Nov 26, 2016

@author: alon
'''
from string import whitespace
import signal
import json, sys, time
import thread
import os
import socket
import re
import collections
from poller import cPoller as pl
from baseagent import cAgentBase
from utils import logger as log
import utils
from ophandler import cOpHandler as op
import sim


cfgInfo = {'NAME':"default-agent", 'CTRLIP':socket.gethostbyname(socket.gethostname()), 'CTRLPORT':8089, 'TOPOLOC': 'TOR'}
switchInf = ['swp']
maxSwitchPorts = 64
switchInfName = 'swp'

class cMonitor(cAgentBase):
    '''
    Monitor class
    '''
    def __init__(self, cfgfile, pollerSet, interval):
        '''
        Constructor
        '''
        cAgentBase.__init__(self)
        self.name = socket.gethostname()
        self.monitorId = self.name
        if cfgfile:
            self.cfgFile = cfgfile
        else:
            self.cfgFile = 'monitorcfg'   
        if not interval is None:
            self.interval = interval
        ## default to 1000msec polling interval
        else:
            self.interval = 1000
        self.run = True
        self.runPeriodic = False
        self.pollerSet = []
                     
        ## initialize agent pollers
        for j in pollerSet.keys():
            poller =pl(pollerSet[j]['name'], \
                                         self.name, \
                                         pollerSet[j]['command'], \
                                         pollerSet[j]['params'], \
                                         pollerSet[j]['interval'], \
                                         pollerSet[j]['rfunc'], \
                                         pollerSet[j]['parsefunc'], \
                                         pollerSet[j]['pfunc'], \
                                         pollerSet[j]['runFunc'], \
                                         pollerSet[j]['additionalInfo'], \
                                         pollerSet[j]['asroot'], \
                                         pollerSet[j]['simfile'], \
                                         pollerSet[j]['init'])
            
            self.pollerSet.append(poller)
            
        ## read configuration
        self.getCnfg()
        
        #register termination signal routine
        signal.signal(signal.SIGINT, self.monitorTerminationSignalHandler)
        
        ## connect to controller
        self.connectToController()    

    
    def connectToController(self):
        cAgentBase.connectToCntrl(self, cfgInfo['CTRLIP'], cfgInfo['CTRLPORT'])
        self.establishConnectionToCtrl()
        
    def getCnfg(self):
        
        try:
            cfgF = open(self.cfgFile)
    
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            raise RuntimeError("Cannot open:",self.cfgFile)
                  
        for Line in cfgF:
            line = Line.rstrip()  
            (attr,val) = line.split(":")
            attr.translate(None, whitespace)
            if attr in cfgInfo.keys():
                cfgInfo[attr] = val
                
        cfgF.close()
    
    def establishConnectionToCtrl(self):
        msg = {}
        msg.update({'type':'connect request','monitorId':self.name,'reqId':0})
        cAgentBase.send(self, msg)
                 
    def monitorHandler(self, msg):
        
        decMsg = json.loads(msg)
        mtype = decMsg['type']
        monitorId = decMsg['monitorId']
        terminate = False
            
        if monitorId != self.monitorId:
            log.error("Monitor-id mismatch, expecting: %s, received: %s", self.monitorId, monitorId)
            return None
        if not (mtype in self.monitorMsgTypes.keys()):
            log.error("Unidentified message type :", mtype)
            return None
        else:
            log.debug("monitorHandler %s:", self.name)    
    
        # execute handler 
        rep = self.monitorMsgTypes[mtype](self,decMsg)
        if rep is not None:          
            # encap reply
            rep.update({'monitorId':self.name})
            if rep['type'] == 'terminate':
                terminate = True 
            # send reply
            log.debug("monitorHandler %s sending reply", self.name)
            self.monitorSend(rep)
            
            # terminate the switch agent
            if terminate:
                log.debug("Terminating monitor...")
                self.shutdownMonitor()

    def doPeriodic(self, time):
        for poller in self.pollerSet:
            reportToController = False
            (reportToController, data) = poller.runFunc(poller, time)
            log.debug("%s: poller %s returned reportToController: %s",self.name, poller.name, reportToController)
            if reportToController:
                log.info("%s: reporting to controller", self.name)
                self.monitorHandlers[poller.name](self, data)
                        
    def restartPollers(self):
        log.debug("%s: restarting pollers", self.monitorId)
        for poller in self.pollerSet:
            if poller.init is not None:          
                poller.init(poller)
    
    def monitorReceive(self):
            ret = cAgentBase.recv(self, self.monitorHandler)
                        
    def monitorSend(self, msg):
        sent = cAgentBase.send(self, msg)
        return sent
            
    def monitorWorker(self, t):
        if sim.standalone:
            self.runPeriodic = True
        t0 = time.clock()
        while True and self.run:
            # Execute periodic operations
            t1= time.clock()
            # Handle new messages
            if self.controllerConnected == True:
                self.monitorReceive()
            else:
                self.connectToController()
                self.runPeriodic = False
            # time.clock is in milliseconds
            if (t1-t0) > t:
                if self.runPeriodic == True:
                    self.doPeriodic(t1)
                    t0 = time.clock()
            
    def shutdownMonitor(self):
        cAgentBase.close(self)
        self.run = False
        
    def monitorTerminationSignalHandler(self, signal, frame):
        print('MSA Program terminated, exiting!')
        self.shutdownMonitor()
        sys.exit(0)
        
                    
    def conRepHndl(self, msg):
        log.debug("From conRepHndl: monitorId: %s, reqId: %d, type: %s", msg['monitorId'], msg['reqId'], \
                  msg['type'])
        #start periodic work only after connecting to controller
        self.runPeriodic = True
        #initialize pollers
        self.restartPollers()
    
   
    def socketInfoUpdate(self, sockInfo):
        log.debug("From socketInfoUpdate:")
        data = dict()
        data['type'] = 'socket info update'
        data['reqId'] = 0
        data['monitorId'] = self.monitorid      
        data.update({'data':sockInfo})
        self.monitorSend(data)

          
    #messages that are received/triggered by the monitor
    monitorMsgTypes = {"connect reply":conRepHndl}

       
       