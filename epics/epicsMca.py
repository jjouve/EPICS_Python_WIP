import os
import string
import time
if (os.name != 'nt'):  # ca nor working yet
   from epicsPV import *
from Mca import *
import Xrf

#######################################################################
class epicsMca(Mca):
   def __init__(self, record_name, environment_file='catch1d.env'):
      """
      PURPOSE:
         This is the initialization code which is invoked when a new object of
         type epicsMca is created.  It cannot be called directly, but only
         indirectly by the epicsMca() function.
      CALLING SEQUENCE:
         mca = epicsMca(record_Name)
      INPUTS:
         record_Name:  The name of the EPICS MCA record for the MCA object
                       being created.  This record name can include a field
                       name which will be stripped off.  For example,
                      '13IDC:mca1' and '13IDC:mca1.DESC' are both
                       valid.  This makes it convenient when dragging process
                       variable names from MEDM windows to Python windows.
      KEYWORD_PARAMETERS:
         environment_file:
            This keyword can be used to specify the name of a file which
            contains the names of EPICS process variables which should be saved
            in the header of files written with Mca.write_file().  If this
            keyword is not specified then this function will attempt to open
            a file called 'catch1d.env' in the current directory.  This is done
            to be compatible with the data catcher program.  This is an ASCII
            with each line containing a process variable name, followed by a
            space and a description field.

      OUTPUTS:
         This function returns a valid object if it was able to
         establish channel access communication with the specified EPICS MCA
         record.  Returns None if not able to.
      EXAMPLE:
        from epicsMca import *
        mca = epicsMca('13IDC:mca1')
        print mca.data
      """
      Mca.__init__(self)
      self.max_rois = 32
      self.record_name = record_name
      self.name = record_name
      self.sequence = 0
      self.pvs = {'calibration': 
                    {'calo': None,
                     'cals': None,
                     'calq': None,
                     'tth' : None,
                     'egu' : None},
                  'presets':
                    {'prtm': None,
                     'pltm': None,
                     'pct':  None,
                     'pctl': None,
                     'pcth': None,
                     'chas': None,
                     'dwel': None,
                     'pscl': None},
                  'elapsed':
                    {'ertm': None,
                     'eltm': None,
                     'act' : None,
                     'rtim': None,
                     'stim': None},
                  'acquire':
                    {'strt': None,
                     'stop': None,
                     'eras': None,
                     'acqg': None,
                     'proc': None,
                     'erst': None},
                  'data':
                    {'nuse': None,
                     'nmax': None,
                     'val':  None}}
      for group in self.pvs.keys():
         for pv in self.pvs[group].keys():
            name = self.record_name + '.' + string.upper(pv)
            self.pvs[group][pv] = epicsPV(name, wait=0)
      # Construct the names of the PVs for the ROIs
      self.roi_def_pvs=[]
      self.roi_data_pvs=[]
      for i in range(self.max_rois):
         n = 'R'+str(i)
         r = {n+'lo'  : None,
              n+'hi'  : None,
              n+'bg'  : None,
              n+'nm'  : None}
         self.roi_def_pvs.append(r)
         r = {n       : None,
              n+'n'   : None}
         self.roi_data_pvs.append(r)
      for roi in range(self.max_rois):
         for pv in self.roi_def_pvs[roi].keys():
            name = self.record_name + '.' + string.upper(pv)
            self.roi_def_pvs[roi][pv] = epicsPV(name, wait=0)
         for pv in self.roi_data_pvs[roi].keys():
            name = self.record_name + '.' + string.upper(pv)
            self.roi_data_pvs[roi][pv] = epicsPV(name, wait=0)

      # Construct the names of the PVs for the environment
      self.read_environment_file(environment_file)
      self.env_pvs = []
      for env in self.environment:
         self.env_pvs.append(epicsPV(env.name, wait=0))

      # Wait for all PVs to connect
      self.pvs['calibration']['calo'].pend_io()

      # ClientWait does not exist in simple_mca.db, which is used
      # for multi-element detectors.  We see if it exists by trying to connect
      # with a short timeout.
      client_wait = epicsPV(self.record_name + 'ClientWait', wait=0)
      enable_wait = epicsPV(self.record_name + 'EnableWait', wait=0)
      try:
         client_wait.pend_io(.01)
         self.pvs['acquire']['client_wait'] = client_wait
         self.pvs['acquire']['enable_wait'] = enable_wait
      except:
         self.pvs['acquire']['client_wait'] = None
         self.pvs['acquire']['enable_wait'] = None

      # Put monitors on the VAL, NUSE and ACQG fields
      # Bug - this does not work yet, data read back are corrupt
      # self.pvs['data']['nuse'].setMonitor()
      # self.pvs['data']['val'].setMonitor()
      # self.pvs['acquire']['acqg'].setMonitor()

      # Read all of the information from the record
      self.get_calibration()
      self.get_presets()
      self.get_elapsed()
      self.get_rois()
      self.get_data()
 

   #######################################################################
   def read_environment_file(self, file):
      self.environment = []
      try:
         fp = open(file, 'r')
         lines = fp.readlines()
         fp.close()
      except:
         return
      for line in lines:
          env = McaEnvironment()
          pos = find(line, ' ')
          if (pos != -1):
             env.name = line[0:pos]
             description = line[pos+1:]
          else:
             env.name = line
             env.description = ' '
          self.environment.apppend(env)

   #######################################################################
   def get_calibration(self):
      calibration = McaCalibration()
      pvs = self.pvs['calibration']
      for pv in pvs.keys():
         pvs[pv].array_get()
      pvs[pv].pend_io()
      calibration.offset    = pvs['calo'].getValue()
      calibration.slope     = pvs['cals'].getValue()
      calibration.quad      = pvs['calq'].getValue()
      calibration.two_theta = pvs['tth'].getValue()
      calibration.units     = pvs['egu'].getValue()
      Mca.set_calibration(self, calibration)
      return calibration

   #######################################################################
   def set_calibration(self, calibration):
      Mca.set_calibration(self, calibration)
      pvs = self.pvs['calibration']
      pvs['calo'].array_put(calibration.offset)
      pvs['cals'].array_put(calibration.slope)
      pvs['calq'].array_put(calibration.quad)
      pvs['tth'].array_put(calibration.two_theta)
      pvs['egu'].array_put(calibration.units)
      pvs['egu'].pend_io()

   #######################################################################
   def get_presets(self):
      presets = McaPresets()
      pvs = self.pvs['presets']
      for pv in pvs.keys():
         pvs[pv].array_get()
      pvs[pv].pend_io()
      presets.real_time       = pvs['prtm'].getValue()
      presets.live_time       = pvs['pltm'].getValue()
      presets.total_counts    = pvs['pct'].getValue()
      presets.start_channel   = pvs['pctl'].getValue()
      presets.end_channel     = pvs['pcth'].getValue()
      presets.dwell           = pvs['dwel'].getValue()
      presets.channel_advance = pvs['chas'].getValue()
      presets.prescale        = pvs['pscl'].getValue()
      Mca.set_presets(self, presets)
      return presets

   #######################################################################
   def set_presets(self, presets):
      Mca.set_presets(self, presets)
      pvs = self.pvs['presets']
      pvs['prtm'].array_put(presets.real_time)
      pvs['pltm'].array_put(presets.live_time)
      pvs['pct'].array_put(presets.total_counts)
      pvs['pctl'].array_put(presets.start_channel)
      pvs['pcth'].array_put(presets.end_channel)
      pvs['dwel'].array_put(presets.dwell)
      pvs['chas'].array_put(presets.channel_advance)
      pvs['pscl'].array_put(presets.prescale)
      pvs['pscl'].pend_io()

   #######################################################################
   def new_elapsed(self):
      # return self.pvs['elapsed']['ertm'].checkMonitor()
      return 1  # Force for now

   #######################################################################
   def get_elapsed(self):
      elapsed = McaElapsed()
      pvs = self.pvs['elapsed']
      for pv in pvs.keys():
         pvs[pv].array_get()
      pvs[pv].pend_io()
      elapsed.real_time    = pvs['ertm'].getValue()
      elapsed.live_time    = pvs['eltm'].getValue()
      elapsed.total_counts = pvs['act'].getValue()
      elapsed.read_time    = pvs['rtim'].getValue()
      elapsed.start_time   = string.strip(pvs['stim'].getValue())
      Mca.set_elapsed(self, elapsed)
      return elapsed

   #######################################################################
   def set_elapsed(self, elapsed):
      Mca.set_elapsed(self, elapsed)

   #######################################################################
   def get_sequence(self):
      pvs = self.pvs['sequence']
      for pv in pvs.keys():
         pvs[pv].array_get()
      pvs[pv].pend_io()
      sequence=pvs['seq'].getValue()
      return sequence

   #######################################################################
   def set_sequence(self, sequence):
      pvs = self.pvs['sequence']
      pvs['seq'].array_put(sequence)
      pvs['seq'].pend_io()
         
   #######################################################################
   def get_rois(self):
      for i in range(self.max_rois):
         pvs = self.roi_def_pvs[i]
         for pv in pvs.keys():
            pvs[pv].array_get()
      pvs[pv].pend_io()
      rois = []
      for i in range(self.max_rois):
         roi = McaROI()
         pvs = self.roi_def_pvs[i]
         r = 'R'+str(i)
         roi.left      = pvs[r+'lo'].getValue()
         roi.right     = pvs[r+'hi'].getValue()
         roi.label     = pvs[r+'nm'].getValue()
         roi.bgd_width = pvs[r+'bg'].getValue()
         roi.use = 1
         if (roi.left > 0) and (roi.right > 0): rois.append(roi)
      Mca.set_rois(self, rois)
      return rois

   #######################################################################
   def set_rois(self, rois, energy=0):
      Mca.set_rois(self, rois, energy=energy)
      nrois = len(self.rois)
      for i in range(nrois):
         roi = rois[i]
         pvs = self.roi_def_pvs[i]
         n = 'R'+str(i)
         pvs[n+'lo'].array_put(roi.left)
         pvs[n+'hi'].array_put(roi.right)
         pvs[n+'nm'].array_put(roi.label)
         pvs[n+'bg'].array_put(roi.bgd_width)
      for i in range(nrois, self.max_rois):
         n = 'R'+str(i)
         pvs = self.roi_def_pvs[i]
         pvs[n+'lo'].array_put(-1)
         pvs[n+'hi'].array_put(-1)
         pvs[n+'nm'].array_put(" ")
         pvs[n+'bg'].array_put(0)
      pvs[n+'bg'].pend_io()

   #######################################################################
   def get_roi_counts(self):
      nrois = len(self.rois)
      for roi in range(nrois):
         for pv in self.roi_data_pvs[roi].keys():
            pv.array_get()
      pvs[pv].pend_io()
      total = []
      net = []
      for i in range(nrois):
         pvs = self.roi_data_pvs[i]
         total.append(pvs['n'].getValue())
         net.append(pvs['nn'].getValue())
      return total, net

   #######################################################################
   def add_roi(self, roi, energy=0):
      Mca.add_roi(self, roi, energy=energy)
      self.set_rois(self.rois)

   #######################################################################
   def delete_roi(self, index):
      Mca.delete_roi(self, index)
      self.set_rois(self.rois)


   #######################################################################
   def get_environment(self):
      if (len(self.env_pvs) > 0):
         for pv in self.env_pvs:
            pv.array_get()
         pv.pend_io
         for i in range(len(self.environment)):
            self.environment[i].name = self.env_pvs[i].name()
            self.environment[i].value = self.env_pvs[i].getValue()
      return Mca.get_environment(self)

   #######################################################################
   def new_data(self):
      # return self.pvs['data']['val'].checkMonitor()
      return 1  # Force for now

   #######################################################################
   def get_data(self):
      nuse = self.pvs['data']['nuse'].getw()
      nchans = max(nuse,1)
      data = self.pvs['data']['val'].getw(count=nchans)
      Mca.set_data(self, data)
      return Mca.get_data(self)

   #######################################################################
   def set_data(self, data):
      nmax = self.pvs['data']['nmax'].getw()
      n_chans = max(len(data), nmax)
      Mca.set_data(self, data[0:n_chans])
      self.pvs['data']['nuse'].array_put(n_chans)
      self.pvs['data']['val'].putw(data[0:nchans])

   #######################################################################
   def new_acquire_status(self):
      # return self.pvs['acquire']['acqg'].checkMonitor()
      return 1  # Force for now

   #######################################################################
   def get_acquire_status(self, update=0):
      """
      busy, new = m.get_acquire_staus([update=1])
      KEYWORD PARAMETERS:
         UPDATE:
            Set this keyword to force the routine to process the record.
            By default update=0 and this routine does NOT process the record.
            The acquire status returned will be the status when the record
            was last processed.
      """
      if (update != 0): 
         self.pvs['acquire']['proc'].putw(1)
      busy = self.pvs['acquire']['acqg'].getw()
      return busy

   #######################################################################
   def wait(self, delay=.1, start=0, stop=1):
      """
      PURPOSE:
         This procedures waits for acquisition of the MCA to complete.
      KEYWORD INPUTS:
         delay:  The time between polling.  Default=0.1 seconds
         start:
            Set this flag to wait for acquisition to start.
         stop:
            Set this flag to wait for acquisition to stop.  This is the default.

         If both the "start" and "stop" keywords are given then the routine 
         will wait first for acquisition to start and then for acquistion to 
         stop.  If only start=1 is given then it will not wait for acquisition
         to stop.
      """
      if (start == 0) and (stop == 0): stop=1
      if (start != 0):
         while (1):
            busy = self.get_acquire_status(update=1)
            if (busy != 0): break
            time.sleep(delay)

      if (stop != 0):
         while (1):
            busy = self.get_acquire_status(update=1)
            if (busy == 0): break
            time.sleep(delay)

   #######################################################################
   def erase(self):
      self.pvs['acquire']['eras'].putw(1)

   #######################################################################
   def start(self, erase=0):
      if (erase == 0):
         self.pvs['acquire']['strt'].putw(1)
      else:
         self.pvs['acquire']['erst'].putw(1)

   #######################################################################
   def stop(self):
      self.pvs['acquire']['stop'].putw(1)

   #######################################################################
   def write_file(self, file):
      Mca.write_file(self, file)
      # Reset the client wait flag in case it is set.  It may not exist.
      if (self.pvs['acquire']['client_wait'] != None):
         self.pvs['acquire']['client_wait'].putw(0)

   ############################################################################
   def spectra_scan(self, first_file, scan_record):
      """
      PURPOSE:
         This procedures collects Mca spectra and saves them to disk in
         conjunction with an EPICS scan record.
         epicsMca.spectra_scan(first_file, scan_record)
      INPUTS:
         first_file:  
            The name of the first spectrum file to save.  Subsequent files 
            will be named using the INCREMENT_FILENAME()function.  The 
            filename must end in a numeric extension for this to work.
         scan_record:
            The name of the EPICS scan record which is controlling the scan.
            This scan record must be configure to start epicsMca data collection
            by writing "1" into the ERST field if the EPICS MCA.
      PROCEDURE:
         1) Wait for scan.EXSC = 1, meaning scan has started
         2) Wait for ClientWait=1, meaning acquisition has started
         3) Wait for Acquiring=0, meaning acquisition has completed
         4) Write data to disk with epicsMca::write_file, increment file name
         5) Reset ClientWait to 0 so scan will continue
         6) If scan.EXSC is still 1 go to 2.
      """
      file = first_file

      # Enable waiting for client
      self.pvs['acquire']['enable_wait'].putw(1)

      # Create PV for scan record executing
      scanPV = epicsPV(scan_record + '.EXSC')
      # Wait for scan to start
      while (scanPV.getw() == 0):
         time.sleep(.1)

      while (1):
         # If scan is complete, exit
         if (scanPV.getw() == 0): return

         # Wait for acquisition to start
         self.wait(start=1, stop=0)

         # Wait for acquisition to complete
         self.wait(start=0, stop=1)
 
         # Write file.  This will reset the client wait flag.
         self.write_file(file)
         print 'Saved file: ', file
         file = Xrf.increment_filename(file)
