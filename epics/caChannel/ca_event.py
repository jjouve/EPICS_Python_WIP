#! /bin/env python
#
# filename: ca_event.py
#
# Test CaChannel monitors
#	search
#	pend_io
#	fdmgr_start()
#	fdmgr_pend
#	add_masked_array_event
#
#
# Once this program is running you must connect to 'catest'
# from a separate program.  Each time you write a new value
# to 'catest' the monitor will execute the callback.
#

from CaChannel import *
import time
import sys

def eventCb(epics_args, user_args):
    print "eventCb: Python callback function"
    print type(epics_args)
    print epics_args
    print ca.message(epics_args['status'])
    print "new value = ", epics_args['pv_value']
    print ca.alarmSeverityString(epics_args['pv_severity'])
    print ca.alarmStatusString(epics_args['pv_status'])


def main():
    ca.fdmgr_start()
    try:
	chan = CaChannel()
	print 'search for "catest"'
	chan.search('catest')
	chan.pend_io()
    except CaChannelException, status: 
	print ca.message(status)

    try:
	print 'add event'
	chan.add_masked_array_event(ca.dbf_type_to_DBR_STS(chan.field_type()),
				None, ca.DBE_VALUE | ca.DBE_ALARM, eventCb)
    except CaChannelException, status: 
	print ca.message(status)

    while 1:
	ca.fdmgr_pend()

main()
