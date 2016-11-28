# monitor
This project has two components: 1. Controller
 2. Monitor

# Controller
============
Runs on any server
Waits for connections initiated by monitors
Provides the following information via a REST API (port 5555):
TBD

# Monitor
=========
Runs on the platform to be monitored and connects to the Controller

# Running the Fabric Controller
===============================
1. Copy code to the controller machine
2. Change to the directory where you put the code
3. Edit 'monitordcfg' ('e' can receive the following values: host/controller/sim/standalone)
4. Run controller: python monitorrun.py

# Running monitor
=================
1. Copy the code to the monitored machine
2. Change to the directory where you put the monitor code
3. Edit/Create 'monitordcfg' file:
    - set 'e'to 'host
    - set 'd' to the required verbosity level (DEBUG/INFO/ERROR)
    (optional) log: - log file to be used by the MSA daemon (if not specified, default is: '/var/log/monitor-daemon.log')
    (optional) pid: - the process-od file of the daemon (if not specified, default is: '/usr/local/monitor-daemon.pid')
Edit 'agentcfg' file:

CTRLIP: - fabric controller ip-address
CTRLPORT: - fabric controller tcp port
TOPOLOC: - tier in the Clos tolology [1-highest spine level]
SFLOWCTRL: - whether sFlow start/stop is controlled by MSA
SFLOWPERIOD: - how long sFlow samples are being sent after conditions (that caused start sending) disappear
Operate the MSA daemon by: 'sudo python msadaemon.py start|stop|restart|status'
