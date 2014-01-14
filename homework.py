## Copyright (C) 2010 Richard Mortier <mort@cantab.net>.
## All Rights Reserved.
##
## This program is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public License
## as published by the Free Software Foundation, either version 3 of
## the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public
## License along with this program.  If not, see
## <http://www.gnu.org/licenses/>.

import sys, traceback
import time, re
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop

from nox.netapps.hwdb.pyhwdb import pyhwdb

from nox.lib import core, util

Homework = None


##
## utility functions
##

def is_valid_ip(ip):
    """ Test if string is valid representation of IP address. """
    quads = ip.split(".")
    if len(quads) != 4: return False

    try: return reduce(lambda acc, quad: (0 <= quad <= 255) and acc, map(int, quads), True)
    except ValueError: return False

def is_valid_eth(eth):
    """ Test if string is valid representation of Ethernet address. """
    if not eth: return False
    bytes = eth.split(":")

    if len(bytes) != 6: return False

    try: return reduce(lambda acc, byte: (0 <= byte <= 256) and acc,
                       map(lambda b: int(b, 16), bytes), True)
    except ValueError: return False

def formatMacAddress(mac):
    if "-" in mac:
        return mac.replace("-", ":")
    if ":" in mac:
        return mac

    return mac[0:2] + ":" + mac[2:4] + ":" + mac[4:6] + ":" + mac[6:8] + ":" + mac[8:10] + ":" + mac[10:12]

def handler(message=None):
    print "handling... %s" % (message)
    command = message.split(" ")
    devices = []
    devices.append({'mac': command[0], 'action':command[1]})
    Homework._hwdb.postEvent(devices)
   
    
def setup():
    try:
        Homework.bus.add_signal_receiver(handler,dbus_interface="test.signal.Type", signal_name="udev")
        #read in permitted devices here and post permits to nox
    except:
        traceback.print_exc(file = sys.stdout)

def run_glib():
    """process glib events within nox"""
    context = gobject.MainLoop().get_context()
    
    def mainloop():
        while context.pending():
            context.iteration(False)
        Homework.post_callback(0.0001, mainloop)
    
    mainloop() #kick it off
##
## main
##

class homework(core.Component):
    """ Main application. """

    def __init__(self, ctxt):
        core.Component.__init__(self, ctxt)
        global Homework
        Homework = self
        Homework.last = None
        
        
    def install(self):
        # gettting a reference for the hwdb component
        self._hwdb = self.resolve(pyhwdb)
        # print "hwdb obj " + str(self._hwdb)
        DBusGMainLoop(set_as_default=True)
        self.bus  = dbus.SystemBus()
        gobject.threads_init()
        run_glib()
        setup()

    def getInterface(self): return str(homework)

def getFactory():
    class Factory:
        def instance(self, ctxt): return homework(ctxt)
    return Factory()