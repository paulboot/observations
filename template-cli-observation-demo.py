#!/usr/bin/env python


#Import config settings here
##if file not exist echo use config-example.py
#from config import *

#Imports for generic parsing etc..
import json
import logging
import time
import re
import os
import argparse
import pprint
import csv
import sys

#For network related tooling
#import paramiko
#from dns import resolver,reversename
#from jinja2 import Environment, PackageLoader #@UnresolvedImport

##Dependencies
# sudo apt-get install python-dnspython python-jinja2 python-paramiko python-dateutil
# pip install python-dateutil

##Version and identification
scriptVersion = '1.x (x-x-2017) by Paul Boot'
scriptPurpose = 'Reads JSON observation file and builds Python dict structure'
scriptFileName = os.path.basename(__file__)
debug = True

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

if __name__ == '__main__':

    args = parseargs()
    debug = args.debug

    log.info('Start of main')
  
    ##JSON demo
    dataDict = {}
    jsonDemo = True
    if jsonDemo:
        with open('observation-column-example1.json', 'r') as f:
            data = json.load(f)
            pp = pprint.PrettyPrinter(indent=4)
            #pp.pprint(data)
        
        for interval in data['intervals']:
            keyInterval = (interval['startTime'],interval['endTime'])
            dataDict[keyInterval] = {}
            dataDict[keyInterval]['phenomenonTime'] = interval['phenomenonTime']
            for position in interval['positions']:
                keyPosition = (position['offsetX'],position['offsetY'],position['offsetZ'])
                dataDict[keyInterval][keyPosition] = {}
                dataDict[keyInterval][keyPosition]['offsetUnit'] = position['offsetUnit']
                for aspect in position['aspects']:
                    keyAspect = aspect['name']
                    dataDict[keyInterval][keyPosition][keyAspect] = {}
                    dataDict[keyInterval][keyPosition][keyAspect] = aspect

        #debug python dict
        #pp.pprint(dataDict)
        
        #Example manipulation
        print(dataDict['2017-02-07T13:05:00Z','2017-02-07T13:05:59Z'][(0, 0, -1.0)]['average']['value'])
        dataDict['2017-02-07T13:05:00Z','2017-02-07T13:05:59Z'][(0, 0, -1.0)]['average']['value']=10000
        print(dataDict['2017-02-07T13:05:00Z','2017-02-07T13:05:59Z'][(0, 0, -1.0)]['average']['value'])
        print(dataDict['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z'][(0, 0, -1.0)]['average']['value'])
        print(dataDict['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z'][(0, 0, -2.0)]['average']['value'])

    log.info('End of main exiting')
    sys.exit()

