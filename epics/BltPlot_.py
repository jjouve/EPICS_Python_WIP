"""
This module provides a wrapper around the Pmw.Blt.Graph widget.  It has both a
standalone plotting widget (BltPlot.BltPlot), GUI routines to configure the
axes, elements, markers, etc., and routines to save and restore settings.
"""
from Tkinter import *
import Tkinter
import tkColorChooser
import tkFileDialog
import Pmw
import os
import cPickle
import myTkTop

########################################################################
class BltPlot:
   
   ########################################################################
   def __init__(self, xdata=None, ydata=None, exit_callback=None, **kw):
      class widgets:
         pass
      self.exit_callback=exit_callback
      self.widgets = widgets()
      self.widgets.top = top = myTkTop.myTkTop()
      Wm.protocol(top, 'WM_DELETE_WINDOW', self.exit)
      self.settings_file = 'BltSettings.sav'
      frame = Frame(top, borderwidth=1, relief='raised')
      frame.pack(fill=X)
      self.widgets.mbar = mbar = Pmw.MenuBar(frame)
      mbar.pack(fill=X)

      # There is a bug (???) in Pmw.Blt, it won't create a new graph if
      # Tkinter.Tk() has been called since the last time a graph was created.
      # Work around the problem for now by reloading Pmw.Blt.
      #reload(Pmw.Blt)
      self.graph = t = Pmw.Blt.Graph(self.widgets.top)
      t.pack(expand=YES, fill=BOTH)

      mbar.addmenu('File', '', side='left')
      mbar.addmenuitem('File', 'command', label='Save as...',
                      command=self.menu_save_as)
      mbar.addmenuitem('File', 'command', label='Save...',
                      command=self.menu_save)
      mbar.addmenuitem('File', 'command', label='Restore...',
                      command=self.menu_restore)
      mbar.addmenuitem('File', 'command', label='Print...',
                      command=lambda g=self.graph: BltPrint(g))
      mbar.addmenuitem('File', 'command', 'Exit', label='Exit',
                      command=self.exit)
      mbar.addmenu('Configure', '', side='left')
      mbar.addmenuitem('Configure', 'command', label='Graph...',
                      command=lambda g=self.graph: BltConfigureGraph(g))
      mbar.addmenuitem('Configure', 'command', label='X axis...',
                      command=lambda g=self.graph: BltConfigureAxis(g,'x'))
      mbar.addmenuitem('Configure', 'command', label='X2 axis...',
                      command=lambda g=self.graph: BltConfigureAxis(g,'x2'))
      mbar.addmenuitem('Configure', 'command', label='Y axis...',
                      command=lambda g=self.graph: BltConfigureAxis(g,'y'))
      mbar.addmenuitem('Configure', 'command', label='Y2 axis...',
                      command=lambda g=self.graph: BltConfigureAxis(g,'y2'))
      mbar.addmenuitem('Configure', 'command', label='Grid...',
                      command=lambda g=self.graph: BltConfigureGrid(g))
      mbar.addmenuitem('Configure', 'command', label='Legend...',
                      command=lambda g=self.graph: BltConfigureLegend(g))
      mbar.addcascademenu('Configure', 'Element')

      apply(self.plot, (xdata, ydata), kw)

   ########################################################################
   def exit(self):
      if (self.exit_callback != None):
         self.exit_callback(self.graph)
      self.widgets.top.destroy()    

   ########################################################################
   def menu_save_as(self):
      file = tkFileDialog.asksaveasfilename(parent=self.widgets.top, 
                                title='Settings file',
                                filetypes=[('Save files','*.sav'),
                                           ('All files','*')])
      if (file == ''): return
      self.settings_file = file
      BltSaveSettings(self.graph, self.settings_file)

   ########################################################################
   def menu_save(self):
      BltSaveSettings(self.graph, self.settings_file)

   ########################################################################
   def menu_restore(self):
      file = tkFileDialog.askopenfilename(parent=self.widgets.top, 
                                title='Settings file',
                                filetypes=[('Save files','*.sav'),
                                           ('All files','*')])
      if (file == ''): return
      self.settings_file = file
      BltRestoreSettings(self.graph, self.settings_file)

   ########################################################################
   def plot(self, xdata, ydata=None, window_title='BltPlot', title=None,
            background='light grey', plotbackground='white',
            xmin="", xmax="", xtitle=None, xlog=0,
            xtickfont=('Helvetica','10'), xtitlefont=('Helvetica','11','bold'),
            ymin="", ymax="", ytitle=None, ylog=0,
            ytickfont=('Helvetica','10'), ytitlefont=('Helvetica','11','bold'),
            symbol="", linewidth=1, pixels=7, smooth="linear", color='black',
            label="line1", legend=0):
   
      self.widgets.top.title(window_title)
      g = self.graph
      elements = g.element_names()
      for element in elements:
         g.element_delete(element)
      self.widgets.mbar.deletemenu('Element') 
      self.widgets.mbar.addcascademenu('Configure', 'Element')
      # Double click event anywhere on widget
      self.widgets.top.bind('<Double-Button-1>', self.double_click)
      g.configure(title=title)
      g.configure(plotbackground=plotbackground)
      if (xdata == None): return
      xdata = tuple(xdata)
      if (ydata == None):
         ydata = xdata
         xdata = tuple(range(len(ydata)))
      else:
         ydata = tuple(ydata)
      g.line_create(label)
      g.element_configure(label, xdata=xdata, ydata=ydata,
                          color=color, symbol=symbol, linewidth=linewidth,
                          pixels=pixels, smooth=smooth)
      self.widgets.mbar.addmenuitem('Element', 'command', label=label, 
         command=lambda g=self.graph, e=label: BltConfigureElement(g, e))
      for event in ('<Enter>', '<Leave>', '<Double-Button-1>'):
         g.element_bind(label, event,
                       lambda e, s=self, t=label: s.element_mouse(e, t))
      g.legend_configure(hide=(not legend))
      for event in ('<Enter>', '<Leave>', 
                     '<ButtonPress>', '<ButtonRelease>'):
         g.legend_bind(label, event, self.legend_mouse)
      g.xaxis_configure(min=xmin, max=xmax, title=xtitle, logscale=xlog,
                        tickfont=xtickfont, titlefont=xtitlefont)
      g.yaxis_configure(min=ymin, max=ymax, title=ytitle, logscale=ylog,
                        tickfont=ytickfont, titlefont=ytitlefont)

   ########################################################################
   def oplot(self, xdata=None, ydata=None, symbol="", linewidth=1, pixels=7, 
             smooth="linear", color='black', label="line2"):
      if (xdata == None): return
      xdata = tuple(xdata)
      if (ydata == None):
         ydata = xdata
         xdata = tuple(range(len(ydata)))
      else:
         ydata = tuple(ydata)
      g = self.graph
      g.line_create(label, color=color)
      g.element_configure(label, xdata=xdata, ydata=ydata,
                          color=color, symbol=symbol, linewidth=linewidth,
                          pixels=pixels, smooth=smooth)
      self.widgets.mbar.addmenuitem('Element', 'command', label=label, 
         command=lambda g=self.graph, e=label: BltConfigureElement(g, e))
      for event in ('<Enter>', '<Leave>', '<Double-Button-1>'):
         g.element_bind(label, event,
                       lambda e, s=self, t=label: s.element_mouse(e, t))
      for event in ('<Enter>', '<Leave>', 
                     '<ButtonPress>', '<ButtonRelease>'):
         g.legend_bind(label, event, self.legend_mouse)

   ########################################################################
   def double_click(self, event):
      x = event.x; y=event.y
      g = self.graph
      if g.inside(x, y):
         BltConfigureGraph(self.graph)

      else:
         # Figure out what margin we are in
         s = self.graph.winfo_geometry()
         s=s.replace('x',' '); s=s.replace('+', ' '); w = s.split()
         wx = int(w[0]); wy = int(w[1])
         if (x <= g.extents('leftmargin')):
            BltConfigureAxis(self.graph, 'y')
         elif (x > (wx - g.extents('rightmargin'))):
            BltConfigureAxis(self.graph, 'y2')
         elif (y > (wy - g.extents('bottommargin'))):
            BltConfigureAxis(self.graph, 'x')
         else:
            BltConfigureAxis(self.graph, 'x2')

   ########################################################################
   def legend_mouse(self, event):
      g = self.graph
      tags = g.element_names()
      if (event.type == '2'):    # KeyPress event
         pos = g.legend_cget('position')
         if (pos[0] != '@'): return
         w = pos[1:].split(','); x = int(w[0]); y=int(w[1])
         if (event.keysym == 'Left'): x=x-1
         elif (event.keysym == 'Down'): y=y+1
         elif (event.keysym == 'Right'): x=x+1
         elif (event.keysym == 'Up'): y=y-1
         g.legend_configure(position='@'+str(x)+','+str(y))

      elif (event.type == '4'):
         # Button press event - start dragging if button 1
          if (event.num == 1):
             for tag in tags:  g.legend_bind(tag, '<Motion>', self.legend_mouse)

      elif (event.type == '5'):
         # Mouse button release event - stop dragging if button 1, menu if 3
         if (event.num == 1):
            for tag in tags:  g.legend_unbind(tag, '<Motion>')
         elif (event.num == 3): BltConfigureLegend(g)

      elif (event.type == '6'):  # Mouse drag event
         g.legend_configure(position='@'+str(event.x)+','+str(event.y))

      elif (event.type == '7'):  # Enter event - highlight and enable arrow keys
         for tag in tags: g.legend_activate(tag)
         self.widgets.top.bind('<KeyPress>', self.legend_mouse)
 
      elif (event.type == '8'):  # Leave event - unhighlight and disable arrow keys
         for tag in tags: g.legend_deactivate(tag)
         # There seems to be a bug that deactivate does not work after
         # drags.  Re-setting the background color fixes it
         g.legend_configure(background=g.legend_cget('background'))
         self.widgets.top.unbind('<KeyPress>')
 
   ########################################################################
   def element_mouse(self, event, element):
      g = self.graph
      if (event.type == '4'): # Double click event
         # NEED TO FIGURE OUT HOW TO "EAT" THIS EVENT SO IT DOES NOT GET
         # PASSED ON TO 'DOUBLE_CLICK" EVENT HANDLER
         BltConfigureElement(g, element)

      elif (event.type == '7'):  # Enter event - highlight
         #s = g.element_closest(event.x, event.y, element)
         #if (s == None): index=None
         #else: index=s['index']
         #g.element_activate(element, index)
         g.element_activate(element)
 
      elif (event.type == '8'):  # Leave event - unhighlight
         g.element_deactivate(element)
 
  
