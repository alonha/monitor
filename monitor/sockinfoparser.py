'''
Created on Nov 26, 2016

@author: alon
'''

from utils import logger as log

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
        
    for i in range(0,len(info)):
        message = '%s' % (info[i])
        log.debug(message)
    
    return info