# Copyright:   (c) Oskar Petersons 2013

"""Widgets used for editing DMs and Options.

Select DMs from a listbox, then edit name and options

Loaded by the frame_01_decisionMakers module.
"""

from tkinter import *
from tkinter import ttk

class DMselector(ttk.Frame):
    """Listbox for DM Creation, Selection, and Sorting."""
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)
        self.conflict = conflict
        self.dms = conflict.decisionMakers
        #variables
        self.listVariable = StringVar(value=tuple(['Double Click to Add Item']))
        self.selIdx = None
        self.selectedDM = None
        
        #widgets
        self.label = ttk.Label(self, text="Decision Makers")
        self.dmListDisp = Listbox(self, listvariable=self.listVariable)
        self.scrollY = ttk.Scrollbar(self, orient=VERTICAL, command=self.dmListDisp.yview)
        self.upBtn   = ttk.Button(self,width=10,text='Up',     command = self.upCmd  )
        self.downBtn = ttk.Button(self,width=10,text='Down',   command = self.downCmd)
        self.delBtn  = ttk.Button(self,width=10,text='Delete', command = self.delCmd)
        
        #configuration
        self.dmListDisp.configure(yscrollcommand=self.scrollY.set)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1,weight=1)
        
        self.label.grid(column=0,row=0,columnspan=5,sticky=(N,S,E,W))
        self.dmListDisp.grid(column=0, row=1, columnspan=5, sticky=(N,S,E,W))
        self.scrollY.grid(column=5,row=1,sticky=(N,S,E,W))
        self.upBtn.grid(  column=2,row=2, sticky=(N,S,E,W))
        self.downBtn.grid(column=3,row=2, sticky=(N,S,E,W))
        self.delBtn.grid( column=4,row=2, sticky=(N,S,E,W))
        
        self.dmListDisp.bind('<<ListboxSelect>>', self.selChgCmd)
        self.dmListDisp.bind('<Double-1>', self.editCmd)
        self.dmListDisp.bind('<Delete>', self.delCmd)
        self.dmListDisp.bind('<Return>', self.editCmd)
        
    def refresh(self,event=None):
        self.updateList()
        for idx in range(len(self.dms)):
            self.dmListDisp.itemconfigure(idx, foreground='black')
        self.dmListDisp.itemconfigure(len(self.dms), foreground='#A0A0A0')
        
    def updateList(self,event=None):
        self.listVariable.set(tuple(self.dms.names()+['Double Click to Add Item']))
        
    def moveEntry(self,idx,idx2):
        """Moves an item from idx to idx2."""
        self.dms.insert(idx2,self.dms.pop(idx))
        self.updateList()
        self.dmListDisp.selection_clear(idx)
        self.dmListDisp.selection_set(idx2)
        self.selChgCmd()
        self.event_generate("<<breakingChange>>")

    def upCmd(self,event=None):
        """Moves the selected element up one space in the list"""
        idx = self.selIdx
        if idx not in [-1,0,len(self.dms)]:   #check that there is an entry selected, and it isn't the first entry.
            self.moveEntry(idx,idx-1)

    def downCmd(self,event=None):
        """Moves the selected element down one space in the list."""
        idx = self.selIdx
        if idx not in [-1,len(self.dms)-1,len(self.dms)]:   #check that there is an entry selected, and it isn't the last entry
            self.moveEntry(idx,idx+1)

    def delCmd(self,*args):
        """Deletes the selected element from the list."""
        idx = self.selIdx
        if idx != len(self.dms):        #check that a valid entry is selected
            del self.dms[idx]
            self.refresh()
            self.event_generate("<<breakingChange>>")
            self.reselect()

    def selChgCmd(self,*args):
        """Called when the selection changes."""
        self.selIdx = int(self.dmListDisp.curselection()[0])
        if self.selIdx != len(self.conflict.decisionMakers):
            self.selectedDM = self.conflict.decisionMakers[self.selIdx]
        else:
            self.selectedDM = None
        self.event_generate('<<DMselected>>')

    def editCmd(self,*args):
        """Called when a list entry is selected for editing."""
        self.event_generate('<<EditDM>>')
        #self.dmListDisp.selection_set(self.selIdx)
        
    def reselect(self,event=None):
        if self.selIdx is not None:
            self.dmListDisp.selection_set(self.selIdx)
            self.dmListDisp.event_generate('<<ListboxSelect>>')


