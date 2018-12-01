#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016  Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

from __future__ import print_function

# Standard modules
import logging
import sys

# Twisted modules
from twisted.internet.protocol import ReconnectingClientFactory, Protocol
from twisted.protocols.basic import NetstringReceiver
from twisted.internet import reactor, task
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource

# Autobahn provides websocket service under Twisted
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

# Specific functions to import from standard modules
from pprint import pprint
from time import time, strftime, localtime
from cPickle import loads
from binascii import b2a_hex as h
from os.path import getmtime
from collections import deque

# Web templating environment
from jinja2 import Environment, PackageLoader, select_autoescape

# Utilities from K0USY Group sister project
from dmr_utils.utils import int_id, get_alias, try_download, mk_full_id_dict

# Configuration variables and IPSC constants
from config import *
#from ipsc_const import *

# Opcodes for reporting protocol to HBlink
OPCODE = {
    'CONFIG_REQ': '\x00',
    'CONFIG_SND': '\x01',
    'BRIDGE_REQ': '\x02',
    'BRIDGE_SND': '\x03',
    'CONFIG_UPD': '\x04',
    'BRIDGE_UPD': '\x05',
    'LINK_EVENT': '\x06',
    'BRDG_EVENT': '\x07',
    }

# Global Variables:
CONFIG      = {}
CTABLE      = {'MASTERS': {}, 'PEERS': {}, 'OPENBRIDGES': {}}
BRIDGES     = {}
BTABLE      = {}
BTABLE['BRIDGES'] = {}
BRIDGES_RX  = ''
CONFIG_RX   = ''
LOGBUF      = deque(100*[''], 100)
RED         = '#ff0000'
GREEN       = '#00ff00'
BLUE        = '#0000ff'
ORANGE      = '#ff8000'
WHITE       = '#ffffff'


# For importing HTML templates
def get_template(_file):
    with open(_file, 'r') as html:
        return html.read()

# Alias string processor
def alias_string(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'CITY', 'STATE')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return alias

def alias_short(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN', 'NAME')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)
        
def alias_call(_id, _dict):
    alias = get_alias(_id, _dict, 'CALLSIGN')
    if type(alias) == list:
        for x,item in enumerate(alias):
            if item == None:
                alias.pop(x)
        return ', '.join(alias)
    else:
        return str(alias)

# Build the HBlink connections table
def build_hblink_table(_config, _stats_table):
    for _hbp, _hbp_data in _config.iteritems(): 
        if _hbp_data['ENABLED'] == True:
            if _hbp_data['MODE'] == 'MASTER':
                _stats_table['MASTERS'][_hbp] = {}
                _stats_table['MASTERS'][_hbp]['REPEAT'] = _hbp_data['REPEAT']
                _stats_table['MASTERS'][_hbp]['PEERS'] = {}
                for _client in _hbp_data['PEERS']:
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)] = {}
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['CALLSIGN'] = _hbp_data['PEERS'][_client]['CALLSIGN']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['TX_FREQ'] = _hbp_data['PEERS'][_client]['TX_FREQ'][:3] + '.' + _hbp_data['PEERS'][_client]['TX_FREQ'][3:7]
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['RX_FREQ'] = _hbp_data['PEERS'][_client]['RX_FREQ'][:3] + '.' + _hbp_data['PEERS'][_client]['RX_FREQ'][3:7]
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['COLORCODE'] = _hbp_data['PEERS'][_client]['COLORCODE']
                    _slots = _hbp_data['PEERS'][_client]['SLOTS']
                    if (_slots <= '2'):
                        _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['SLOTS'] = _slots
                    elif (_slots == '3'):
                        _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['SLOTS'] = 'BOTH'
                    else:
                        _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['SLOTS'] = 'DMO'
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['LOCATION'] = _hbp_data['PEERS'][_client]['LOCATION']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['CONNECTION'] = _hbp_data['PEERS'][_client]['CONNECTION']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['IP'] = _hbp_data['PEERS'][_client]['IP']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['PINGS_RECEIVED'] = _hbp_data['PEERS'][_client]['PINGS_RECEIVED']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['LAST_PING'] = _hbp_data['PEERS'][_client]['LAST_PING']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)]['PORT'] = _hbp_data['PEERS'][_client]['PORT']
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][1]= {}
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][1]['TS'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][1]['TYPE'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][1]['SUB'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][1]['SRC'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][1]['DEST'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][2] = {}
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][2]['TS'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][2]['SUB'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][2]['TYPE'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][2]['SRC'] = ''
                    _stats_table['MASTERS'][_hbp]['PEERS'][int_id(_client)][2]['DEST'] = ''
            elif _hbp_data['MODE'] == 'PEER':
                _stats_table['PEERS'][_hbp] = {}
                _stats_table['PEERS'][_hbp]['CALLSIGN'] = _hbp_data['CALLSIGN']
                _stats_table['PEERS'][_hbp]['RADIO_ID'] = int_id(_hbp_data['RADIO_ID'])
                _stats_table['PEERS'][_hbp]['MASTER_IP'] = _hbp_data['MASTER_IP']
                _stats_table['PEERS'][_hbp]['STATS'] = _hbp_data['STATS']
            elif _hbp_data['MODE'] == 'OPENBRIDGE':
                _stats_table['OPENBRIDGES'][_hbp] = {}
                _stats_table['OPENBRIDGES'][_hbp]['NETWORK_ID'] = int_id(_hbp_data['NETWORK_ID'])
                _stats_table['OPENBRIDGES'][_hbp]['TARGET_IP'] = _hbp_data['TARGET_IP']
                _stats_table['OPENBRIDGES'][_hbp]['TARGET_PORT'] = _hbp_data['TARGET_PORT']
    return(_stats_table)
    
