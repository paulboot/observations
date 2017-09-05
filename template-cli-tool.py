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
import json
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
debug = True

##Globals
places = set()
building = {}
targets = {}

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
    observations = {}
    jsonDemo = True
    pp = pprint.PrettyPrinter(indent=4)
    with open('observation-column-example1 20170901.json', 'r') as f:
        dataJson = json.load(f)
        #pp.pprint(dataJson)

    for observation in dataJson['observations']:
        keyObservation = observation['startTime'],observation['endTime']
        observations[keyObservation] = {}
        observations[keyObservation]['phenomenonTime'] = observation['phenomenonTime']
        #ToDo Process Values
        #ToDo Aspect Meta Values
        for position in observation['positions']:
            keyPosition = (position['offset']['x'],position['offset']['y'],position['offset']['z'])
            if 'positions' not in observations[keyObservation]:
                observations[keyObservation]['positions'] = {}
            observations[keyObservation]['positions'][keyPosition] = {}
            observations[keyObservation]['positions'][keyPosition]['offset'] = {}
            observations[keyObservation]['positions'][keyPosition]['offset']['unit'] = position['offset']['unit']
            for aspect in position['aspects']:
                keyAspect = aspect['name']
                if 'aspects' not in observations[keyObservation]['positions'][keyPosition]:
                    observations[keyObservation]['positions'][keyPosition]['aspects'] = {}
                observations[keyObservation]['positions'][keyPosition]['aspects'][keyAspect] = {}
                observations[keyObservation]['positions'][keyPosition]['aspects'][keyAspect] = aspect

    #pp.pprint(observations)

    #Example manipulation
    #observations['2017-02-07T13:05:00Z','2017-02-07T13:05:59Z']['positions'][(0, 0, -1.0)]['aspects']['average']['value']=10000
    #observations['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z']['positions'][(0, 0, -2.0)]['aspects']['average']['value']=50000
    #print(observations['2017-02-07T13:05:00Z','2017-02-07T13:05:59Z']['positions'][(0, 0, -1.0)]['aspects']['average']['value'])
    #print(observations['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z']['positions'][(0, 0, -1.0)]['aspects']['average']['value'])
    #print(observations['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z']['positions'][(0, 0, -2.0)]['aspects']['average']['value'])

    #fails because need to build back structure
    #print(json.dumps(observations, indent=4, sort_keys=True, ensure_ascii=False))
    
    #read data from RMI example same observations stucture
    observations = {}
    aspectStructure = {}
    aspectStructure['WaterLevel'] = {}
    aspectStructure['WaterLevel']['minset'] = ['average']

    #for-loop HVH25,HVH45,HVH90
    locationNames = {}
    locationNames['HVH25'], locationNames['HVH45'], locationNames['HVH90'] = {},{},{}
    locationNames['HVH25']['hight'] = -2.5
    locationNames['HVH45']['hight'] = -4.5
    locationNames['HVH90']['hight'] = -9.0
    filePath='data/CSV'
    fileName='TW10_2017_08_01'
    for locationName in locationNames:
        positionHight = locationNames[locationName]['hight']
        try:
            with open(filePath + '/' + locationName + '/' + fileName, 'r') as f:
                for line in f:
                    dateRMIStr, timeRMIStr, seperatorStr, valueQualityStr = line.split()
                    valueInt, qualityInt = [int(x) for x in valueQualityStr.split('/')]
                    valueFloat = float(valueInt/10)
                    
                    #Example 01-08-17 23:50:00
                    #datetime_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
                    phenomenonTime = datetime.strptime(dateRMIStr + ' ' + timeRMIStr + ' +0100', '%d-%m-%y %H:%M:%S %z').astimezone(pytz.timezone('UTC'))
                    #print ('%s  Temperatuur is %r met Kwaliteit %i' % (phenomenonTime.isoformat(), valueFloat, qualityInt))
                    
                    #create one observation
                    startTime = phenomenonTime - timedelta(seconds=300)
                    endTime = phenomenonTime + timedelta(seconds=299)
                    keyObservation = startTime.isoformat(), endTime.isoformat()
                    if keyObservation not in observations:
                        observations[keyObservation] = {}
                        observations[keyObservation]['phenomenonTime'] = phenomenonTime.isoformat()
                    #create position
                    if 'positions' not in observations[keyObservation]:
                        observations[keyObservation]['positions'] = {}
                    observations[keyObservation]['positions'][(0,0,positionHight)] = {}
                    #create offset
                    if 'offset' not in observations[keyObservation]['positions'][(0,0,positionHight)]:
                        observations[keyObservation]['positions'][(0,0,positionHight)]['offset'] = {}
                        observations[keyObservation]['positions'][(0,0,positionHight)]['offset']['unit'] = 'm'
                    #loop through aspects depending on aspect set
                    for aspect in aspectStructure['WaterLevel']['minset']:
                        if aspect == 'average':
                            #check if exists
                            if 'aspects' not in observations[keyObservation]['positions'][(0,0,positionHight)]:
                                observations[keyObservation]['positions'][(0,0,positionHight)]['aspects'] = {}
                            observations[keyObservation]['positions'][(0,0,positionHight)]['aspects']['name'] = aspect
                            observations[keyObservation]['positions'][(0,0,positionHight)]['aspects']['value'] = valueFloat
                            observations[keyObservation]['positions'][(0,0,positionHight)]['aspects']['quality'] = qualityInt
                            observations[keyObservation]['positions'][(0,0,positionHight)]['aspects']['uncertainty'] = None
                            
        except IOError as e:
            sys.exit('file %s, mode %s: %s' % (filename, f.mode, e))
    
    #pp.pprint(observations)
    #sys.exit()

        
    dataJsonDict={}
    #TODO fill in symple things
    dataJsonDict['observations'] = []
    for keyObservation in observations:
        startTimeStr, endTimeStr = keyObservation
        dataJsonDict['observations'].append({})
        dataJsonDict['observations'][-1]['startTime'] = startTimeStr
        dataJsonDict['observations'][-1]['endTime'] = endTimeStr
        dataJsonDict['observations'][-1]['phenomenonTime'] = observations[keyObservation]['phenomenonTime']
        for keyPosition in observations[keyObservation]['positions']:
            positionOffsetX, positionOffsetY, positionOffsetZ = keyPosition
            if 'positions' not in dataJsonDict['observations'][-1]:
                dataJsonDict['observations'][-1]['positions'] = []
            dataJsonDict['observations'][-1]['positions'].append({})
            dataJsonDict['observations'][-1]['positions'][-1]['offset'] = {}
            dataJsonDict['observations'][-1]['positions'][-1]['offset']['x'] = positionOffsetX
            dataJsonDict['observations'][-1]['positions'][-1]['offset']['y'] = positionOffsetY
            dataJsonDict['observations'][-1]['positions'][-1]['offset']['z'] = positionOffsetZ
            dataJsonDict['observations'][-1]['positions'][-1]['offset']['unit'] = observations[keyObservation]['positions'][keyPosition]['offset']['unit']
            for keyAspect in observations[keyObservation]['positions'][keyPosition]:
                if keyAspect == 'aspects':
                    if 'aspects' not in dataJsonDict['observations'][-1]['positions'][-1]:
                        dataJsonDict['observations'][-1]['positions'][-1]['aspects'] = []
                    dataJsonDict['observations'][-1]['positions'][-1]['aspects'].append({})
                    dataJsonDict['observations'][-1]['positions'][-1]['aspects'][-1]['name'] = keyAspect
                    dataJsonDict['observations'][-1]['positions'][-1]['aspects'][-1]['value'] = observations[keyObservation]['positions'][keyPosition]['aspects']['value']
                    dataJsonDict['observations'][-1]['positions'][-1]['aspects'][-1]['quality'] = observations[keyObservation]['positions'][keyPosition]['aspects']['quality']
                
    #pp.pprint(dataJsonDict)
    
    print(json.dumps(dataJsonDict, indent=4, ensure_ascii=False))

    log.info('End of main exiting')
    sys.exit()

