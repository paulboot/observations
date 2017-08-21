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
# sudo apt-get install python-dnspython python-jinja2 python-paramiko

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
    
    ##CSV demo
    csvDemo = False
    if csvDemo:
        read_csv_targets(csvpath + '/' + targetsfile)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(targets)
        pp.pprint(places)
        pp.pprint(building)
    
    ##JSON demo
    dataDict = {}
    jsonDemo = True
    if jsonDemo:
        with open('observation-column-example1.json', 'r') as f:
            data = json.load(f)
            pp = pprint.PrettyPrinter(indent=4)
            #pp.pprint(data)
        
        for position in data['positions']:
            pp.pprint(position)
            keyPosition = (position['offsetX'],position['offsetY'],position['offsetZ'])
            print(keyPosition)
            dataDict[keyPosition] = {}
            dataDict[keyPosition]['offsetUnit'] = position['offsetUnit']
            for aspect in position['aspects']:
                keyAspect = aspect['name']
                print(keyAspect)
                dataDict[keyPosition][keyAspect] = {}
                dataDict[keyPosition][keyAspect] = aspect

        pp.pprint(dataDict)
        dataDict[(0, 0, -1.0)]['average']['value']=10000
        pp.pprint(dataDict)

    log.info('End of main exiting')
    sys.exit()

