from epicsPV import *

class epicsScaler:
   def __init__(self, name):
      self.nchans = epicsPV(name+'.NCH').getw()
      self.pvs = {'count': epicsPV(name+'.CNT'), 
                  'preset_time': epicsPV(name+'.TP'),
                  'preset':[], 'counts':[], 'label':[]}
      for i in range(1, self.nchans+1): 
         self.pvs['preset'].append(epicsPV(name+'.PR'+str(i)))
         self.pvs['counts'].append(epicsPV(name+'.S'+str(i)))
         self.pvs['label'].append(epicsPV(name+'.NM'+str(i)))

   def start(self, time=None):
      if (time != None):
         self.pvs['count'].putw(0)
         self.pvs['preset_time'].putw(time)
         self.pvs['count'].putw(1)
      else:
         self.pvs['count'].putw(0)
         self.pvs['count'].putw(1)

   def stop(self):
      self.pvs['count'].putw(0)

   def read(self, scaler=None):
      if (scaler == None):
         counts = []
         for i in range(self.nchans):
            self.pvs['counts'][i].array_get()
         self.pvs['count'].pend_io()
         for i in range(self.nchans):
            counts.append(self.pvs['counts'][i].getValue())
      else:
         counts = self.pvs['counts'][scaler].getw()
      return counts
   
   def get_label(self, scaler=None):
      if (scaler == None):
         labels = []
         for i in range(self.nchans):
            self.pvs['label'][i].array_get()
         self.pvs['count'].pend_io()
         for i in range(self.nchans):
            labels.append(self.pvs['label'][i].getValue())
      else:
         labels = self.pvs['label'][scaler].getw()
      return labels

   def set_label(self, label, scaler):
      self.pvs['label'][scaler].putw(label)

   def wait(self, start=None, stop=None, poll=0.1):
      if (start == None) and (stop == None): stop=1
      if (start != None):
         while(1):
            counting = self.pvs['count'].getw()
            if (counting != 0): break
            time.sleep(poll)
      if (stop != None):
         while(1):
            counting = self.pvs['count'].getw()
            if (counting == 0): break
            time.sleep(poll)