########################################################################
class BltPrint:

   ########################################################################
   def __init__(self, graph, xsize=0, ysize=0, orientation='Portrait',
                file = 'Blt.ps',
                print_command = os.getenv('BLT_PRINT_COMMAND')):
      self.graph=graph
      self.xsize=xsize
      self.ysize=ysize
      self.orientation = orientation
      self.file=file
      if (print_command != None):
         self.print_command = print_command
      else:
         self.print_command = 'print '
      class BltPrint_widgets:
         pass
      self.widgets = BltPrint_widgets()
      self.widgets.top = t = Pmw.Dialog(command=self.menu_print_save,
                     buttons=('Print', 'Save','Quit'),
                     title='BltPlotPrint')
      top = t.component('dialogchildsite')
      self.widgets.xsize = t = Pmw.EntryField(top,
                               value=str(self.xsize), labelpos=W,
                               label_text='X size (in):',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'real'})
      t.pack(side=TOP)
      self.widgets.ysize = t = Pmw.EntryField(top,
                               value=str(self.ysize), labelpos=W,
                               label_text='Y size (in):',
                               entry_width=8, entry_justify=CENTER,
                               validate={'validator':'real'})
      t.pack(side=TOP)
      self.widgets.orientation = t = Pmw.OptionMenu(top, labelpos=W,
                           label_text='Orientation:',
                           items=('Portrait', 'Landscape'),
                        initialitem = self.orientation)
      t.pack(side=TOP)
      self.widgets.file = t = Pmw.EntryField(top,
                               value=self.file, labelpos=W,
                               entry_width=30, label_text='Filename:')
      t.pack(side=TOP, expand=YES, fill=X)
      self.widgets.print_command = t = Pmw.EntryField(top,
                               value=self.print_command, labelpos=W,
                               label_text='Print command:',
                               entry_width=20)
      t.pack(side=TOP, expand=YES, fill=X)

   ########################################################################
   def menu_print_save(self, button):
      if (button == 'Print') or (button == 'Save'):
         self.xsize = self.widgets.xsize.get()
         self.ysize = self.widgets.ysize.get()
         self.orientation = self.widgets.orientation.getcurselection()
         self.file = self.widgets.file.get()
         self.print_command = self.widgets.print_command.get()
         self.graph.postscript_output(self.file,
                                    height=self.ysize, width=self.xsize,
                                    landscape=(self.orientation=='Landscape'))
      if (button == 'Print'):
         os.system(self.print_command + ' ' + self.file)
      if (button == 'Quit') or (button == None): 
         self.widgets.top.destroy()

