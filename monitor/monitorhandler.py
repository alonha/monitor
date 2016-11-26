'''
Created on Nov 26, 2016

@author: alon
'''
import json
from utils import logger as log
from utils import event as eve
import thread
import time
import controller


class cMonitorHandler(object):
    '''
    Handles one monitor
    '''

    def __init__(self, hid, sock):
        '''
        Constructor
        '''
        self.id = hid
        self.sock = sock
        
    def conRecHndl(self, msg, sock):
        log.debug("From conRecHndl:")
        msg = {'type':'connect reply','monitorId':msg['monitorId'],'status':'accepted','reqId':msg['reqId']}
        controller.controllerSend(msg, sock)
        
    def monitorlTermination(self, msg):
        log.debug( "Received termination for monitor %s",msg['monitorId'])
           
    def execHandler (self, Type, reqid, msg):
        
        #execute corresponding message handler
        rep = self.agentTrigMsgTypes[Type](self, msg)
        #if there is a reply, send it
        if rep is not None:          
            rep.update({'monitorId':self.name})
            jRep = json.dumps(rep) 
            #send reply
            log.debug("execHandler sending reply")
            self.agentSend(jRep)
                         
#        
    agentTrigMsgTypes = {"connect request": conRecHndl}
    
    