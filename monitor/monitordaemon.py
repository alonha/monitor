'''
Created on Nov 26, 2016

@author: alonharel
The source for this daemon is:
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
''' 

import sys, os, time, atexit
from string import whitespace
from signal import SIGTERM
import mainmonitor


class Daemon:
	"""
	A generic daemon class.
	
	Usage: subclass the Daemon class and override the run() method
	"""
	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', attr=None):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
		self.params = attr
	
	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced 
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() 
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except OSError, e: 
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1) 
	
		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		print "monitordaemon: redirecting stdout to", self.stdout
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())
	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)
	
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run(self.params)

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()
		
	def status(self):
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
		except IOError:
			pid = None
	
		if not pid:
			print "status: not running"
			return
		else:
			print "status:  running"
			return

	def run(self):
		"""
		You should override this method when you subclass Daemon. It will be called after the process has been
		daemonized by start() or restart().
		"""


class monitorDaemon(Daemon):
	def run(self, prms):
		#change working dir to parent's
		os.chdir(prms['dir'])
		mainmonitor.main(prms)

def readMonitorCnfg():
	cfgInfo={}
	cfgFile = 'monitordcfg'
	try:
		cfgF = open(cfgFile)
	except IOError as e:
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
		raise RuntimeError("Cannot open:",cfgFile)
	
	for Line in cfgF:
		line = Line.rstrip()
		if not line.startswith("#"):  
			(attr,val) = line.split(":")
			attr.translate(None, whitespace)
			cfgInfo.update({attr:val})

	cfgF.close()        
	return cfgInfo


if __name__ == "__main__":
	#default values for log and pid files
	_stdout = '/var/log/monitor-daemon.log'
	pid = '/usr/local/monitor-daemon.pid'
	
	params = readMonitorCnfg()
	if 'log' in params.keys():
		_stdout = params['log']
	if 'pid' in params.keys():
		pid = params['pid']
	
	params.update({'dir':os.getcwd()})
		
	msaD = monitorDaemon(pid, stdout=_stdout, attr=params)
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			msaD.start()
		elif 'stop' == sys.argv[1]:
			msaD.stop()
		elif 'restart' == sys.argv[1]:
			msaD.restart()
		elif 'status' == sys.argv[1]:
			msaD.status()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|status" % sys.argv[0]
		sys.exit(2)