########################################################################
class BltConfigureAxis:

   ########################################################################
   def __init__(self, graph, axis, command=None):
      self.graph=graph
      self.axis=axis
      self.return_command=command
      self.widgets = {}
      cget = graph.axis_cget
      self.widgets['top'] = t = Pmw.Dialog(command=self.commands,
                     buttons=('OK', 'Apply','Quit'),
                     title='BltConfigureAxis')
      top = t.component('dialogchildsite')
      t = Label(top, text=axis.upper() + ' axis',
                font=('Arial','12','bold')); t.pack()
      menu_option(self, top, 'hide', 'Hide or show:', ['Show', 'Hide'],
                  int(cget(axis, 'hide')))
      menu_entry(self, top, 'title', 'Title:',
                 cget(axis, 'title'))
      menu_entry(self, top, 'titlefont', 'Title font:',
                 cget(axis, 'titlefont'))
      menu_color(self, top, 'titlecolor', 'Title color:',
                 cget(axis, 'titlecolor'))
      menu_entry(self, top, 'stepsize', 'Tick interval:',
                 cget(axis, 'stepsize'))
      menu_entry(self, top, 'subdivisions', 'Minor ticks:',
                 cget(axis, 'subdivisions'))
      menu_entry(self, top, 'ticklength', 'Tick length:',
                 cget(axis, 'ticklength'))
      menu_entry(self, top, 'tickfont', 'Tick font:',
                 cget(axis, 'tickfont'))
      menu_color(self, top, 'color', 'Axis color:',
                 cget(axis, 'color'))
      min = cget(axis, 'min')
      max = cget(axis, 'max')
      auto = ((min == "") and (max == ""))
      menu_option(self, top, 'auto', 'Limits:', ['Manual', 'Auto'], auto)
      menu_entry(self, top, 'min', 'Minimum:',
                 cget(axis, 'min'))
      menu_entry(self, top, 'max', 'Maximum:',
                 cget(axis, 'max'))
      menu_option(self, top, 'logscale', 'Scale:', ['Linear', 'Logarithmic'],
                  int(cget(axis, 'logscale')))
      
   ########################################################################
   def commands(self, button):
      widgets = self.widgets
      graph = self.graph
      axis = self.axis
      configure = graph.axis_configure
      if (button == 'OK') or (button == 'Apply'):
         configure(axis, title=widgets['title'].get())
         configure(axis, titlefont=widgets['titlefont'].get())
         configure(axis, titlecolor=widgets['titlecolor'].get())
         configure(axis, stepsize=widgets['stepsize'].get())
         configure(axis, subdivisions=widgets['subdivisions'].get())
         configure(axis, ticklength=widgets['ticklength'].get())
         configure(axis, color=widgets['color'].get())
         configure(axis, tickfont=widgets['tickfont'].get())
         configure(axis, hide=widgets['hide'].index(Pmw.SELECT))
         auto = widgets['auto'].index(Pmw.SELECT)
         if (auto):
            configure(axis, min="", max="")
         else:
            configure(axis, min=widgets['min'].get(), max=widgets['max'].get())
         configure(axis, logscale=widgets['logscale'].index(Pmw.SELECT))
         if (self.return_command != None): self.return_command(axis)
      if (button != 'Apply'): 
         self.widgets['top'].destroy()

