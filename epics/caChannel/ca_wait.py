#! /bin/env python
#
# filename: ca_wait.py
#
# Test the simple CA methods
#	searchw
#	putw
#	getw
#
# Each of the actions (search, put, get) ending with a "w" signifies
# that the action completes before the function returns.  In CA terms
# this means that a call to ca_pend_io() is issued to force the action
# to process and wait for the action to complete.  When an exception
# occurs the offending CA status return is printed using
# print ca.message(status).
#

from CaChannel import *

def main():
    
    # write and read an analog input record
    try:
	catest = CaChannel()
	catest.searchw('catest')
        catest.putw(55)
	print catest.getw()
    except CaChannelException, status:
        print ca.message(status)

    # write and read a waveform record
    try:
	cawave = CaChannel()
        cawave.searchw('cawave')
	l = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
        cawave.putw(l)
	print cawave.getw()
    except CaChannelException, status:
        print ca.message(status)

main()
