from CaChannel import *

def getCallBack(epicsArgs, userArgs):
   data=epicsArgs['pv_value']
   print 'In callback', data[900:1100]

c = CaChannel()
c.searchw('13LAB:aim_adc1')
data = c.getw()
print data[900:1100]

c.add_masked_array_event(None, None, ca.DBE_VALUE, getCallBack, 0)
c.pend_event()

c.clear_event()