########################################################################
class BltConfigureLegend:

   ########################################################################
   def __init__(self, graph, command=None):
      self.graph=graph
      self.return_command=command
      self.widgets = {}
      cget = graph.legend_cget
      self.widgets['top'] = t = Pmw.Dialog(command=self.commands,
                     buttons=('OK', 'Apply','Quit'),
                     title='BltConfigureLegend')
      top = t.component('dialogchildsite')
      t = Label(top, text='Legend configuration',
                font=('Arial','12','bold')); t.pack()
      initial=int(cget('hide'))
      menu_option(self, top, 'hide', 'Hide or show:', ['Show', 'Hide'],
                  int(cget('hide')))
      menu_entry(self, top, 'font', 'Legend font:', cget('font'))
      menu_color(self, top, 'foreground', 'Text color:', cget('foreground'))
      menu_color(self, top, 'background', 'Background color:', cget('background'))
      initial=cget('position')
      # Windows uses 'rightmargin' rather than 'right', etc.  Trim it.
      p = initial.find('margin')
      if (p != -1): initial=initial[:p]
      if (initial[0] == '@'): initial='manual'
      menu_option(self, top, 'position', 'Legend position:',
                       ['left', 'right', 'top', 'bottom', 'plotarea', 'manual'],
                       initial)
      menu_option(self, top, 'anchor', 'Legend anchor:',
                  ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'],
                  cget('anchor'))
      menu_entry(self, top, 'borderwidth', 'Border width:', cget('borderwidth'))
      menu_option(self, top, 'relief', 'Relief:',
                  ['raised', 'sunken', 'groove', 'ridge', 'flat'],
                  cget('relief'))
      
   ########################################################################
   def commands(self, button):
      widgets = self.widgets
      graph = self.graph
      configure = graph.legend_configure
      if (button == 'OK') or (button == 'Apply'):
         configure(hide=widgets['hide'].index(Pmw.SELECT))
         configure(font=widgets['font'].get())
         configure(foreground=widgets['foreground'].get())
         configure(background=widgets['background'].get())
         position=widgets['position'].getcurselection()
         if (position != 'manual'):
            configure(position=widgets['position'].getcurselection())
         configure(anchor=widgets['anchor'].getcurselection())
         configure(borderwidth=widgets['borderwidth'].get())
         configure(relief=widgets['relief'].getcurselection())
         if (self.return_command != None): self.return_command()
      if (button != 'Apply'): 
         self.widgets['top'].destroy()

