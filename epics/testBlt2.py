from Tkinter import *
import Pmw

def testBlt2(pmw=0):
   t = Tk()
   Pmw.initialise(t)
   l = Label(t, text='A label'); l.pack()
   b = Button(t, text='Press me'); b.pack()
   if (pmw != 0):
      e = Pmw.EntryField(t, labelpos=W, label_text='Enter something'); e.pack()
