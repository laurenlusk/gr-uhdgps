#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
import pmt
import subprocess
import time
import tempfile
from gps3 import gps3

class gps_probe_e310(gr.sync_block):
    """
    docstring for block gps_probe_e310
    """
    def __init__(self, parent, target):
        gr.sync_block.__init__(self,
            name="gps_probe_e310",
            in_sig=[],
            out_sig=[])
        self.parent = parent
        self.target = target
        self.message_port_register_in(pmt.intern("pdus"))
        self.message_port_register_out(pmt.intern("pdus"))
        self.set_msg_handler(pmt.intern("pdus"), self.handler)
       # (self.gps_log, self.gps_log_path) = tempfile.mkstemp()
       # subprocess.Popen("gpspipe -r -o -d " + self.gps_log_path  + " -t | grep GPGGA", shell=True)

    def __del__(self):
        close(self.gps_log)
        # delete the log for security and space

    def work(self, input_items, output_items):
        assert(False)

    def handler(self, pdu):
        (ometa, data) = (pmt.to_python(pmt.car(pdu)), pmt.cdr(pdu))
        
        d = {}
        try:
            # grab all mboard sensor data
            uhd_source = eval("self.parent.%s"%(self.target))
            mbs = uhd_source.get_mboard_sensor_names()
            for k in mbs:
                v = uhd_source.get_mboard_sensor(k)
                d[k] = v.value
            #d["gps_location"] = str(self.gps_log.readlines()[-1])
	   # d["gps_location"] = str(subprocess.check_output['tail','-n','1', self.gps_log_path])
            d["gain"] = uhd_source.get_gain()
            d["gps_present"] = True

            gps_socket = gps3.GPSDSocket()
            data_stream = gps3.DataStream()
            gps_socket.connect()
            gps_socket.watch()
            for new_data in gps_socket:
                if new_data:
                    data_stream.unpack(new_data)
                    print 'Latitude = ', data_stream.TPV['lat']
            
        except AttributeError:
            d["gps_present"] = False
        
        ometa.update( d )
        self.message_port_pub(pmt.intern("pdus"), pmt.cons(pmt.to_pmt(ometa), data))