def update_hblink_table(_config, _stats_table):
    
    pprint(_config)
    print
    pprint(_stats_table)
    for _hbp, _hbp_data in _config.iteritems():
        _stats_peers = _stats_table['MASTERS'][_hbp]['PEERS']
        
        # if this peer is the master
        if _stats_table[_ipsc]['MASTER'] == False:
            _peer = _config[_ipsc]['MASTER']['RADIO_ID']
            _config_peer_data = _config[_ipsc]['MASTER']
            
            _stats_peers[_peer]['RADIO_ID'] = int_id(_peer)
            update_peer(_stats_peers, _peer, _config_peer_data)

        # for all of the peers that are not the master... update or add
        for _peer, _config_peer_data in _config[_ipsc]['PEERS'].iteritems():
            if _peer != _config[_ipsc]['LOCAL']['RADIO_ID']:
                _stats_peers = _stats_table[_ipsc]['PEERS']
            
                # update the peer if we already have it
                if _peer in _stats_table[_ipsc]['PEERS']:
                    update_peer(_stats_peers, _peer, _config_peer_data)
            
                # addit if we don't have it
                if _peer not in _stats_table[_ipsc]['PEERS']:
                    add_peer(_stats_peers, _peer, _config_peer_data, 'peer')

        # for peers that need to be removed, never the master. This is complicated
        peers_to_delete = []
        
        # find any peers missing in the config update    
        for _peer, _stats_peer_data in _stats_table[_ipsc]['PEERS'].iteritems():
            if _peer not in _config[_ipsc]['PEERS'] and _peer != _config[_ipsc]['MASTER']['RADIO_ID']:
                peers_to_delete.append(_peer)
        
        # delte anything identified from the right part of the stats table
        delete_peers(peers_to_delete, _stats_table[_ipsc]['PEERS'])
        
#
# CONFBRIDGE TABLE FUNCTIONS
#
def build_bridge_table(_bridges):
    _stats_table = {}
    _now = time()
    _cnow = strftime('%Y-%m-%d %H:%M:%S', localtime(_now))
    
    for _bridge, _bridge_data in _bridges.iteritems():
        _stats_table[_bridge] = {}

        for system in _bridges[_bridge]:
            _stats_table[_bridge][system['SYSTEM']] = {}
            _stats_table[_bridge][system['SYSTEM']]['TS'] = system['TS']
            _stats_table[_bridge][system['SYSTEM']]['TGID'] = int_id(system['TGID'])
            
            if system['TO_TYPE'] == 'ON' or system['TO_TYPE'] == 'OFF':
                if system['TIMER'] - _now > 0:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = int(system['TIMER'] - _now)
                else:
                    _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'Expired'
                if system['TO_TYPE'] == 'ON':
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Disconnect'
                else:
                    _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'Connect'
            else:
                _stats_table[_bridge][system['SYSTEM']]['EXP_TIME'] = 'N/A'
                _stats_table[_bridge][system['SYSTEM']]['TO_ACTION'] = 'None'
            
            if system['ACTIVE'] == True:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Connected'
                _stats_table[_bridge][system['SYSTEM']]['COLOR'] = GREEN
            elif system['ACTIVE'] == False:
                _stats_table[_bridge][system['SYSTEM']]['ACTIVE'] = 'Disconnected'
                _stats_table[_bridge][system['SYSTEM']]['COLOR'] = RED
            
            for i in range(len(system['ON'])):
                system['ON'][i] = str(int_id(system['ON'][i]))
                    
            _stats_table[_bridge][system['SYSTEM']]['TRIG_ON'] = ', '.join(system['ON'])
            
            for i in range(len(system['OFF'])):
                system['OFF'][i] = str(int_id(system['OFF'][i]))
                
            _stats_table[_bridge][system['SYSTEM']]['TRIG_OFF'] = ', '.join(system['OFF'])
    return _stats_table

