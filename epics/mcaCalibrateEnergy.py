from Tkinter import *
import copy
import tkMessageBox
import Pmw
import Mca
import Numeric
import math
import Xrf
import CARSMath
import BltPlot

############################################################
class mcaCalibrateEnergy_widgets:
   def __init__(self, nrois):
      self.use_flag             = range(nrois)
      self.centroid             = range(nrois)
      self.fwhm                 = range(nrois)
      self.energy               = range(nrois)
      self.energy_diff          = range(nrois)
      self.line                 = range(nrois)

class mcaCalibrateEnergy:
   def __init__(self, mca, command=None):
      self.input_mca = mca
      self.mca = copy.copy(mca)
      self.exit_command = command
      self.roi = self.mca.get_rois()
      self.nrois = len(self.roi)
      if (self.nrois < 2):
         tkMessageBox.showerror(title='mcaCalibrateEnergy Error', 
                message='Must have at least two ROIs to perform calibration')
         return
      self.calibration = self.mca.get_calibration()
      self.fwhm_chan = Numeric.zeros(self.nrois, Numeric.Float)
      self.widgets = mcaCalibrateEnergy_widgets(self.nrois)
      self.data = self.mca.get_data()

      # Compute the centroid and FWHM of each ROI
      for i in range(self.nrois):
         left = self.roi[i].left
         right = self.roi[i].right+1
         total_counts = self.data[left:right]
         n_sel        = right - left
         sel_chans    = left + Numeric.arange(n_sel)
         left_counts  = self.data[left]
         right_counts = self.data[right]
         bgd_counts   = (left_counts + Numeric.arange(float(n_sel))/(n_sel-1) *
                                     (right_counts - left_counts))
         net_counts   = total_counts - bgd_counts
         net          = Numeric.sum(net_counts)
 
         if ((net > 0.) and (n_sel >= 3)):
            amplitude, centroid, fwhm = CARSMath.fit_gaussian(sel_chans, net_counts)
            self.roi[i].centroid = centroid
            self.fwhm_chan[i] = fwhm
         else:
            self.roi[i].centroid = (left + right)/2.
            self.fwhm_chan[i] = right-left
         self.roi[i].fwhm = (self.mca.channel_to_energy(self.roi[i].centroid + 
                                          self.fwhm_chan[i]/2.) - 
                             self.mca.channel_to_energy(self.roi[i].centroid - 
                                          self.fwhm_chan[i]/2.))

      self.widgets.top = t = Pmw.Dialog(command=self.menu_ok_cancel,
                     buttons=('OK', 'Apply', 'Cancel'),
                     title='mcaCalibrateEnergy')
      top = t.component('dialogchildsite')
      box = Frame(top, borderwidth=1, relief=SOLID); box.pack(fill=X, pady=3)
      t = Label(box, text='ROI'); t.grid(row=0, column=0)
      t = Label(box, text='Use?'); t.grid(row=0, column=1)
      t = Label(box, text='Centroid'); t.grid(row=0, column=2)
      t = Label(box, text='FWHM'); t.grid(row=0, column=3)
      t = Label(box, text='Energy'); t.grid(row=0, column=4)
      t = Label(box, text='Fluor. line'); t.grid(row=0, column=5)
      t = Label(box, text='Energy diff.'); t.grid(row=0, column=6)
      text_width=10
      for i in range(self.nrois):
         row=i+1
         t = Label(box, text=str(i)); 
         t.grid(row=row, column=0)
         self.widgets.use_flag[i] = t = Pmw.OptionMenu(box,
                        items=('No','Yes'),
                        initialitem = self.roi[i].use,
                        command=lambda e, s=self, r=i: s.menu_use(e,r))
         t.grid(row=row, column=1)
         self.widgets.centroid[i] = t = Pmw.EntryField(box, 
                        value=('%.3f' % self.roi[i].centroid),
                        entry_width=text_width, entry_justify=CENTER, 
                        command=lambda s=self, r=i: s.menu_centroid(r))
         t.grid(row=row, column=2)
         self.widgets.fwhm[i] = t = Label(box, 
                            text=('%.3f' % self.roi[i].fwhm), width=text_width,
                            justify=CENTER, borderwidth=1, relief=SOLID)
         t.grid(row=row, column=3)
         # If the ROI energy is zero, then try to use the label to lookup an
         # XRF line energy
         if (self.roi[i].energy == 0.0):
            self.roi[i].energy = Xrf.lookup_xrf_line(self.roi[i].label)
            if (self.roi[i].energy == None):
               self.roi[i].energy = Xrf.lookup_gamma_line(self.roi[i].label)
            if (self.roi[i].energy == None): self.roi[i].energy=0.0
         self.widgets.energy[i] = t = Pmw.EntryField(box, 
                        value=('%.3f' % self.roi[i].energy),
                        entry_width=text_width, entry_justify=CENTER, 
                        command=lambda s=self, r=i: s.menu_energy(r))
         t.grid(row=row, column=4)
         self.widgets.line[i] = t = Pmw.EntryField(box, 
                        value=str(self.roi[i].label),
                        entry_width=text_width, entry_justify=CENTER, 
                        command=lambda s=self, r=i: s.menu_line(r))
         t.grid(row=row, column=5)

         self.widgets.energy_diff[i] = t = Label(box, 
                            text=('%.3f' % 0.0), width=text_width,
                            justify=CENTER, borderwidth=1, relief=SOLID)
         t.grid(row=row, column=6)

      row = Frame(top, borderwidth=1, relief=SOLID); row.pack(fill=X, pady=3)
      self.widgets.fit_type = t = Pmw.OptionMenu(row, labelpos=N,
                                        label_text='Calibration type:',
                                        items=('Linear','Quadratic'))
      t.pack(side=LEFT, anchor=S)
      self.widgets.do_fit = t = Button(row, text='Compute calibration', 
                                        command=self.menu_do_fit)
      t.pack(side=LEFT, anchor=S)
      self.widgets.plot_cal = t = Button(row, text='Plot calibration error',
                                        command=self.menu_plot_calibration)
      t.pack(side=LEFT, anchor=S)
      self.widgets.plot_fwhm = t = Button(row, text='Plot FWHM',
                                        command=self.menu_plot_fwhm)
      t.pack(side=LEFT, anchor=S)

      row = Frame(top, borderwidth=1, relief=SOLID); row.pack(fill=X, pady=3)
      text_width=10
      t = Label(row, text='Calibration coefficients'); t.pack()
      self.widgets.cal_units = t = Pmw.EntryField(row, 
                            label_text='Units:', labelpos=W,
                            value=self.calibration.units,
                            entry_width=text_width, entry_justify=CENTER)
      t.pack(side=LEFT)
      self.widgets.cal_offset = t = Pmw.EntryField(row, 
                            label_text='Offset:', labelpos=W,
                            value=self.calibration.offset,
                            entry_width=text_width, entry_justify=CENTER)
      t.pack(side=LEFT)
      self.widgets.cal_slope = t = Pmw.EntryField(row, 
                            label_text='Slope:', labelpos=W,
                            value=self.calibration.slope,
                            entry_width=text_width, entry_justify=CENTER)
      t.pack(side=LEFT)
      self.widgets.cal_quad = t = Pmw.EntryField(row, 
                            label_text='Quadratic:', labelpos=W,
                            value=self.calibration.quad,
                            entry_width=text_width, entry_justify=CENTER)
      t.pack(side=LEFT)

   def menu_plot_calibration(self):
      energy = []
      energy_diff = []
      energy_use = []
      energy_diff_use = []
      for i in range(self.nrois):
         energy.append(self.roi[i].energy)
         energy_diff.append(self.roi[i].energy -
                            self.mca.channel_to_energy(self.roi[i].centroid))
         if (self.roi[i].use):
            energy_use.append(energy[i])
            energy_diff_use.append(energy_diff[i])
      p = BltPlot.BltPlot(energy, energy_diff, 
                          title='MCA Calibration', legend=1,
                          symbol='circle', linewidth=0,
                          xtitle='Energy', ytitle='Calibration error', 
                          label='All points')
      p.oplot(energy_use, energy_diff_use, 
              symbol="square", linewidth=1,
              label='Points used')

   def menu_plot_fwhm(self):
      energy = []
      fwhm = []
      for i in range(self.nrois):
         energy.append(self.roi[i].energy)
         fwhm.append(self.roi[i].fwhm)
      p = BltPlot.BltPlot(energy, fwhm, title='MCA FWHM',
                   symbol='circle', linewidth=1, 
                   xtitle='Energy', ytitle='FWHM')

   def menu_energy(self, roi):
      energy = float(self.widgets.energy[roi].get())
      self.roi[roi].energy = energy
      self.widgets.energy[roi].setentry('%.3f' % energy)

   def menu_centroid(self, roi):
      centroid = float(self.widgets.centroid[roi].get())
      self.roi[roi].centroid = centroid
      self.widgets.centroid[roi].setentry('%.3f' % centroid)

   def menu_use(self, value, roi):
      self.roi[roi].use = (value == 'Yes')

   def menu_line(self, roi):
       line = self.widgets.line[roi].get()
       energy = Xrf.lookup_xrf_line(line)
       if (energy == None):
          energy = Xrf.lookup_gamma_line(line)
       if (energy != None): 
          self.roi[roi].energy = energy
          self.widgets.energy[roi].setentry('%.3f' % energy)

   def menu_do_fit(self):
      degree = self.widgets.fit_type.index(
                                self.widgets.fit_type.getcurselection()) + 1
      use = []
      for i in range(self.nrois):
         if (self.roi[i].use): use.append(i)
      nuse = len(use)
      if ((degree == 1) and (nuse < 2)):
         tkMessageBox.showerror(title='mcaCalibateEnergy Error', 
            message='Must have at least two valid points for linear calibration')
         return
      elif ((degree == 2) and (nuse < 3)):
         tkMessageBox.showerror(title='mcaCalibateEnergy Error', 
            message='Must have at least three valid points for quadratic calibration')
         return
      chan=Numeric.zeros(nuse, Numeric.Float)
      energy=Numeric.zeros(nuse, Numeric.Float)
      weights=Numeric.ones(nuse, Numeric.Float)
      for i in range(nuse):
         chan[i] = self.roi[use[i]].centroid
         energy[i] = self.roi[use[i]].energy
      coeffs = CARSMath.polyfitw(chan, energy, weights, degree)
      self.calibration.offset = coeffs[0]
      self.widgets.cal_offset.setentry(str(self.calibration.offset))
      self.calibration.slope = coeffs[1]
      self.widgets.cal_slope.setentry(str(self.calibration.slope))
      if (degree == 2):
         self.calibration.quad = coeffs[2]
      else:
         self.calibration.quad = 0.0
      self.widgets.cal_quad.setentry(str(self.calibration.quad))
      self.mca.set_calibration(self.calibration)
      for i in range(self.nrois):
         energy_diff = (self.roi[i].energy -
                        self.mca.channel_to_energy(self.roi[i].centroid))
         self.widgets.energy_diff[i].configure(text=('%.4f' % energy_diff))
         # Recompute FWHM
         self.roi[i].fwhm = (self.mca.channel_to_energy(self.roi[i].centroid + 
                                   self.fwhm_chan[i]/2.) - 
                           self.mca.channel_to_energy(self.roi[i].centroid -
                                   self.fwhm_chan[i]/2.))
         self.widgets.fwhm[i].configure(text=('%.3f' % self.roi[i].fwhm))

   def menu_ok_cancel(self, button):
      if (button == 'OK') or (button == 'Apply'):
         # Copy calibration and rois to input mca object
         self.input_mca.set_calibration(self.calibration)
         self.input_mca.set_rois(self.roi)
      if (button == 'OK'):
         exit_status=1
      elif (button == 'Apply'):
         return
      else:
         exit_status = 0
      if (self.exit_command): self.exit_command(exit_status)
      self.widgets.top.destroy()
