from CaChannel import *

class epicsPV(CaChannel):
   def __init__(self, pvName=None, wait=1):
      self.monitored = 0
      self.newMonitor = 0
      self.putComplete = 0
      # Invoke the base class initialization
      CaChannel.__init__(self)
      if (pvName != None):
         if (wait):
            self.searchw(pvName)
         else:
            self.search(pvName)

   def setMonitor(self):
      self.add_masked_array_event(None, None, ca.DBE_VALUE, self.getCallBack, 0)
      self.monitored = 1

   def clearMonitor(self):
      self.clear_event
      self.monitored = 0

   def checkMonitor(self):
      m = self.newMonitor
      self.newMonitor = 0
      return m

   def getControl(self, req_type=None, count=None, wait=1, poll=.01):
      if (req_type == None): req_type = self.field_type()
      if (wait != 0): self.newMonitor = 0
      self.array_get_callback(ca.dbf_type_to_DBR_CTRL(req_type),
                              count, self.getCallBack, 0)
      if (wait != 0):
         while(self.newMonitor == 0):
            self.pend_event(poll)

   def array_get(self, req_type=None, count=None):
      if (self.monitored):
         self.newMonitor = 0
         return self.pv_value
      else:
         return CaChannel.array_get(self, req_type, count)

   def getw(self, req_type=None, count=None):
      if (self.monitored):
         self.newMonitor = 0
         if (count == None):
            return self.pv_value
         else:
            return self.pv_value[0:count]
      else:
         return CaChannel.getw(self, req_type, count)

   def putWait(self, value, req_type=None, count=None, poll=.01):
      self.putComplete=0
      self.array_put_callback(value, req_type, count, self.putCallBack, 0)
      while(self.putComplete == 0):
         self.pend_event(poll)

   def putCallBack(self, epicsArgs, userArgs):
      self.putComplete=1

   def getCallBack(self, epicsArgs, userArgs):
      self.newMonitor = 1
      for key in epicsArgs.keys():
         setattr(self, key, epicsArgs[key])

