''''
Created on Nov 26, 2016

@author: alon
'''

monitorID = ''
threads = []

import poller
import cmdparser
import signal
import sys
import time
import os
import thread
import multiprocessing
import threading
import utils
from utils import logger as log
from thread import error as thread_error
from string import whitespace
from monitor import cMonitor as mn
import controller
import sim
import socket

CONTROLLER_PORT = 8089
if not sim.sim:
    CONTROLLER_IP = socket.gethostbyname(socket.gethostname())
else:
    #CONTROLLER_IP = 'localhost'
    CONTROLLER_IP = '10.0.0.11'

def readCnfg():
        
        print "Working dir: ", os.getcwd()
        cfgInfo={}
        cfgFile = 'monitordcfg'
        try:
            cfgF = open(cfgFile)
    
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            raise RuntimeError("Cannot open:",cfgFile)
                  
        for Line in cfgF:
            line = Line.rstrip()  
            (attr,val) = line.split(":")
            attr.translate(None, whitespace)
            cfgInfo.update({attr:val})
                
        cfgF.close()
        
        return cfgInfo

def terminationSignalHandler(signal, frame):
        print('Program terminated, exiting!')
        sys.exit(0)

def init():
    global monitorID
    monitorID = 'stub-id'
    #register termination signal routine
    signal.signal(signal.SIGINT, terminationSignalHandler)
    
def controllerInit(ctrlIP, ctrlPort):
    #initialize fabric controller mode
    if sim.runRest == True:
        import controllerrest
            
    controller.controllerInit(ctrlIP, ctrlPort)
              
    t = threading.Thread(target=controller.controllerWorker, args=(1,))
    t.daemon = True
    threads.append(t)
    t.start()
         
    t = threading.Thread(target=controllerrest.controllerRestRun, args=())
    t.daemon = True
    threads.append(t)
    t.start()
    
def runControllerMode():
    #wait for agents to connect to server   
    time.sleep(1)
  
    #sleep - wait for a killing signal...
    while True:
        time.sleep(1)

def runHostMonitor(interval, pollerSet):
    monitor = mn(None, pollerSet, interval)
    t = threading.Thread(target=monitor.monitorWorker, args=(0.2,))
    t.daemon = True
    threads.append(t)
    t.start()
    
def runMonitorMode():
    #sleep - wait for a killing signal...
    while True:
        time.sleep(1)
            
def runSimMode(interval, pollerSet, ctrlIP, ctrlPort):
    # run in 'all-in-one' mode
    controllerInit(ctrlIP, ctrlPort)
    runHostMonitor(interval, pollerSet)
    runControllerMode()
   
def main(userargs=None):
    init()
  
    if userargs == None:
        userargs = readCnfg()
     
    if cmdparser.validateParams(userargs) == -1:
        print "command line parameters error, exiting!"
        return
     
    #set verbosity
    utils.uInit(userargs['d'])
    interval = userargs['t']
    if 'controller_ip' in userargs:
        controller_ip = userargs['controller_ip']
    else:
        controller_ip = CONTROLLER_IP
    if 'controller_port' in userargs:
        controller_port = userargs['controller_port']
    else:
        controller_port = CONTROLLER_PORT
        userargs['controller_port']
  
    if userargs['e'] == 'sim':
        sim.sim = True
        sim.runRest = True
        #set the relevant poller set
        runSimMode(interval, poller.pollers[userargs['e']], controller_ip, controller_port)
        
    elif userargs['e'] == 'controller':
        sim.sim = False
        sim.runRest = True
        controllerInit(controller_ip, controller_port)
        runControllerMode()
    
    elif userargs['e'] == 'standalone':
        sim.standalone = True
        sim.sim = False
        #set the relevant poller set
        runHostMonitor(interval, poller.pollers['host'])
        runMonitorMode()
        
    else:
        #host
        sim.sim = False
        #set the relevant poller set
        runHostMonitor(interval, poller.pollers[userargs['e']])
        runMonitorMode()

