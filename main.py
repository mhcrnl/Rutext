#!/usr/bin/python
import wx
import wx.lib.dialogs
import wx.stc as stc
import os
faces = {
    'times': 'Times New Roman',
    'mono': 'Courier New',
    'helv': 'Ariel',
    'other': 'Comos Sans MS',
    'size': 10,
    'size2': 8,
}

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.dirname = ''
        self.filename = ''
        self.leftMarginWidth = 25
        self.lineNumbersEnable = True

        wx.Frame.__init__(self, parent, title=title, size=(800,600))
        self.control = stc.StyledTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)

        self.control.CmdKeyAssign(ord('='), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.control.CmdKeyAssign(ord('-'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.control.SetViewWhiteSpace(False)

        self.control.SetMargins(5,0)
        self.control.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.control.SetMarginWidth(1, self.leftMarginWidth)

        self.CreateStatusBar()
        self.StatusBar.SetBackgroundColour((100,100,100))

        filemenu = wx.Menu()
        menuNew = filemenu.Append(wx.ID_NEW, "&New", "Create a new document")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open an existing document")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save", "Save the document")
        menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "Save &As", "Save as new document")

        editmenu = wx.Menu()
        menuUndo = editmenu.Append(wx.ID_UNDO, "&Undo", "Undo last action")
        menuRedo = editmenu.Append(wx.ID_REDO, "&Redo", "Redo last action")
        editmenu.AppendSeparator()
        menuSelectAll = editmenu.Append(wx.ID_SELECTALL, "&Select All", "Select all lines")
        menuCopy = editmenu.Append(wx.ID_COPY, "&Copy", "Copy selected text")
        menuCut = editmenu.Append(wx.ID_CUT, "&Cut", "Cut selected text")
        menuPaste = editmenu.Append(wx.ID_PASTE, "&Paste", "Paste copied text")

        prefmenu = wx.Menu()
        menuLineNumbers = prefmenu.Append(wx.ID_ANY, "&Toggle line numbers", "Show/hide line numbers")

        helpmenu = wx.Menu()
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "Info and credits")

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(editmenu, "&Edit")
        menubar.Append(prefmenu, "&Preferences")
        menubar.Append(helpmenu, "&Help")
        self.SetMenuBar(menubar)

        #start new code here
        self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menuSaveAs)

        self.Bind(wx.EVT_MENU, self.OnUndo, menuUndo)
        self.Bind(wx.EVT_MENU, self.OnRedo, menuRedo)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, menuSelectAll)
        self.Bind(wx.EVT_MENU, self.OnCopy, menuCopy)
        self.Bind(wx.EVT_MENU, self.OnCut, menuCut)
        self.Bind(wx.EVT_MENU, self.OnPaste, menuPaste)

        self.Bind(wx.EVT_MENU, self.OnToggleLinbeNumbers, menuLineNumbers)

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        self.control.Bind(wx.EVT_KEY_UP, self.UpdateLineCol)
        self.control.Bind(wx.EVT_CHAR, self.OnCharEvent)

        self.Show()

    def OnNew(self, e):
        self.filename = ''
        self.control.SetValue("")

    def OnOpen(self, e):
        try:
            dialog = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
            if (dialog.ShowModal() == wx.ID_OK):
                self.filename = dialog.GetFilename()
                self.dirname = dialog.GetDirectory()
                f = open(os.path.join(self.dirname, self.filename), 'r')
                self.control.SetValue(f.read())
                f.close()
            dialog.Destroy()
        except:
            dialog = wx.MessageDialog(self, "couldn't open file", "Error", wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

    def OnSave(self, e):
        try:
            f = open(os.path.join(self.direname, self.filename), 'w')
            f.write(self.control.GetValue())
            f.Close()
        except:
            try:
                dialog = wx.FIleDialog(self, "Save file as", self. dirname, "Untitled", "*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if (dialog.ShowModal() == wx.ID_OK):
                    self.filename = dialog.GetFilename()
                    self.dirname = dialog.GetDirectory()
                    f = open(os.path.join(self.dirname, self.filename), 'w')
                    f.write(self.control.GetValue())
                    f.Close()
                dialog.Destroy()
            except:
                pass

    def OnSaveAs(self, e):
        try:
            f = open(os.path.join(self.direname, self.filename), 'w')
            f.write(self.control.GetValue())
            f.Close()
        except:
            try:
                dialog = wx.FileDialog(self, "Save file as", self. dirname, "Untitled", "*.*", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if (dialog.ShowModal() == wx.ID_OK):
                    self.filename = dialog.GetFilename()
                    self.dirname = dialog.GetDirectory()
                    f = open(os.path.join(self.dirname, self.filename), 'w')
                    f.write(self.control.GetValue())
                    f.Close()
                dialog.Destroy()
            except:
                pass

    def OnClose(self,e):
        self.Close(True)

    def OnUndo(self, e):
        self.control.Undo()

    def OnRedo(self,e):
        self.control.Redo()

    def OnSelectAll(self, e):
        self.control.SelectAll()

    def OnCopy(self, e):
        self.control.Copy()

    def OnCut(self, e):
        self.control.Cut()

    def OnPaste(self, e):
        self.control.Paste()

    def OnToggleLinbeNumbers(self,e):
        if (self.lineNumbersEnable):
            self.control.SetMarginWidth(1,0)
            self.lineNumbersEnable = False
        else:
            self.control.SetMarginWidth(1, self.leftMarginWidth)
            self.lineNumbersEnable = True

    def OnAbout(self,e):
        dialog = wx.MessageDialog(self, "Made in Python by Rutger Klamer", "About", wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()

    def UpdateLineCol(self,e):
        line = self.control.GetCurrentLine() + 1
        col = self.control.GetColumn(self.control.GetCurrentPos())
        stat = "Line %s, Column %s" % (line, col)
        self.StatusBar.SetStatusText(stat, 0)

    def OnCharEvent(self,e):
        keycode = e.GetKeyCode()
        altdown = e.AltDown()
        if (keycode == 14):
            self.OnNew(self)
        elif(keycode == 15):
            self.OnOpen(self)
        elif (keycode == 19):
            self.OnSave(self)
        elif(altdown and (keycode == 115)):
            self.OnSaveAs(self)
        elif (keycode == 340):
            self.OnAbout(self)
        else:
            e.Skip()


app = wx.App(False)
frame = MainWindow(None, "Rutext")
app.MainLoop()