from CaChannel import *

class callBack:
   def __init__(self):
      self.newMonitor = 0
      self.putComplete = 0
      self.monitorState = 0

class epicsPV(CaChannel):
   def __init__(self, pvName=None, wait=1):
      # monitorState:  
      #   0=not monitored 
      #   1=monitor requested, but no callback yet
      #   2=monitor requested, callback has arrived
      # Invoke the base class initialization
      self.callBack = callBack()
      CaChannel.__init__(self)
      if (pvName != None):
         if (wait):
            self.searchw(pvName)
         else:
            self.search(pvName)

   def setMonitor(self):
      self.add_masked_array_event(None, None, ca.DBE_VALUE, 
                                  getCallBack, self.callBack)
      self.callBack.monitorState = 1

   def clearMonitor(self):
      self.clear_event()
      self.callBack.monitorState = 0

   def checkMonitor(self):
      # This should be self.poll(), but that is generating errors
      self.pend_event(.0001)
      m = self.callBack.newMonitor
      self.callBack.newMonitor = 0
      return m

   def getControl(self, req_type=None, count=None, wait=1, poll=.01):
      if (req_type == None): req_type = self.field_type()
      if (wait != 0): self.callBack.newMonitor = 0
      self.array_get_callback(ca.dbf_type_to_DBR_CTRL(req_type),
                              count, getCallBack, self.callBack)
      if (wait != 0):
         while(self.callBack.newMonitor == 0):
            self.pend_event(poll)

   def array_get(self, req_type=None, count=None):
      if (self.callBack.monitorState != 0):
         # This should be self.poll(), but that is generating errors
         self.pend_event(.0001)
      if (self.callBack.monitorState == 2):
         self.callBack.newMonitor = 0
         return self.callBack.pv_value
      else:
         return CaChannel.array_get(self, req_type, count)

   def getw(self, req_type=None, count=None):
      if (self.callBack.monitorState != 0):
         # This should be self.poll(), but that is generating errors
         self.pend_event(.0001)
      if (self.callBack.monitorState == 2):
         self.callBack.newMonitor = 0
         if (count == None):
            return self.callBack.pv_value
         else:
            return self.callBack.pv_value[0:count]
      else:
         return CaChannel.getw(self, req_type, count)

   def getValue(self):
      if (self.callBack.monitorState != 0):
         # This should be self.poll(), but that is generating errors
         self.pend_event(.0001)
      if (self.callBack.monitorState == 2):
         self.callBack.newMonitor = 0
         return self.callBack.pv_value
      else:
         return CaChannel.getValue(self)

   def putWait(self, value, req_type=None, count=None, poll=.01):
      self.callBack.putComplete=0
      self.array_put_callback(value, req_type, count, putCallBack, self.callBack)
      while(self.callBack.putComplete == 0):
         self.pend_event(poll)

def putCallBack(epicsArgs, userArgs):
   userArgs[0].putComplete=1

def getCallBack(epicsArgs, userArgs):
   if (userArgs[0].monitorState == 1): userArgs[0].monitorState = 2
   userArgs[0].newMonitor = 1
   for key in epicsArgs.keys():
      setattr(userArgs[0], key, epicsArgs[key])

