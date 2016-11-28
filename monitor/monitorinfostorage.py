'''
Created on Nov 26, 2016

@author: alonharel
'''
from utils import logger as log

infoStorageTypes = ['hash']

class cMonitorInfoStorage(object):
    '''
    classdocs
    '''
    def __init__(self, stype, name):
        '''
        Constructor
        '''
        self.type = stype
        self.name = name
        if not stype in infoStorageTypes:
            log.error("Not supported storage type: %s", str(stype))
        
    def addEntry(self, info):
        pass
    
    def isInfoEntryFound(self, info):
        pass
    
    def delInfoEntry(self, info):
        pass
    
    def isInfoEntryEqual(self, info):
        pass
    