########################################################################
class BltConfigureGrid:

   ########################################################################
   def __init__(self, graph, command=None):
      self.graph=graph
      self.return_command=command
      self.widgets = {}
      cget = graph.grid_cget
      self.widgets['top'] = t = Pmw.Dialog(command=self.commands,
                     buttons=('OK', 'Apply','Quit'),
                     title='BltConfigureGrid')
      top = t.component('dialogchildsite')
      t = Label(top, text='Grid configuration',
                font=('Arial','12','bold')); t.pack()
      initial=int(cget('hide'))
      menu_option(self, top, 'hide', 'Hide or show:', ['Show', 'Hide'],
                  int(cget('hide')))
      menu_color(self, top, 'color', 'Grid color:', cget('color'))
      menu_entry(self, top, 'linewidth', 'Line width:', cget('linewidth'))
      menu_entry(self, top, 'dashes', 'Dash pattern:', cget('dashes'))
      menu_option(self, top, 'minor', 'Minor grid lines:',
                  ['No', 'Yes'],
                  int(cget('minor')))
      
   ########################################################################
   def commands(self, button):
      widgets = self.widgets
      graph = self.graph
      configure = graph.grid_configure
      if (button == 'OK') or (button == 'Apply'):
         configure(hide=widgets['hide'].index(Pmw.SELECT))
         configure(color=widgets['color'].get())
         configure(linewidth=widgets['linewidth'].get())
         configure(dashes=widgets['dashes'].get())
         configure(minor=widgets['minor'].index(Pmw.SELECT))
         if (self.return_command != None): self.return_command()
      if (button != 'Apply'): 
         self.widgets['top'].destroy()

