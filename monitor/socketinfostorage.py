'''
Created on Nov 26, 2016

@author: alonharel
'''
from monitorinfostorage import cMonitorInfoStorage
from utils import logger as log
    
class cSocketInfoStorage(cMonitorInfoStorage):
    '''
    classdocs
    '''
    def __init__(self, name):
        '''
        Constructor
        '''
        cMonitorInfoStorage.__init__(self, 'hash',name)
        self.data = {}
    
    def calcIndx(self, info):
        sockAtt = str(info['srcIp'])+str(info['srcPort'])+str(info['dstIp'])+str(info['dstPort'])
        return hash(sockAtt)
    
    def refreshEntry(self, indx):
        self.data[indx]['status'] = 'used'
        
    def getEntryInfo(self, indx):
        try:
            return self.data[indx]
        except ValueError:
            log.error("indx value for getEntryInfo was not found in sockInfoStorae!")
            
    def updateEntryState(self, indx, state):
        self.data[indx]['state'] = state
        
    def updateAllEntriesStatus(self, status):
        for k,v in self.data.iteritems():
            v['status'] = status
        
    def addEntry(self, indx, info):
        #hash socket fields
        info.update({'status':'new'})
        self.data.update({indx:info})
        
    def deleteEntry(self, indx):
        #hash socket fields
        del self.data[indx]
    
    def isInfoEntryFound(self, indx):
        if indx in self.data.keys():
            return True
        else:
            return False
    
    def delInfoEntry(self, info):
        indx = self.calcIndx(info)
        try:
            self.data.pop(indx)
        except ValueError:
            log.error("indx value to remove was not found in sockInfoStorae!")
    
    def isInfoEntryEqual(self, indx, info):
        try:
            rec = self.data[indx]
            if cmp (rec, info) == 0:
                return True
            return False
        except ValueError:
            log.error("indx value to search was not found in sockInfoStorae!")
            return False
            
    def stateChanged(self, indx, info):
        try:
            if self.data[indx]['state'] != info['state']:
                return True
            return False
        except ValueError:
            log.error("indx value to search was not found in sockInfoStorae!")
    
    def getStaleRecords(self):
        deleteList = []
        for k,v in self.data.iteritems():
            if v['status'] == 'stale':
                deleteList.append(v['sockIdn'])
        return deleteList
        