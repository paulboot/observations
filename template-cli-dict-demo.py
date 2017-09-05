#!/usr/bin/env python

import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

#Import config settings here
##if file not exist echo use config-example.py
#from config import *

#Imports for generic parsing etc..
from datetime import datetime, timedelta
import pytz
import logging
import time
import re
import os
import argparse
import pprint

#For network related tooling
#import paramiko
#from dns import resolver,reversename
#from jinja2 import Environment, PackageLoader #@UnresolvedImport

##Dependencies
# sudo apt-get install python-dnspython python-jinja2 python-paramiko python-dateutil
# pip install python-dateutil pytz

##Version and identification
scriptVersion = '1.x (x-x-2017) by Paul Boot'
scriptPurpose = 'Generates xxxx'
scriptFileName = os.path.basename(__file__)
debug = False

##Start logging
log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

def parseargs():
    '''Parse commandline arguments'''
    parser = argparse.ArgumentParser(prog=scriptFileName, description=scriptPurpose)

    parser.add_argument('--debug', action="store_true", default=False,
                            help='show debug info')
    parser.add_argument('--version', '-V', action='version', version=scriptFileName + ' ' + scriptVersion,
                            help='print version')
    return parser.parse_args()

def dict_def_rules():
    rules = {
            ('public','local',20) : {'dst_host' : "ANY", 'dst_port' : "HTTPS",
                                     'src_host' : "ANY", 'srcport' : "ANY",
                                     'proto' : "TCP",
                                     'desc' : "Van Internet naar firewall zelf(VPN, tunnels en remote login)"},
            ('public','local',900) : {'dst_host' : "ANY", 'dst_port' : "NTP",
                                     'src_host' : "ANY",
                                     'proto' : "ANY",
                                     'desc' : "Van Internet naar firewall zelf(VPN, tunnels en remote login)"},
            ('public','local',15)  : {'dst_host' : "ANY", 'dst_port' : "ANY",
                                     'src_host' : "ANY",
                                     'proto' : "UDP",
                                     'desc' : "Van Internet naar firewall zelf(VPN, tunnels en remote login)"},
            ('public','local',10) : {'dst_host' : "ANY", 'dst_port' : "NTP",
                                     'src_host' : "ANY",
                                     'proto' : "UDP",
                                     'desc' : "Van Internet naar firewall zelf(VPN, tunnels en remote login)"},
            ('public','private',10) : {'dst_host' : "ANY", 'dst_port' : "OPENVPN",
                                    'src_host' : "ANY",
                                    'proto' : "TCP",
                                    'desc' : "Van Internet direct naar intern(DNAT)"}
    }
    
    #Insert a new unique key
    rules[('private','local',10)] = {'dst_host' : "ANY", 'dst_port' : "SSH",
                                  'src_host' : "ANY",
                                  'proto' : "TCP",
                                  'desc' : "Van LAN naar firewall zelf"}
    rules[('private','partner',200)] = {'dst_host' : "ANY", 'dst_port' : "ANY",
                                    'src_host' : "ANY",
                                    'proto' : "TCP",
                                    'desc' : "Van LAN naar TalkTo partnet netwerk tbv printers"}
    rules[('private','partner',300)] = {'dst_host' : "ANY", 'dst_port' : "ANY",
                                    'src_host' : "ANY",
                                    'proto' : "TCP",
                                    'desc' : "Van LAN naar TalkTo partnet netwerk tbv printers"}

    #modify or add a single entry
    rules[('private','partner',200)]['desc'] = 'Modify the desc entry'
    rules[('private','partner',200)]['more'] = 'More entries in the dict'
    
    #remove or a single of whole dict
    del rules[('private','partner',200)]['desc']
    del rules[('private','local',10)]

    for key1,key2,key3 in rules:
        print('Key=' + key1 + ' ' + key2 + ' ' + str(key3))
    print

    pp = pprint.PrettyPrinter(indent=3)
    print("Rules definition")
    pp.pprint(rules)

    return rules

if __name__ == '__main__':

    args = parseargs()
    debug = args.debug

    log.info('Start of main')

    ##Dict demo
    dictDemo = True
    if dictDemo:
        dict_def_rules()

    log.info('End of main exiting')
    sys.exit()