########################################################################
class BltConfigureElement:

   ########################################################################
   def __init__(self, graph, element, command=None):
      self.graph=graph
      self.return_command = command
      self.selected_elements = list(graph.element_names(element))
      self.selected_elements.sort()
      self.element = element = self.selected_elements[0]
      self.widgets = {}
      cget = graph.element_cget
      self.widgets['top'] = t = Pmw.Dialog(command=self.commands,
                     buttons=('OK', 'Apply','Quit'),
                     title='BltConfigureElement')
      top = t.component('dialogchildsite')
      t = Label(top, text=element + ' configuration',
                font=('Arial','12','bold')); t.pack()
      menu_option(self, top, 'hide', 'Hide or show:', ['Show', 'Hide'],
                  int(cget(element, 'hide')))
      menu_entry(self, top, 'label', 'Label:', cget(element, 'label'))
      menu_entry(self, top, 'linewidth', 'Line width:', cget(element, 'linewidth'))
      menu_entry(self, top, 'dashes', 'Line pattern:', cget(element, 'dashes'))
      line_color = cget(element, 'color')
      menu_color(self, top, 'color', 'Line color:', line_color)
      initial = cget(element, 'symbol')
      menu_option(self, top, 'symbol', 'Symbol:', 
                       ["none", "square", "circle", "diamond", "plus",
                        "cross", "splus", "scross", "triangle"],
                       initial)
      menu_entry(self, top, 'pixels', 'Symbol size:', cget(element, 'pixels'))
      menu_color(self, top, 'fill', 'Symbol fill color:',
                 cget(element, 'fill'), defcolor=line_color)
      menu_color(self, top, 'outline', 'Outline color:',
                 cget(element, 'outline'), defcolor=line_color)
      menu_entry(self, top, 'outlinewidth', 'Outline width:',
                 cget(element, 'outlinewidth'))
      initial=cget(element, 'smooth')
      menu_option(self, top, 'smooth', 'Line smoothing:',
                  ['linear', 'quadratic', 'step', 'natural'],
                  initial)
      
   ########################################################################
   def commands(self, button):
      widgets = self.widgets
      graph = self.graph
      configure = graph.element_configure
      if (button == 'OK') or (button == 'Apply'):
         for element in self.selected_elements:
            configure(element, hide=widgets['hide'].index(Pmw.SELECT))
            configure(element, label=widgets['label'].get())
            configure(element, linewidth=widgets['linewidth'].get())
            configure(element, dashes=widgets['dashes'].get())
            configure(element, color=widgets['color'].get())
            configure(element, symbol=widgets['symbol'].getcurselection())
            configure(element, pixels=widgets['pixels'].get())
            configure(element, fill=widgets['fill'].get())
            configure(element, outline=widgets['outline'].get())
            configure(element, outlinewidth=widgets['outlinewidth'].get())
            configure(element, smooth=widgets['smooth'].getcurselection())
            if (self.return_command != None): self.return_command(element)
      if (button != 'Apply'): 
         self.widgets['top'].destroy()

########################################################################
class BltConfigureMarker:

   ########################################################################
   def __init__(self, graph, marker, command=None):
      class widgets:
         pass
      self.graph=graph
      self.return_command = command
      self.selected_markers = list(graph.marker_names(marker))
      self.selected_markers.sort()
      self.marker = marker = self.selected_markers[0]
      self.widgets = {}
      self.type = graph.marker_type(self.marker)
      cget = graph.marker_cget
      self.widgets['top'] = t = Pmw.Dialog(command=self.commands,
                     buttons=('OK', 'Apply','Quit'),
                     title='BltConfigureMarker')
      top = t.component('dialogchildsite')
      t = Label(top, text=marker + ' configuration',
                font=('Arial','12','bold')); t.pack()
      menu_option(self, top, 'hide', 'Hide or show:', ['Show', 'Hide'],
           int(cget(marker, 'hide')))
      menu_entry(self, top, 'coords', 'Coordinates:',
              cget(marker, 'coords'))
      # Windows returns 'LineMarker', Linux returns 'line'
      if (self.type == 'LineMarker') or (self.type == 'line'):
         menu_color(self, top, 'outline', 'Foreground color:',
                 cget(marker, 'outline'))
         menu_color(self, top, 'fill', 'Background color:',
                 cget(marker, 'fill'))
         menu_entry(self, top, 'linewidth', 'Line width:',
                 cget(marker, 'linewidth'))
         menu_entry(self, top, 'dashes', 'Line pattern:',
                 cget(marker, 'dashes'))
     
   ########################################################################
   def commands(self, button):
      widgets = self.widgets
      graph = self.graph
      configure = graph.marker_configure
      if (button == 'OK') or (button == 'Apply'):
         for marker in self.selected_markers:
            configure(marker, hide=widgets['hide'].index(Pmw.SELECT))
            # Only change coordinates of first marker
            configure(self.selected_markers[0], coords=widgets['coords'].get())
            if (self.type == 'LineMarker') or (self.type == 'line'):
               configure(marker, outline=widgets['outline'].get())
               configure(marker, fill=widgets['fill'].get())
               configure(marker, linewidth=widgets['linewidth'].get())
               configure(marker, dashes=widgets['dashes'].get())
            if (self.return_command != None): self.return_command(marker)
      if (button != 'Apply'): 
         self.widgets['top'].destroy()

