'''
Created on Nov 26, 2016

@author: alon
'''

import shlex
import subprocess
import os
import collections
import monitoruser
from utils import logger as log
import sim
import sockinfoparser


def run_command(command, simfile = None, params = None, as_root=False):
    '''Executes a command and captures the exit code and the output.
        :param command: the command to execute
        :param as_root: if True, the command is executed with root privileges
        :param simfile: if simulation, process this file instead of executing the command
        :return: a deque list with the exit code as first element, and
            the output lines following.
    '''
    result = []
    if not sim.sim:
        env = os.environ.copy()
        log.debug("executing command: %s" % command)
        try:
            if as_root:
                monitoruser.raise_privileges()
            proc = subprocess.Popen(shlex.split(command),
                                    stdout=subprocess.PIPE,
                                    env=env)
        finally:
            if as_root:
                monitoruser.drop_privileges()
        
        output = proc.stdout.readline()
        while output != '' or proc.poll() is None:
            if output:
                result.append(output.strip())
            output = proc.stdout.readline()
        log.debug("exit code for command (%s): %d" % (command, proc.poll()))
    else:
        #read simulation file        
        with open(simfile,"r") as f:
            for line in f.readlines():
                result.append(line)
                
    return result

class cOpHandler(object):
    '''
    Performs MSA operation(s) 
    '''

    def __init__(self, opr, agentId, opDict):
        
        '''
        Constructor
        '''
        self.name = opr.replace(" ", "")
        log.debug("opHandler name: %s", self.name)
        if opDict is not None:
            self.opDict = opDict
        else:
            self.opDict = None
                     
        if not sim.sim:
            self.fileToProcess = self.name
        else:
            self.fileToProcess = sim.fileToProcess+self.name+agentId
            
        self.op = self.opTypes[opr]
     
    def process(self):
        info = dict()
        log.debug("Executing: %s with cmd: %s", self.op['func'], self.op['command'])
        if self.opDict is not None:
            info = self.op['func'](self, self.op['command'], self.opDict)
        else:
            info = self.op['func'](self, self.op['command'])
            
        return info
     
    
    def sockInfoOp(self, cmnd):
        #read data
        log.debug("Executing: %s", cmnd)
        
        if not sim.sim:
            output = run_command(self.command, as_root=False)       
            return sockinfoparser.parseSocketOutput(output)
        else:
            output = run_command('ls', as_root=False)       
            return output
              
                
    opTypes = {'socket info':{'func':sockInfoOp, 'command':'./netlink-diag'}}
#    
#    