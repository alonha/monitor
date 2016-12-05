'''
Created on Nov 26, 2016

@author: alon
'''
import socket
import select
import signal
import sys
import time
import json
import errno
import sim
from socket import error as socket_error
from utils import logger as log
from utils import event as eve
import monitormessage
from monitorhandler import cMonitorHandler as mh

server_socket = None
connList = []   # list of socket clients
RECV_BUFFER = 65536 # Advisable to keep it as an exponent of 2
NUM_OF_MONITORS = 20
monitorList = {}
monitorSocketDict = {}
run = True
monitorInventoryList = []


def controllerInit(ctrlIp, ctrlPort):
    global server_socket
    
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket_error as serr:
            log.error("controller socket creation error")
            raise serr
            
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    
    try:
        if not sim.sim:
            log.debug("Controller ip %s", str(ctrlIp))
            server_socket.bind((ctrlIp, ctrlPort))
        else: #for some reason I had to add explicit address on my mac-os
            server_socket.bind((ctrlIp, int(ctrlPort)))
        
    except socket_error as serr:
            log.error("controller socket bind error")
            raise serr
    # accept up to NUM_OF_AGENTS connections
    server_socket.listen(NUM_OF_MONITORS)
    # Add server socket to the list of readable connections
    connList.append(server_socket)
    #register termination signal routine
    signal.signal(signal.SIGINT, controllerlTerminationSignalHandler)
    
        
def controllerlRemoveMonitor(sock):
    found = False
    for monitor, val in monitorList.iteritems():
        if val['socket'] == sock:
            found = True
            break
     
    if found:
        log.info("--- Removing monitor %s", monitor)
        monitorList.pop(monitor)    
    
        
def controllerlAddMonitor(sock, monitorId):
    newMonitorHndlr = mh(monitorId, sock)
    log.info("+++ Adding monitor %s", monitorId)
    monitorList.update({monitorId:{'obj':newMonitorHndlr, 'socket': sock, 'run':'True'}})          
    return newMonitorHndlr 

def controllerRecFromSock(sock):
    length = monitorSocketDict[sock]['length']
    buff = monitorSocketDict[sock]['buff']
    data = monitorSocketDict[sock]['data']
    valErr = False
    
    try:
        data += sock.recv(RECV_BUFFER)
    except socket.error, serr:
        err = serr.args[0]
        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
            pass
        else:
            # a "real" error occurred
            log.error("'controllerRecFromSock' socket receive error: %s", serr)
    else:
        buff += data
        while True:
            if length == 0:
                if '::' not in buff:
                    break
            # remove the length bytes from the front of buffer
            # leave any remaining bytes in the buffer!
            length_str, ignored, buff = buff.partition('::')
            try:
                length_int =  int(length_str)
            except ValueError:
                log.error("######### 'ValueError' from  controllerRecFromSock !!!!!!")
                valErr = True
                break
            length = length_int-len('::')
            
            if len(buff) < length:
                break
            # split off the full message from the remaining bytes
            # leave any remaining bytes in the buffer!
            message = buff[:length]
            buff = buff[length:]
            length = 0
    # PROCESS MESSAGE            
    log.debug("Controller received %r", data)
    monitorSocketDict[sock]['length'] = 0
    monitorSocketDict[sock]['buff'] = ""
    monitorSocketDict[sock]['data'] = ""
    if not valErr:
        return message
    else:
        return


def controllerWorker(t):
    global server_socket, connList
                 
    while 1 and (run == True):
                        
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(connList,[],[])
     
        for sock in read_sockets:
             
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection received through server_socket
                sockfd, addr = server_socket.accept()
                #add to connection list
                connList.append(sockfd)
                #add to switch agent socket dict
                monitorSocketDict.update({sockfd:{'length':0, 'buff':"", 'data':""}})
                log.info ("Client (%s, %s) connected" % addr)
                                 
            #Some incoming message from a client
            else:
                # Data received from client, process it
                try:
                    data = controllerRecFromSock(sock)
                    if data:
                        controllerlRec(sock, data)
                                     
                # client disconnected, so remove from socket list
                except:
                    log.error ("Client (%s, %s) is disconnected" % addr)
                    if sock in connList:
                        connList.remove(sock)
                        #clear agent list
                        controllerlRemoveMonitor(sock)
                        sock.close()
                    continue
    return
                
             
def controllerlRec(sock, data):
    # decode message
    msg = json.loads(data)
    mtype = msg['type']
    reqId = msg['reqId']
    monitorId = msg['monitorId']
        
    log.debug("Controller received: %s %s %s", monitorId, mtype, reqId)
    sys.stdout.flush()
          
    # handle new agents
    if mtype == 'connect request':
        if not monitorId in monitorList.iterkeys():
            authenticated = controllerAuthenticateMonitor(msg)
            if authenticated == True:
                newmonitorHndlr = controllerlAddMonitor(sock, monitorId)
                # send reply
                newmonitorHndlr.conRecHndl(msg, sock)
            else:
                #disconnect socket
                log.info("Monitor %s authentication fail, closing socket", monitorId) 
                if sock in connList:
                    connList.remove(sock)
                    #clear agent list
                    controllerRemoveMonitor(sock)
                    sock.close()
    # validate message type   
    elif not mtype in monitormessage.monitorMsgTypes:
        log.error("Unidentified message type : %s", mtype)
        return None
    else:
        # call agent handler
        res = monitorList[monitorId]['obj'].execHandler(mtype, reqId, msg)
        
                        
def controllerAuthenticateMonitor(msg):
    
    #do authentication - TBD
    return True

def controllerSend(msg, sock):
    jMsg = json.dumps(msg)
    Len = len (jMsg)
    Len += len(str(sys.getsizeof(Len))) # add the length of 'Len' value (i.e. add an integer length
    buff=str(Len)+'::'+jMsg
    lenToSend = len(buff)
    
    totalsent = 0
    while totalsent < lenToSend:
        try:
            sent = sock.send(buff[totalsent:])
        except socket.error, serr:
            log.error("--- !!! socket error: %s", serr)
            err = serr.args[0]
            #handle the case where socket was closed
            if err == errno.EBADF: 
                log.error ("Client is disconnected")
                if sock in connList:
                    connList.remove(sock)
                    #clear agent list
                    controllerlRemoveMonitor(sock)
                break;
                   
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent
    
def controllerIsMonitorConnected(monitor):
    try:
        Connected = monitorList[monitor]
    except KeyError:
        return False

    return True

def controllerShutdown():
    log.debug("Closing controller socket..." )
    try:
        server_socket.shutdown(socket.SHUT_RDWR)
    except socket.error, serr:
        pass
    try:
        server_socket.close()
    except socket.error, serr:
            pass
    
def controllerlTerminationSignalHandler(signal, frame):
        print('Fabric Controller Program terminated, exiting!')
        controllerShutdown()
        sys.exit(0)    
        

        
        
        

        

        
        



     

                 