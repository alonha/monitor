'''
Created on Nov 26, 2016

@author: alon
'''

from utils import logger as log
from socketinfostorage import cSocketInfoStorage


def parseSocketOutput(input):
    '''This function parses the output of TBD
    :param output_lines: a list with the lines from 'inet-diag' program
    The output looks like:
        User: root (UID: 0) Src: 127.0.0.1:631 Dst: 0.0.0.0:0
            State: LISTEN RTT: 0ms (var. 250ms) Recv. RTT: 0ms Snd_cwnd: 0/10
        User: alonharel (UID: 1000) Src: 172.16.32.149:51614 Dst: 162.213.33.241:80
            State: CLOSE-WAIT RTT: 82.457ms (var. 56.578ms) Recv. RTT: 0ms Snd_cwnd: 0/10
    '''

    info = []
    for line in input:
        words = line.split()
        if words[0].strip() == 'User:':
            # first item of a new record
            srcInfo = words[5].split(":")
            dstInfo = words[7].split(":")
            identifyer = {'user':words[1],'srcIp':srcInfo[0],'srcPort':srcInfo[1],'dstIp':dstInfo[0],'dstPort':dstInfo[1]}
            continue
        elif words[0].strip() == 'State:':
            # second and last record line, add to socket list
            info.append({'sockIdn':identifyer,'state':words[1]})
            continue
        
#     for i in range(0,len(info)):
#         message = '%s' % (info[i])
#         log.debug(message)
    
    return info

def sockInfoProcess(info, storage):
    ret = {}
    deleteList = []
    changedList = []
    newList = []
    #mark all storage entries as 'stale'
    storage.updateAllEntriesStatus('stale')
        
    for rec in info:
        indx = storage.calcIndx(rec['sockIdn'])
        exist = storage.isInfoEntryFound(indx)
        if not exist:
            log.debug("+++ Adding socket to storage: %s, state: %s", str(rec['sockIdn']), str(rec['state']))
            storage.addEntry(indx, rec)
            newList.append(rec)
        else:
            if storage.stateChanged(indx, rec):
                log.debug("*** Socket %s state changed to %s", str(rec['sockIdn']), rec['state'])
                storage.updateEntryState(indx, rec['state'])
                changedList.append(rec)
                #mark socket as 'used' (refresh use)
                storage.refreshEntry(indx)
            else:
                #mark socket as 'used' (refresh use)
                storage.refreshEntry(indx)
      
    #add to report also sockets which exist in storage but do not exist anymore in the system
    deleteList = storage.getStaleRecords()
    ret.update({'new':newList, 'changed':changedList, 'deleted':deleteList})
    #remove socket entries which do not exist anymore in the system
    for rec in deleteList:
        log.debug("---Removing socket from storage: %s", rec)
        indx = storage.calcIndx(rec)
        storage.deleteEntry(indx)
            
    if ( (len(newList) == 0) and (len(changedList) == 0) and (len(deleteList) == 0) ):
        return False, None
    else:
        log.debug("sending to ctrl: %s" ,str(ret))
        return True, ret