class DMeditor(ttk.Frame):
    def __init__(self,master,conflict):
        ttk.Frame.__init__(self,master)
        self.conflict = conflict
        
        #variables
        self.labelVar = StringVar()
        self.dmNameVar = StringVar()
        self.optionEditors = []
        self.dm = None
        
        #widgets
        self.label = ttk.Label(self,textvariable=self.labelVar)
        self.dmFieldLabel = ttk.Label(self,text="DM Name:")
        self.dmNameEditor = ttk.Entry(self,textvariable=self.dmNameVar,validate='key')
        vcmd = self.dmNameEditor.register(self.dmNameMod)
        self.dmNameEditor.configure(validatecommand=(vcmd,'%P'))
        self.optionListFrame = ttk.Frame(self)
        self.newOptionBtn = ttk.Button(self,text="New Option",command=self.newOption)
        
        #configuration
        self.columnconfigure(1,weight=1)
        self.label.grid(column=0,row=0,columnspan=2,sticky=(N,S,E,W))
        ttk.Separator(self,orient=HORIZONTAL).grid(column=0,row=1,columnspan=2,sticky=(N,S,E,W),pady=3)
        self.dmFieldLabel.grid(column=0,row=2,sticky=(N,S,E,W))
        self.dmNameEditor.grid(column=1,row=2,sticky=(N,S,E,W))
        ttk.Separator(self,orient=HORIZONTAL).grid(column=0,row=3,columnspan=2,sticky=(N,S,E,W),pady=3)
        self.optionListFrame.grid(column=0,row=4,columnspan=2,sticky=(N,S,E,W))
        self.newOptionBtn.grid(column=0,row=5,sticky=(N,S,E,W))
        
        self.loadDM()
        
        
    def loadDM(self,dm=None):
        self.dm = dm
        
        print('loading '+ str(self.dm))
        
        for child in self.optionListFrame.winfo_children():
            child.destroy()
            
        ttk.Frame(self.optionListFrame).grid(column=0,row=0)
        
        if dm is None:
            self.labelVar.set("Select a Decision Maker")
            self.dmNameVar.set("No DM Selected")
            self.dmNameEditor.configure(state='disabled')
            self.newOptionBtn.configure(state='disabled')
            return
            
        self.labelVar.set("Editing DM " + self.dm.name)
        self.dmNameVar.set(self.dm.name)
        self.dmNameEditor.configure(state='normal')
        self.newOptionBtn.configure(state='normal')
        
        self.optionVars = []
        self.optionEditors = []
        
        for idx,opt in enumerate(self.dm.options):
            self.addOption(opt)
            
    def dmNameMod(self,newName):
        self.labelVar.set("Editing DM " + newName)
        self.dm.name = newName
        self.event_generate('<<dmNameChange>>')
        return True
        
    def addOption(self,opt):
        def optNameMod(newName):
            opt.name = newName
            return True
            
        def deleteOption(event=None):
            self.dm.options.remove(opt)
            self.loadDM(self.dm)
            self.event_generate('<<breakingChange>>')

        newOptionVar = StringVar(value=opt.name)
        self.optionVars.append(newOptionVar)
        newOptionEditor = ttk.Entry(self.optionListFrame,textvariable=newOptionVar,validate='key')
        self.optionEditors.append(newOptionEditor)
        ovcmd = newOptionEditor.register(optNameMod)
        newOptionEditor.configure(validatecommand=(ovcmd,'%P'))
        newOptionEditor.grid(row=len(self.optionVars),column=0,sticky=(N,S,E,W))
        newOptionDelBtn = ttk.Button(self.optionListFrame,text="X",command=deleteOption)
        newOptionDelBtn.grid(row=len(self.optionVars),column=1,sticky=(N,S,E,W))
    
    def newOption(self):
        self.dm.options.append('New Option')
        self.loadDM(self.dm)
        self.event_generate('<<breakingChange>>')
        self.optionEditors[-1].focus()
        self.optionEditors[-1].select_range(0,END)