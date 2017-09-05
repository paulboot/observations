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
import csv

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

def read_csv_targets(filename):
    """
    Fill targets dictionary using a csv configuration file.
    
    Format:
       Naam;Plaats;Gebouw;SER;Kast;IP;Type;Rapport;Uplink;Opmerking;port-channel;interfaces1;interfaces2
       SWA-DEL-R-TH-094;Delft;R-gebouw;TH;K1;10.20.255.94;WS-C3850-48P;true;nvt;TH (buiten H-gebouw, in augustus);209;1/4/9;
       SWA-DEL-R-TG-095;Delft;R-gebouw;TG;K1;10.20.255.95;WS-C3850-48P;true;nvt;TG (garage buiten terrein, in augustus);210;1/4/10;
       SWA-DEL-E-0A-191;Delft;R-gebouw;0E;K1;10.20.255.191;WS-C3850-48P;true;nvt;;208;1/4/8;2/4/8
       SWA-DEL-R-0A-001;Delft;R-gebouw;0A;K1;10.20.255.1;WS-C4510R+E;true;nvt;;105;1/2/5;2/2/5
    :param interfaces: string with a CSV filename
    :rtype: none
    """

    log.info('Start reading router file: %s' % filename)
    with open(filename, 'rb') as f:
        reader = csv.DictReader(f, delimiter=';', quoting=csv.QUOTE_NONE)
        try:
            for row in reader:
                if row['Rapport'] == 'true':
                    places.add(row['Plaats'])
                    if building.has_key(row['Plaats']):
                        building[row['Plaats']].add(row['Gebouw'])
                    else:
                        building[row['Plaats']] = set()
                        building[row['Plaats']].add(row['Gebouw'])
                    key = (row['Plaats'],row['Gebouw'],row['Naam'])
                    targets[key] = {}
                    targets[key]['ip'] = row['IP']
                    targets[key]['ser'] = row['SER']
                    targets[key]['kast'] = row['Kast']
                    targets[key]['type'] = row['Type']
                    targets[key]['uplink'] = row['Uplink'].split(',')
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

if __name__ == '__main__':

    args = parseargs()
    debug = args.debug

    log.info('Start of main')

    ##CSV demo
    csvDemo = True
    if csvDemo:
        read_csv_targets(csvpath + '/' + targetsfile)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(targets)
        pp.pprint(places)
        pp.pprint(building)
    
    log.info('End of main exiting')
    sys.exit()

