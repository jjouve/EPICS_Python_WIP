from Tkinter import *
import Pmw
Pmw.initialise()
t1 = Toplevel()
g1 = Pmw.Blt.Graph(t1); g1.pack()
t2 = Toplevel()
#reload(Pmw.Blt)
g2 = Pmw.Blt.Graph(t2); g2.pack()