########################################################################
class BltConfigureGraph:

   ########################################################################
   def __init__(self, graph, command=None):
      self.graph=graph
      self.return_command = command
      self.widgets = {}
      cget = graph.cget
      self.widgets['top'] = t = Pmw.Dialog(command=self.commands,
                     buttons=('OK', 'Apply','Quit'),
                     title='BltConfigureGraph')
      top = t.component('dialogchildsite')
      t = Label(top, text='Graph configuration',
                font=('Arial','12','bold')); t.pack()
      lwidth=25
      menu_color(self, top, 'background', 'Widget background color:',
                 cget('background'), label_width=lwidth)
      menu_color(self, top, 'plotbackground', 'Plot background color:',
                 cget('plotbackground'), label_width=lwidth)
      menu_entry(self, top, 'title', 'Title:', cget('title'),
                 label_width=lwidth)
      menu_entry(self, top, 'font', 'Title font:', cget('font'),
                 label_width=lwidth)
      menu_entry(self, top, 'borderwidth', 'Border width:', cget('borderwidth'),
                 label_width=lwidth)
      menu_option(self, top, 'relief', 'Relief:',
                  ['raised', 'sunken', 'groove', 'ridge', 'flat'],
                  cget('relief'), label_width=lwidth)
      menu_entry(self, top, 'plotborderwidth', 'Plot border width:',
                 cget('plotborderwidth'), label_width=lwidth)
      menu_option(self, top, 'plotrelief', 'Plot relief:',
                  ['raised', 'sunken', 'groove', 'ridge', 'flat'],
                  cget('plotrelief'), label_width=lwidth)

   ########################################################################
   def commands(self, button):
      widgets = self.widgets
      graph = self.graph
      configure = graph.configure
      if (button == 'OK') or (button == 'Apply'):
         configure(background=widgets['background'].get())
         configure(plotbackground=widgets['plotbackground'].get())
         configure(title=widgets['title'].get())
         configure(font=widgets['font'].get())
         configure(borderwidth=widgets['borderwidth'].get())
         configure(relief=widgets['relief'].getcurselection())
         configure(plotborderwidth=widgets['plotborderwidth'].get())
         configure(plotrelief=widgets['plotrelief'].getcurselection())
         if (self.return_command != None): self.return_command()
      if (button != 'Apply'): 
         self.widgets['top'].destroy()

########################################################################
def menu_entry(self, parent, attribute, label, value, validate=None,
               label_width=20, entry_width=20):
   t = Pmw.EntryField(parent, value=value,
                      labelpos=W, label_text=label, label_width=label_width,
                      label_anchor=E,
                      entry_width=entry_width, entry_justify=LEFT,
                      validate=validate,
                      command=lambda s=self: s.commands('Apply'))
   t.pack(anchor=W)
   self.widgets[attribute] = t

########################################################################
def menu_option(self, parent, attribute, label, items, initial,
                label_width=20):
   t = Pmw.OptionMenu(parent, items=items, initialitem=initial,
                      labelpos=W, label_text=label, label_width=label_width,
                      label_anchor=E,
                      command=lambda v,s=self: s.commands('Apply'))
   t.pack(anchor=W)
   self.widgets[attribute] = t

########################################################################
def menu_color(self, parent, attribute, label, value, label_width=20,
               entry_width=20, defcolor=None):
   row = Frame(parent); row.pack(anchor=W, pady=2)
   t = Pmw.EntryField(row, value=value,
                      labelpos=W, label_text=label, label_width=label_width,
                      label_anchor=E,
                      entry_width=entry_width, entry_justify=LEFT,
                      command=lambda s=self, a=attribute: new_color(s, a))
   t.pack(side=LEFT)
   self.widgets[attribute] = t
   bcolor = value
   if (value == 'defcolor') and (defcolor != None): bcolor=defcolor
   if (value == ""): bcolor=None
   t = Button(row, background=bcolor, width=5, height=1,
              command=lambda s=self,v=value,a=attribute,d=defcolor:
              ask_color(s, v, a, defcolor=d))
   t.pack(side=LEFT, padx=5)
   self.widgets[attribute+'_color'] = t
      