#
# BUILD HBlink AND CONFBRIDGE TABLES FROM CONFIG/BRIDGES DICTS
#          THIS CURRENTLY IS A TIMED CALL
#
build_time = time()
def build_stats():
    global build_time
    now = time()
    if True: #now > build_time + 1:
        if CONFIG:
            table = 'd' + dtemplate.render(_table=CTABLE)
            dashboard_server.broadcast(table)
        if BRIDGES:
            table = 'b' + btemplate.render(_table=BTABLE['BRIDGES'])
            dashboard_server.broadcast(table)
        build_time = now

def table_update(p):
    action = p[1]
    system = p[2]
    timeSlot = int(p[6])
    callType = p[0]
    sourceSub = int(p[5])
    sourcePeer = int(p[4])
    destination = int(p[7])

    if system in CTABLE['MASTERS']:
        if action == 'START':
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['TS'] = True
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['TYPE'] = callType
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['SUB'] = sourceSub
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['SRC'] = sourcePeer
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['DEST'] = destination
        if action == 'END':
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['TS'] = False
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['TYPE'] = ''
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['SUB'] = ''
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['SRC'] = ''
            CTABLE['MASTERS'][system]['PEERS'][sourcePeer][timeSlot]['DEST'] = ''       

        build_stats()
#
# PROCESS IN COMING MESSAGES AND TAKE THE CORRECT ACTION DEPENING ON THE OPCODE
#
def process_message(_message):
    global CTABLE, CONFIG, BRIDGES, CONFIG_RX, BRIDGES_RX
    opcode = _message[:1]
    _now = strftime('%Y-%m-%d %H:%M:%S %Z', localtime(time()))
    
    if opcode == OPCODE['CONFIG_SND']:
        logging.debug('got CONFIG_SND opcode')
        CONFIG = load_dictionary(_message)
        CONFIG_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        if CTABLE:
            update_hblink_table(CONFIG, CTABLE)
        else:
            build_hblink_table(CONFIG, CTABLE)
    
    elif opcode == OPCODE['BRIDGE_SND']:
        logging.debug('got BRIDGE_SND opcode')
        BRIDGES = load_dictionary(_message)
        BRIDGES_RX = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        BTABLE['BRIDGES'] = build_bridge_table(BRIDGES)
        
    elif opcode == OPCODE['LINK_EVENT']:
        logging.info('LINK_EVENT Received: {}'.format(repr(_message[1:])))
        
    elif opcode == OPCODE['BRDG_EVENT']:
        logging.info('BRIDGE EVENT: {}'.format(repr(_message[1:])))
        p = _message[1:].split(",")
        table_update(p)
        if p[0] == 'GROUP VOICE':
            if p[1] == 'END':
                log_message = '{}: {} {}:   SYS: {:12.12s} SRC: {:8.8s}; {:15.15s} TS: {} TGID: {:>5s} SUB: {:8.8s}; {:30.30s} Time: {}s'.format(_now, p[0], p[1], p[2], p[4], alias_call(int(p[4]), peer_ids), p[6], p[7], p[5], alias_short(int(p[5]), subscriber_ids), p[8])
            elif p[1] == 'START':
                log_message = '{}: {} {}: SYS: {:12.12s} SRC: {:8.8s}; {:15.15s} TS: {} TGID: {:>5s} SUB: {:8.8s}; {:30.30s}'.format(_now, p[0], p[1], p[2], p[4], alias_call(int(p[4]), peer_ids), p[6], p[7], p[5], alias_short(int(p[5]), subscriber_ids))
            elif p[1] == 'END WITHOUT MATCHING START':
                log_message = '{}: {} {} on SYSTEM {:12.12s}: SRC: {:8.8s}; {}:15.15s TS: {} TGID: {:>5s} SUB: {:8.8s}; {:30.30s}'.format(_now, p[0], p[1], p[2], p[4], alias_call(int(p[4]), peer_ids), p[6], p[7], p[5], alias_short(int(p[5]), subscriber_ids))
            else:
                log_message = '{}: UNKNOWN GROUP VOICE LOG MESSAGE'.format(_now)
        else:
            log_message = '{}: UNKNOWN LOG MESSAGE'.format(_now)
            
        dashboard_server.broadcast('l' + log_message)
        LOGBUF.append(log_message)
    else:
        logging.debug('got unknown opcode: {}, message: {}'.format(repr(opcode), repr(_message[1:])))


def load_dictionary(_message):
    data = _message[1:]
    return loads(data)
    logging.debug('Successfully decoded dictionary')

#
# COMMUNICATION WITH THE HBlink INSTANCE
#
class report(NetstringReceiver):
    def __init__(self):
        pass

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass
        
    def stringReceived(self, data):
        process_message(data)


