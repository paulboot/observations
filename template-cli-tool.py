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
    with open('observation-column-example1 20170908.json', 'r') as f:
        dataJson = json.load(f)
        #pp.pprint(dataJson)

    for observationJson in dataJson['observations']:
        keyObservation = observationJson['startTime'],observationJson['endTime']
        observations[keyObservation] = {}
        observations[keyObservation]['phenomenonTime'] = observationJson['phenomenonTime']

        #Process Values
        observations[keyObservation]['process'] = {}
        observations[keyObservation]['process']['intervalLength'] = observationJson['process']['intervalLength']
        observations[keyObservation]['process']['name'] = observationJson['process']['name']
        observations[keyObservation]['process']['aspectSet'] = observationJson['process']['aspectSet']

        #Aspect Meta Values
        for aspectMetaValuesJson in observationJson['aspectMetaValues']:
            keyAspectMetaValue = aspectMetaValuesJson['name']
            if 'keyAspectMetaValue' not in observations[keyObservation]:
                observations[keyObservation]['aspectMetaValues'] = {}
            bla observations[keyObservation]['aspectMetaValues'] = {}
            observations[keyObservation]['aspectMetaValues'][keyAspectMetaValue]['name'][] = aspectMetaValuesJson
        
        for positionJson in observationJson['positions']:
            keyPosition = (positionJson['offset']['x'],positionJson['offset']['y'],positionJson['offset']['z'])
            if 'positions' not in observations[keyObservation]:
                observations[keyObservation]['positions'] = {}
            observations[keyObservation]['positions'][keyPosition] = {}
            observations[keyObservation]['positions'][keyPosition]['offset'] = {}
            observations[keyObservation]['positions'][keyPosition]['offset']['unit'] = positionJson['offset']['unit']
            for aspectJson in positionJson['aspects']:
                keyAspect = aspectJson['name']
                if 'aspects' not in observations[keyObservation]['positions'][keyPosition]:
                    observations[keyObservation]['positions'][keyPosition]['aspects'] = {}
                observations[keyObservation]['positions'][keyPosition]['aspects'][keyAspect] = {}
                observations[keyObservation]['positions'][keyPosition]['aspects'][keyAspect] = aspectJson

    pp.pprint(observations)
    sys.exit()

    #Example manipulation
    #observations['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z']['positions'][(0, 0, -1.0)]['aspects']['average']['value']=10000
    #observations['2017-02-07T13:07:00Z','2017-02-07T13:07:59Z']['positions'][(0, 0, -2.0)]['aspects']['average']['value']=50000
    #print(observations['2017-02-07T13:06:00Z','2017-02-07T13:06:59Z']['positions'][(0, 0, -1.0)]['aspects']['average']['value'])
    #print(observations['2017-02-07T13:07:00Z','2017-02-07T13:07:59Z']['positions'][(0, 0, -2.0)]['aspects']['average']['value'])

    #sys.exit()
    
    #fails because need to build back structure
    #print(json.dumps(observations, indent=4, sort_keys=True, ensure_ascii=False))
    
    #read file data from 3 RMI stations to observations dict
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

        
    dataJson={}
    #TODO fill in symple things
    dataJson['observations'] = []
    for keyObservation in observations:
        startTimeStr, endTimeStr = keyObservation
        dataJson['observations'].append({})
        dataJson['observations'][-1]['startTime'] = startTimeStr
        dataJson['observations'][-1]['endTime'] = endTimeStr
        dataJson['observations'][-1]['phenomenonTime'] = observations[keyObservation]['phenomenonTime']
        for keyPosition in observations[keyObservation]['positions']:
            positionOffsetX, positionOffsetY, positionOffsetZ = keyPosition
            if 'positions' not in dataJson['observations'][-1]:
                dataJson['observations'][-1]['positions'] = []
            dataJson['observations'][-1]['positions'].append({})
            dataJson['observations'][-1]['positions'][-1]['offset'] = {}
            dataJson['observations'][-1]['positions'][-1]['offset']['x'] = positionOffsetX
            dataJson['observations'][-1]['positions'][-1]['offset']['y'] = positionOffsetY
            dataJson['observations'][-1]['positions'][-1]['offset']['z'] = positionOffsetZ
            dataJson['observations'][-1]['positions'][-1]['offset']['unit'] = observations[keyObservation]['positions'][keyPosition]['offset']['unit']
            for keyAspect in observations[keyObservation]['positions'][keyPosition]:
                if keyAspect == 'aspects':
                    if 'aspects' not in dataJson['observations'][-1]['positions'][-1]:
                        dataJson['observations'][-1]['positions'][-1]['aspects'] = []
                    dataJson['observations'][-1]['positions'][-1]['aspects'].append({})
                    dataJson['observations'][-1]['positions'][-1]['aspects'][-1]['name'] = keyAspect
                    dataJson['observations'][-1]['positions'][-1]['aspects'][-1]['value'] = observations[keyObservation]['positions'][keyPosition]['aspects']['value']
                    dataJson['observations'][-1]['positions'][-1]['aspects'][-1]['quality'] = observations[keyObservation]['positions'][keyPosition]['aspects']['quality']
                
    pp.pprint(dataJson)
    
    print(json.dumps(dataJson, indent=4, ensure_ascii=False))

    log.info('End of main exiting')
    sys.exit()