########################################################################
def new_color(self, attribute):
   c = self.widgets[attribute].get()
   if (c == ""): c = None
   self.widgets[attribute+'_color'].configure(background=c)
   self.commands('Apply')

########################################################################
def ask_color(self, value, attribute, defcolor=None):
   if (value == 'defcolor') and (defcolor != None): value=defcolor
   c = tkColorChooser.askcolor(value, parent=self.graph)
   c = c[1]
   if (c != None):
      self.widgets[attribute].setentry(c)
      self.widgets[attribute+'_color'].configure(background=c)
      self.commands('Apply')

########################################################################
class BltSettings:

   ########################################################################
   def __init__(self):
      pass
   
########################################################################
def BltGetSettings(graph, main=1, legend=1, grid=1, axes=1,
                   elements=1, data=1, markers=1):
   s = BltSettings()
   if (main == 1):
      s.graph_config = _get_settings(graph.configure())
   if (legend == 1):
      s.legend_config = _get_settings(graph.legend_configure())
   if (grid == 1):
      s.grid_config = _get_settings(graph.grid_configure())
   if (axes == 1):
      s.axis_names = graph.axis_names()
      s.axis_config = {}
      for axis in s.axis_names:
         s.axis_config[axis] = _get_settings(
                                    graph.axis_configure(axis))
   if (elements == 1):
      s.element_names = graph.element_names()
      s.element_config = {}
      for element in s.element_names:
         s.element_config[element] = _get_settings(
                                       graph.element_configure(element))
         if (data != 1):
            # The 'x' and 'y' attributes seem to exist on Windows but not Linux
            if (hasattr(s.element_config[element], 'x')):
               del s.element_config[element]['x']
            if (hasattr(s.element_config[element], 'y')):
               del s.element_config[element]['y']
            del s.element_config[element]['xdata']
            del s.element_config[element]['ydata']
            del s.element_config[element]['data']
   if (markers == 1):
      s.marker_names = graph.marker_names()
      s.marker_config = {}
      for marker in s.marker_names:
         s.marker_config[marker] = _get_settings(
                                       graph.marker_configure(marker))
         # We don't want to save or restore the "name" parameter, it is
         # redundant since it is the name of the marker, and it is an error to
         # restore it
         del s.marker_config[marker]['name']
   return s

########################################################################
def _get_settings(dict):
   t = {}
   for key in dict.keys():
      t[key] = dict[key][-1]
   return t

########################################################################
def BltSaveSettings(graph, file, **kw):
   s = apply(BltGetSettings, (graph,), kw)
   fp = open(file, 'w')
   cPickle.dump(s, fp)
   fp.close

########################################################################
def BltLoadSettings(graph, s):
   if (hasattr(s, 'graph_config')):
       _restore_settings(s.graph_config, graph.configure)
   if (hasattr(s, 'legend_config')):
      _restore_settings(s.legend_config, graph.legend_configure)
   if (hasattr(s, 'grid_config')):
      _restore_settings(s.grid_config, graph.grid_configure)
   if (hasattr(s, 'axis_names')):
      for axis in s.axis_names:
         _restore_settings(
            s.axis_config[axis], graph.axis_configure, axis)
   if (hasattr(s, 'element_names')):
      for element in s.element_names:
         _restore_settings(
            s.element_config[element], graph.element_configure, element)
   if (hasattr(s, 'marker_names')):
      for marker in s.marker_names:
         _restore_settings(
            s.marker_config[marker], graph.marker_configure, marker)

########################################################################
def _restore_settings(dict, function, *args):
   for key in dict.keys():
      kw = {key: dict[key]}
      try:
         apply(function, args, kw)
      except:
         pass

########################################################################
def BltRestoreSettings(graph, file):
   fp = open(file, 'r')
   s = cPickle.load(fp)
   BltLoadSettings(graph, s)
