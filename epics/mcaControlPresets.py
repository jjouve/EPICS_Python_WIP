from Tkinter import *
import Pmw
 
class mcaControlPresets:
   def __init__(self, mca):
      class widgets:
         pass
      self.mca = mca
      self.widgets = widgets()
      t = Pmw.Dialog(command=self.menu_ok_cancel,
                     buttons=('OK', 'Apply', 'Cancel'),
                     title='mcaControlPresets')
      self.widgets.top = top = t.component('dialogchildsite')

      self.presets = self.mca.get_presets()
      self.widgets.real_time = t = Pmw.EntryField(row,
                               value=str(self.presets.real_time), labelpos=N,
                               label_text='Real time:',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.live_time = t = Pmw.EntryField(row,
                               value=str(self.presets.live_time), labelpos=N,
                               label_text='Live time:',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.total_counts = t = Pmw.EntryField(row,
                               value=str(self.presets.total_counts), labelpos=N,
                               label_text='Total counts:',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.start_channel = t = Pmw.EntryField(row,
                               value=str(self.presets.start_channel), labelpos=N,
                               label_text='Start channel:',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'numeric'})
      t.pack(side=LEFT)
      self.widgets.end_channel = t = Pmw.EntryField(row,
                               value=str(self.presets.end_channel), labelpos=N,
                               label_text='End channel:',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'numeric'})
      t.pack(side=LEFT)

   def menu_ok_cancel(self, value):
      if (value == 'OK') or (value == 'Apply'):
         # Copy presets to Mca object
         self.presets.real_time = self.widgets.real_time.get()
         self.presets.live_time = self.widgets.live_time.get()
         self.presets.total_counts = self.widgets.total_counts.get()
         self.presets.start_chan = self.widgets.start_chan.get()
         self.presets.end_chan = self.widgets.end_chan.get()
         self.mca.set_presets(self.presets)
      if (value != 'Apply'): Toplevel.destroy(self.widgets.top)
      
