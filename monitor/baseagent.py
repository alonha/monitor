'''
Created on Jan 1, 2015

@author: alon
'''
import socket
import fcntl
import os
import errno
import time
import sys
import json
from socket import error as socket_error
from utils import logger as log
import sim

RECV_BUFFER = 8192 # Advisable to keep it as an exponent of 2
CTRL_DISCONNECTED = -1
CTRL_CONN_OK = 0

class cAgentBase(object):
    '''
    Switch agent base class.
    Implements connection related tasks
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.controllerConnected = False
         
    def connectToCntrl(self, ip, port):
        if not sim.standalone:
            try:
                self.ctrlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except:
                log.error("socket creation error")
                
            log.debug("Connecting %s:%s..." %(ip, port))
    
            notPrinted = True
            # try to connect to server
            while self.controllerConnected == False:
                try:
                    if not sim.sim:
                        self.ctrlSocket.connect((ip, int(port)))
                    else: #I don't know why when running on my mac the above 'connect' failed...
                        self.ctrlSocket.connect(('localhost', 8089))
                    # set socket to be non-blocking
                    fcntl.fcntl(self.ctrlSocket, fcntl.F_SETFL, os.O_NONBLOCK)
                    self.controllerConnected = True
                except socket_error as serr:
                    if notPrinted:
                        log.error ("socket connection error: %s" %(serr.errno))
                        log.error ("Keeping trying to connect...")
                        notPrinted = False
                time.sleep(1) # wait 1 sec
    
            log.info("Connection established!")
        else:
            #standalone mode
            self.controllerConnected = True
        
        
    def recv(self, handler):
        if not sim.standalone:
            length = None
            buffer = ""
            data = ""
            valErr = False
            
            try:
                data += self.ctrlSocket.recv(RECV_BUFFER)
            except socket.error, serr:
                err = serr.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    pass
                else:
                    # a "real" error occurred
                    log.error("Server is disconnected, socket error: %s", serr)
                    self.ctrlSocket.close()
                    self.controllerConnected = False
            else:
                buffer += data
                while True:
                    if length == 0:
                        if '::' not in buffer:
                            break
                    # remove the length bytes from the front of buffer
                    # leave any remaining bytes in the buffer!
                    length_str, ignored, buffer = buffer.partition('::')
                    try:
                        length_int =  int(length_str)
                    except ValueError:
                            valErr = True
                            log.info("Server connection error, closing socket")
                            #############################################################
                            # Need to check if this can only happen when socket is broken
                            #############################################################
                            self.ctrlSocket.close()
                            self.controllerConnected = False
                            #############################################################
                            
                            break
                    length = length_int-len('::')
                
                    if len(buffer) < length:
                        break
                    # split off the full message from the remaining bytes
                    # leave any remaining bytes in the buffer!
                    message = buffer[:length]
                    buffer = buffer[length:]
                    length = 0
                # PROCESS MESSAGE            
                if not valErr:
                    log.debug("agent received %r", data)
                    handler(message)
                return
        else:
            #standalone mode
            return 

    def send(self, msg):
        if not sim.standalone:
            jMsg = json.dumps(msg)
            Len = len (jMsg)
            Len += len(str(sys.getsizeof(Len))) # add the length of 'Len' value (i.e. add an integer length
            buff=str(Len)+'::'+jMsg
            lenToSend = len(buff)
            totalsent = 0
                    
            while totalsent < lenToSend:
                try:
                    sent = self.ctrlSocket.send(buff[totalsent:])
                except socket.error, serr:
                    err = serr.args[0]
                    #handle the case where socket was closed
                    if err == errno.EBADF:
                        log.error("--- !!! socket error: %s", serr)
                        log.error ("Server is disconnected !!!")
                        self.ctrlSocket.close()
                        self.controllerConnected = False
                        break;
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent
        else:
            #standalone mode
            pass
                 
    def close(self):
        log.debug("Closing MSA socket..." )
        try:
            self.ctrlSocket.shutdown(socket.SHUT_RDWR)
        except socket.error, serr:
            pass
        try:
            self.ctrlSocket.close()
        except socket.error, serr:
            pass
        
       
     