class reportClientFactory(ReconnectingClientFactory):
    def __init__(self):
        logging.info('reportClient object for connecting to HBlink.py created at: %s', self)
        
    def startedConnecting(self, connector):
        logging.info('Initiating Connection to Server.')
        if 'dashboard_server' in locals() or 'dashboard_server' in globals():
            dashboard_server.broadcast('q' + 'Connection to HBlink Established')

    def buildProtocol(self, addr):
        logging.info('Connected.')
        logging.info('Resetting reconnection delay')
        self.resetDelay()
        return report()

    def clientConnectionLost(self, connector, reason):
        logging.info('Lost connection.  Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        dashboard_server.broadcast('q' + 'Connection to HBlink Lost')

    def clientConnectionFailed(self, connector, reason):
        logging.info('Connection failed. Reason: %s', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


#
# WEBSOCKET COMMUNICATION WITH THE DASHBOARD CLIENT
#
class dashboard(WebSocketServerProtocol):
        
    def onConnect(self, request):
        logging.info('Client connecting: %s', request.peer)

    def onOpen(self):
        logging.info('WebSocket connection open.')
        self.factory.register(self)
        self.sendMessage('d' + str(dtemplate.render(_table=CTABLE)))
        self.sendMessage('b' + str(btemplate.render(_table=BTABLE['BRIDGES'])))
        for _message in LOGBUF:
            if _message:
                self.sendMessage('l' + _message)

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info('Binary message received: %s bytes', len(payload))
        else:
            logging.info('Text message received: %s', payload.decode('utf8'))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

    def onClose(self, wasClean, code, reason):
        logging.info('WebSocket connection closed: %s', reason)


class dashboardFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            logging.info('registered client %s', client.peer)
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            logging.info('unregistered client %s', client.peer)
            self.clients.remove(client)

    def broadcast(self, msg):
        logging.debug('broadcasting message to: %s', self.clients)
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            logging.debug('message sent to %s', c.peer)
            
#
# STATIC WEBSERVER
#
class web_server(Resource):
    isLeaf = True
    def render_GET(self, request):
        logging.info('static website requested: %s', request)
        if request.uri == '/':
            return index_html
        else:
            return 'Bad request'




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,filename = (LOG_PATH + LOG_NAME), filemode='a')

    logging.info('web_tables.py starting up')
    
    # Download alias files
    result = try_download(PATH, 'peer_ids.csv', PEER_URL, (FILE_RELOAD * 86400))
    logging.info(result)
   
    result = try_download(PATH, 'subscriber_ids.csv', SUBSCRIBER_URL, (FILE_RELOAD * 86400))
    logging.info(result)
    
    # Make Alias Dictionaries
    peer_ids = mk_full_id_dict(PATH, PEER_FILE, 'peer')
    if peer_ids:
        logging.info('ID ALIAS MAPPER: peer_ids dictionary is available')
        
    subscriber_ids = mk_full_id_dict(PATH, SUBSCRIBER_FILE, 'subscriber')
    if subscriber_ids:
        logging.info('ID ALIAS MAPPER: subscriber_ids dictionary is available')
    
    talkgroup_ids = mk_full_id_dict(PATH, TGID_FILE, 'tgid')
    if talkgroup_ids:
        logging.info('ID ALIAS MAPPER: talkgroup_ids dictionary is available')
    
    local_subscriber_ids = mk_full_id_dict(PATH, LOCAL_SUB_FILE, 'subscriber')
    if local_subscriber_ids:
        logging.info('ID ALIAS MAPPER: local_subscriber_ids added to subscriber_ids dictionary')
        subscriber_ids.update(local_subscriber_ids)
        
    local_peer_ids = mk_full_id_dict(PATH, LOCAL_PEER_FILE, 'peer')
    if local_peer_ids:
        logging.info('ID ALIAS MAPPER: local_peer_ids added peer_ids dictionary')
        peer_ids.update(local_peer_ids)
    
    # Jinja2 Stuff
    env = Environment(
        loader=PackageLoader('web_tables', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    dtemplate = env.get_template('hblink_table.html')
    btemplate = env.get_template('bridge_table.html')
    
    # Create Static Website index file
    index_html = get_template(PATH + 'index_template.html')
    index_html = index_html.replace('<<<system_name>>>', REPORT_NAME)
    
    # Start update loop
    update_stats = task.LoopingCall(build_stats)
    update_stats.start(FREQUENCY)
    
    # Connect to HBlink
    reactor.connectTCP(HBLINK_IP, HBLINK_PORT, reportClientFactory())
    
    # Create websocket server to push content to clients
    dashboard_server = dashboardFactory('ws://*:9000')
    dashboard_server.protocol = dashboard
    reactor.listenTCP(9000, dashboard_server)

    # Create static web server to push initial index.html
    website = Site(web_server())
    reactor.listenTCP(WEB_SERVER_PORT, website)

    reactor.run()
