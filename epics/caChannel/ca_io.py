#! /bin/env python
#
# filename: ca_io.py
#
# Test CaChannel io using ca.pend_io()
#	search
#	array_put
#	array_get
#	pend_io
#
# Each group of actions (search, put, get) is executed by the call
# to pend_io().  When the actions have completed pend_io() returns
# and the code continues.  Each call to pend_io() applies to all the
# channel objects and not just the object whose method is being invoked.
# A timeout value (specified in seconds) is associated with a call to
# pend_io() if no timeout is given the default value of one second is used.
#
# Values returned from a get are stored for retrieval after pend_io()
# has returned.  The returned values are accessed using the getValue()
# method.  If pend_io() returns an error status then all values read
# during processing are not guaranteed to be correct.
#

from CaChannel import *

def main():
    try:
	catest = CaChannel()
	cawave = CaChannel()
	scan = CaChannel()

	catest.search('catest')
	cawave.search('cawave')
	scan.search('catest.SCAN')
	catest.pend_io()
	
	t = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19)
	catest.array_put(123.456)
	cawave.array_put(t)
	scan.array_put("1 second", ca.DBR_STRING)
	cawave.pend_io()
	
	catest.array_get()
	cawave.array_get()
	scan.array_get()
	ca.pend_io(1.0)
	
	print catest.getValue()
	print cawave.getValue()
	print scan.getValue()
	
	scan.array_get(ca.DBR_STRING)
	scan.pend_io()
	print scan.getValue()
	
    except CaChannelException, status:
	print ca.message(status)
    
main()
