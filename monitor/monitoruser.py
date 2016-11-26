'''
Created on Nov 22, 2016

@author: alonharel
'''

import grp
import os
import pwd
from utils import logger as log
USER = 'alonharel'
GROUP = 'alonharel'


def drop_privileges():
    global USER
    global GROUP
    if os.getuid() == 0:
        try:
            uid = pwd.getpwnam(USER)[2]
            gid = grp.getgrnam(GROUP)[2]
        except KeyError:
            log.warn("user %s or group %s does not exist" % (USER, GROUP))
            return False
        try:
            os.setegid(gid)
        except OSError, e:
            log.warn("could not set effective group to %s: %s" % (GROUP, e))
            return False
        try:
            os.seteuid(uid)
        except OSError, e:
            log.error("could not set effective user to %s: %s" % (USER, e))
            return False
        os.umask(057)
        return True


def raise_privileges():
    try:
        os.seteuid(0)
        os.setegid(0)
        return True
    except OSError, e:
        log.error("cannot raise privileges: %s" % e)
        return False