import copy
import math
from Tkinter import *
import tkFileDialog
import tkMessageBox
import tkSimpleDialog
import Pmw
import Mca
import Xrf
import myTkTop

############################################################
class mcaPeakFit:
   """
   mcaPeakFit(mca, fit=None, command=None)
      mca:  Mca.Mca object to be fitted
      fit:  Mca.Fit object with fit parameters.  Optional.
      command:  callback command.  callback will be called as:
                command(background_mca=background_mca, fit_mca=fit_mca,
                cursor=cursor, fit=fit, get_cursor=1)
   """
   ############################################################
   def __init__(self, mca, fit=None, command=None):
      class widgets:
         pass
      self.mca = mca
      self.callback_command = command
      self.widgets = widgets()
      self.background_mca = copy.copy(mca)
      self.fit_mca = copy.copy(mca)
      data = self.background_mca.get_data() * 0
      self.background_mca.set_data(data)
      self.fit_mca.set_data(data)
      self.index=0
      if (fit == None):
         self.fit = Mca.McaFit(mca)
      else:
         self.fit = fit
      if (len(self.fit.peaks) == 0): self.fit.peaks=[Mca.McaPeak()]
      xsize=10
      top = myTkTop.myTkTop()
      Pmw.initialise(top)
      top.title('Peak Fit')
      self.widgets.top = top
      frame = Frame(top, borderwidth=1, relief='raised')
      frame.pack(fill=X)
      mb = Pmw.MenuBar(frame)
      mb.pack(fill=X)
      mb.addmenu('File', '', side='left')
      self.widgets.file = mb.component('File-menu')
      mb.addmenuitem('File', 'command', 
                      label='Read peaks...', 
                      command=self.read_peak_file)
      mb.addmenuitem('File', 'command', 
                      label='Write peaks...',
                      command=self.write_peak_file)
      mb.addmenuitem('File', 'command', 
                      label='Results file...', command=self.set_results_file)
      mb.addmenuitem('File', 'command', 
                      label='Spreadsheet file...', 
                      command=self.set_spreadsheet_file)
      mb.addmenuitem('File', 'command', 'Exit', label='Exit',
                      command=self.menu_exit)
      t = Pmw.Group(top, tag_text='Background Parameters'); t.pack(fill=X)
      bcol = t.interior()
      row = Frame(bcol); row.pack(side=TOP)
      background = self.fit.background
      self.widgets.exponent = t = Pmw.OptionMenu(row, labelpos=N,
                                    label_text='Exponent',
                                    items=('2','4','6'),
                                    initialitem = str(background.exponent))
      t.pack(side=LEFT)
      self.widgets.top_width = t = Pmw.EntryField(row,
                                    value=background.top_width,
                                    entry_width=8, entry_justify=CENTER,
                                    labelpos=N, label_text='Top width',
                                    validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.bottom_width = t = Pmw.EntryField(row,
                                       value=background.bottom_width,
                                       entry_width=8, entry_justify=CENTER,
                                       labelpos=N, label_text='Bottom width',
                                       validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.tangent = t = Pmw.OptionMenu(row, labelpos=N,
                                        label_text='Tangent?',
                                        items=('No', 'Yes'),
                                        menubutton_width=3,
                                        initialitem = background.tangent)
      t.pack(side=LEFT)
      self.widgets.compress = t = Pmw.OptionMenu(row, labelpos=N,
                                        label_text='Compression',
                                        items=('1', '2', '4', '8', '16'),
                                        menubutton_width=2,
                                        initialitem = str(background.compress))
      t.pack(side=LEFT)
      row = Frame(bcol); row.pack(side=TOP)
      self.widgets.fit_background = t = Button(row, text='Fit background',
                                               command=self.fit_background)
      t.pack(side=LEFT)
      self.widgets.plot_background = t = Button(row, text='Re-plot background',
                                                command=self.plot_background)
      t.pack(side=LEFT)

      t = Pmw.Group(top, tag_text='Peak Fit Parameters'); t.pack(fill=X)
      fcol = t.interior()
      t = Pmw.Group(fcol, tag_text='Initial energy calibration'); 
      t.pack(side=TOP)
      row = t.interior()
      self.widgets.energy_cal_offset = t = Pmw.EntryField(row, value=0,
                            entry_width=10, entry_justify=CENTER,
                            labelpos=W, label_text='Offset:',
                            validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.energy_cal_slope = t = Pmw.EntryField(row, value=0,
                            entry_width=10, entry_justify=CENTER,
                            labelpos=W, label_text='Slope:',
                            validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.energy_cal_flag = t = Pmw.OptionMenu(row, labelpos=W,
                                        label_text='Flag:',
                                        items=('Fix', 'Optimize'),
                                        menubutton_width=8,
                                        initialitem = 1)
      t.pack(side=LEFT)
      t = Pmw.Group(fcol, tag_text='Initial FWHM calibration');
      t.pack(side=TOP)
      row = t.interior()
      self.widgets.fwhm_cal_offset = t = Pmw.EntryField(row, value=0,
                            entry_width=10, entry_justify=CENTER,
                            labelpos=W, label_text='Offset:',
                            validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.fwhm_cal_slope = t = Pmw.EntryField(row, value=0,
                            entry_width=10, entry_justify=CENTER,
                            labelpos=W, label_text='Slope:',
                            validate={'validator':'real'})
      t.pack(side=LEFT)
      self.widgets.fwhm_cal_flag = t = Pmw.OptionMenu(row, labelpos=W,
                                        label_text='Flag:',
                                        items=('Fix', 'Optimize'),
                                        menubutton_width=8,
                                        initialitem = 1)
      t.pack(side=LEFT)

      width=10
      t = Pmw.Group(fcol, tag_text='Peak parameters'); t.pack(fill=X)
      pcol = t.interior()
      row = Frame(pcol); row.pack()
      self.widgets.label = t = Pmw.EntryField(row, value=' ',
                            entry_width=width, entry_justify=CENTER,
                            labelpos=N, label_text='Label',
                            command=self.peak_label)
      t.pack(side=LEFT)
      self.widgets.energy = t = Pmw.EntryField(row, value=0.,
                            entry_width=width, entry_justify=CENTER,
                            labelpos=N, label_text='Energy',
                            validate={'validator':'real'},
                            command=self.peak_params)
      t.pack(side=LEFT)

      self.widgets.energy_flag = t = Pmw.OptionMenu(row, labelpos=N,
                                        label_text='Energy flag',
                                        items=('Fix', 'Optimize'),
                                        initialitem = 1,
                                        menubutton_width=8,
                                        command=self.peak_params)
      t.pack(side=LEFT)
      self.widgets.fwhm = t = Pmw.EntryField(row, value=0.,
                            entry_width=width, entry_justify=CENTER,
                            labelpos=N, label_text='FWHM',
                            validate={'validator':'real'},
                            command=self.peak_params)
      t.pack(side=LEFT)
      self.widgets.fwhm_flag = t = Pmw.OptionMenu(row, labelpos=N,
                                        label_text='FWHM flag',
                                        items=('Fix', 'Optimize'),
                                        initialitem = 1,
                                        menubutton_width=8,
                                        command=self.peak_params)
      t.pack(side=LEFT)
      self.widgets.ampl_factor = t = Pmw.EntryField(row, value=0.,
                            entry_width=width, entry_justify=CENTER,
                            labelpos=N, label_text='Ampl. ratio',
                            validate={'validator':'real'},
                            command=self.peak_params)
      t.pack(side=LEFT)
      row = Frame(pcol); row.pack(side=TOP, anchor=W)
      col = Frame(row); col.pack(side=LEFT)
      width=7
      self.widgets.insert = t = Button(col, text='Insert', width=width,
                           command=lambda s=self: s.insert_or_append(insert=1)); 
      t.pack()
      self.widgets.append = t = Button(col, text='Append', width=width,
                           command=lambda s=self: s.insert_or_append(insert=0)); 
      t.pack()
      self.widgets.delete = t = Button(col, text='Delete', width=width,
                                       command=self.delete_peak); 
      t.pack()
      self.widgets.clear_peaks = t = Button(col, text='Clear', width=width,
                                            command=self.clear_peaks) 
      t.pack()
      self.widgets.sort = t = Button(col, text='Sort', width=width,
                                     command=self.sort_peaks); 
      t.pack()
      self.widgets.mark_peaks = t = Button(col, text='Mark all', width=width,
                                           command=self.mark_peaks) 
      t.pack()

      self.widgets.peak_list = t = Pmw.ScrolledListBox(row,
                                            listbox_font=('Courier','8'), 
                                            listbox_width=65, listbox_height=10,
                                            vscrollmode='static',
                                            hscrollmode='none',
                                            selectioncommand=self.new_index)
      t.pack()

      width=40
      self.widgets.result_file_name = t = Pmw.EntryField(fcol, 
                            value=self.fit.results_file,
                            entry_width=width, entry_justify=CENTER,
                            labelpos=W, label_text='Fit results file:')
      t.pack(anchor=W)
      self.widgets.spreadsheet_file_name = t = Pmw.EntryField(fcol, 
                            value=self.fit.spreadsheet_file,
                            entry_width=width, entry_justify=CENTER,
                            labelpos=W, label_text='Fit spreadsheet file:')
      t.pack(anchor=W)
      self.widgets.append_mode = t = Pmw.OptionMenu(fcol, labelpos=W,
            label_text='Overwrite or append results and spreadsheet files:',
                                        items=('Overwrite', 'Append'),
                                        menubutton_width=9,
                                        initialitem = 1)
      t.pack(anchor=W)
      row = Frame(fcol); row.pack(side=TOP)
      self.widgets.fit_peaks = t = Button(row, text='Fit peaks') 
      t.pack(side=LEFT)
      self.widgets.plot_fit = t = Button(row, text='Re-plot fit')
      t.pack(side=LEFT)
      self.update_peaks()

   ############################################################
   def new_index(self):
      index=self.widgets.peak_list.curselection()
      self.index=int(index[0])
      self.update_peak_line()
      
   ############################################################
   def update_peaks(self):
      text = []
      peaks = self.fit.peaks
      for peak in peaks:
         s =  ('%15s'   % peak.label) + ', ' + \
              ('%10.4f' % peak.initial_energy) + ', ' + \
              ('%2d'    % peak.energy_flag) + ', ' + \
              ('%10.4f' % peak.initial_fwhm) + ', ' + \
              ('%2d'    % peak.fwhm_flag) + ', ' + \
              ('%10.4f' % peak.ampl_factor)
         text.append(s)
      self.widgets.peak_list.setlist(text)
      self.widgets.peak_list.select_set(self.index)
      # See if this works
      self.widgets.peak_list.configure(selectioncommand=self.new_index)
      if (len(peaks) > 0):
         self.update_peak_line()
      self.mark_peaks()

   ############################################################
   def update_peak_line(self):
      peak = self.fit.peaks[self.index]
      self.widgets.label.setentry(peak.label)
      self.widgets.energy.setentry(peak.initial_energy)
      self.widgets.energy_flag.setitems(
                               ['Fix', 'Optimize'], index=peak.energy_flag)
      self.widgets.fwhm.setentry(peak.initial_fwhm)
      self.widgets.fwhm_flag.setitems(
                               ['Fix', 'Optimize'], index=peak.fwhm_flag)
      self.widgets.ampl_factor.setentry(peak.ampl_factor)
      if (self.callback_command != None):
         chan = self.mca.energy_to_channel(peak.initial_energy)
         self.callback_command(cursor=chan)

   ############################################################
   def fit_background(self):
      background = self.fit.background
      background.exponent = int(self.widgets.exponent.getcurselection())
      background.compress = int(self.widgets.compress.getcurselection())
      background.tangent = int(self.widgets.tangent.index(Pmw.SELECT))
      background.top_width = float(self.widgets.top_width.get())
      background.bottom_width = float(self.widgets.bottom_width.get())
      self.widgets.top.configure(cursor='watch')
      self.widgets.top.update()
      #self.widgets.peak_list.update_idletasks()
      self.background_mca = Mca.fit_background(self.mca,
                                 exponent=background.exponent,
                                 compress=background.compress,
                                 tangent=background.tangent,
                                 top_width=background.top_width,
                                 bottom_width=background.bottom_width)
      if (self.callback_command != None):
         self.callback_command(background_mca=self.background_mca)
      self.widgets.top.configure(cursor='')

   ############################################################
   def plot_background(self):
      if (self.callback_command != None):
         self.callback_command(background_mca=self.background_mca)

   ############################################################
   def read_peak_file(self):
      file = tkFileDialog.askopenfilename(parent=self.widgets.top,
                                title='Peaks file',
                                filetypes=[('Peak files','*.pks'),
                                           ('All files','*')])
      if (file == ''): return
      r = Mca.read_peaks(file)
      self.fit.peaks = r['peaks']
      self.fit.background = r['background']
      self.index = 0
      self.update_peaks()

   ############################################################
   def write_peak_file(self):
      file = tkFileDialog.asksaveasfilename(parent=self.widgets.top, 
                                title='Output file',
                                filetypes=[('Peak files','*.pks'),
                                           ('All files','*')])
      if (file == ''): return
      Mca.write_peaks(file, peaks, self.fit.background)

   ############################################################
   def set_results_file(self):
      file = tkFileDialog.asksaveasfilename(parent=self.widgets.top, 
                                title='Results file',
                                filetypes=[('All files','*')])
      if (file == ''): return
      self.file.fit_results = file
      self.widgets.results_file_name(setentry=file)

   ############################################################
   def set_spreadsheet_file(self):
      file = tkFileDialog.asksaveasfilename(parent=self.widgets.top, 
                                title='Spreadsheet file',
                                filetypes=[('All files','*')])
      if (file == ''): return
      self.file.fit_spreadsheet = file
      self.widgets.spreadsheet_file_name(setentry=file)

   ############################################################
   def menu_exit(self):
      self.widgets.top.destroy()

   ############################################################
   def mark_peaks(self):
      data = self.mca.get_data()
      temp = data*0
      for peak in self.fit.peaks:
        chan = self.mca.energy_to_channel(peak.initial_energy, clip=1)
        temp[chan] = data[chan]
      self.background_mca.set_data(temp)
      self.background_mca.name = 'Peak positions'
      if (self.callback_command != None):
         self.callback_command(background_mca=self.background_mca)

   ############################################################
   def peak_label(self):
      peaks=self.fit.peaks
      label = self.widgets.label.get()
      label = label.strip()
      peaks[self.index].label = label
      energy = Xrf.lookup_xrf_line(label)
      if (energy == None): energy = Xrf.lookup_gamma_line(label)
      if (energy != None):
         peaks[self.index].initial_energy=energy
         # Set the energy flag to 0, since energy is known
         peaks[self.index].energy_flag=0
         # Set FWHM flag to 0, since peak width will be defined by
         # detector resolution
         peaks[self.index].fwhm_flag=0
      self.update_peaks()

   ############################################################
   def peak_params(self, value=None):
      peaks = self.fit.peaks
      peaks[self.index].initial_energy = float(self.widgets.energy.get())
      peaks[self.index].energy_flag = self.widgets.energy_flag.index(Pmw.SELECT)
      peaks[self.index].initial_fwhm = float(self.widgets.fwhm.get())
      peaks[self.index].fwhm_flag = self.widgets.fwhm_flag.index(Pmw.SELECT)
      peaks[self.index].ampl_factor = float(self.widgets.ampl_factor.get())
      self.update_peaks()

   ############################################################
   def insert_or_append(self, insert):
      new_peak = Mca.McaPeak()
      if (self.callback_command != None):
         cursor = self.callback_command(get_cursor=1)
         energy = self.mca.channel_to_energy(cursor)
      else:
         energy=0.
      new_peak.initial_energy = energy
      # Make a reasonble estimate of initial FWHM
      new_peak.initial_fwhm = 0.2 + .03*math.sqrt(abs(energy))
      new_peak.energy_flag=1
      new_peak.fwhm_flag=1
      if (insert):
         self.fit.peaks.insert(self.index, new_peak)
      else:
         self.fit.peaks.insert(self.index+1, new_peak)
         self.index = self.index + 1
      self.update_peaks()

   ############################################################
   def delete_peak(self):
      self.fit.peaks.pop(self.index)
      if (len(self.fit.peaks) == 0): self.clear_peaks()
      self.index = max(0, self.index-1)
      self.update_peaks()

   ############################################################
   def clear_peaks(self):
      self.fit.peaks=[Mca.McaPeak()]
      self.index=0
      self.update_peaks()

   ############################################################
   def sort_peaks(self):
      self.fit.peaks.sort(self.sort_function)
      self.update_peaks()

   ############################################################
   def sort_function(self, p1, p2):
      if (p1.initial_energy < p2.initial_energy): return -1
      if (p1.initial_energy == p2.initial_energy): return 0
      return 1

   ############################################################
   def plot_fit(self):
      if (self.callback_command != None):
         self.callback_command(fit_mca=self.fit_mca)

   ############################################################
   def fit_peaks(self):
      append = self.widgets.append_mode.getcurselection()
      self.widgets.top.configure(cursor='watch')
      self.widgets.top.update()
      self.fit_mca = self.mca.fit_peaks(self.fit, background=self.background_mca, 
                                  append=append)
      self.widgets.top.configure(cursor='')
      self.fit_mca.name = 'Peak fit'
      t = Pmw.TextDialog(title='mcaPeakFit Results',
                     scrolledtext_width=85, scrolledtext_font=('Courier','8'))
      t._scrolledtext.importfile(self.fit.results)
