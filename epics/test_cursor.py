from Tkinter import *
import Pmw
import time

class test_cursor:
   def __init__(self):
      self.top=t=Tk()
      l = Label(t, text='This is a label'); l.pack()
      self.e = e = Pmw.EntryField(t,
                            labelpos=W, label_text='Enter data here:'); e.pack()
      self.b = b = Button(t, text='A long calculation',
                    command=self.calc); b.pack()
      #t.mainloop()

   def calc(self):
      print 'setting cursor to watch'
      self.top.configure(cursor='watch')
      #self.b.configure(cursor='watch')
      #Pmw.showbusycursor()
      #Pmw.busycallback(time.sleep, 5)
      self.top.update()
      time.sleep(5)
      #self.top.after(5000)
      print 'setting cursor to normal'
      #Pmw.hidebusycursor()
      self.top.configure(cursor='')
      #self.b.configure(cursor='')
      self.top.quit()
      
