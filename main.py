#!/usr/bin/python
import wx
import wx.lib.dialogs
import wx.stc as stc
import keyword
import os
import keywords
from xml.dom.minidom import parse
import xml.dom.minidom

if wx.Platform == '__WXMSW__':
    faces = {'times': 'Times New Roman',
             'mono': 'Courier New',
             'helv': 'Arial',
             'other': 'Comic Sans MS',
             'size': 10,
             'size2': 10,
             }
elif wx.Platform == '__WXMAC__':
    faces = {'times': 'Times New Roman',
             'mono': 'Monaco',
             'helv': 'Helvetica',
             'other': 'Monaco',
             'size': 12,
             'size2': 12,
             'size3': 10,
             }
else:
    faces = {'times': 'Times',
             'mono': 'Courier',
             'helv': 'Helvetica',
             'other': 'Courier',
             'size': 10,
             'size2': 8,
             }


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        self.dirname = ''
        self.filename = ''
        self.fileExtension = ''
        self.normalStylesFore = dict()
        self.normalStylesBack = dict()
        self.pythonStylesFore = dict()
        self.pythonStylesBack = dict()

        self.sources = []
        self.toolbars = []
        self.filenames = []
        self.dirnames = []

        self.tabIndent = False
        self.tabs = 0
        self.foldSymbols = 2
        self.leftMarginWidth = 25
        self.lineNumbersEnable = True

        wx.Frame.__init__(self, parent, title=title, size=(1024,720))
        self.control = stc.StyledTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)

        self.control.CmdKeyAssign(ord('='), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.control.CmdKeyAssign(ord('-'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.control.SetLexer(stc.STC_LEX_CPP)
        self.control.SetKeyWords(0, " ".join(keyword.kwlist))

        # Set some properties of the text control
        self.control.SetViewWhiteSpace(True)
        self.control.SetViewWhiteSpace(stc.STC_WS_VISIBLEALWAYS)
        self.control.SetProperty("fold", "1")
        self.control.SetProperty("tab.timmy.whinge.level", "1")

        self.control.SetMargins(5,0)
        self.control.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        self.control.SetMarginWidth(1, self.leftMarginWidth)

        if self.foldSymbols == 0:
            # Arrow pointing right for contracted folders, arrow pointing down for expanded
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_ARROWDOWN, "black", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_ARROW, "black", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "black", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "black", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")

        elif self.foldSymbols == 1:
            # Plus for contracted folders, minus for expanded
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black")

        elif self.foldSymbols == 2:
            # Like a flattened tree control using circular headers and curved joins
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_CIRCLEMINUS, "white", "#404040")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_CIRCLEPLUS, "white", "#404040")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#404040")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNERCURVE, "white", "#404040")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_CIRCLEPLUSCONNECTED, "white", "#404040")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white",
                                      "#404040")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE, "white", "#404040")

        elif self.foldSymbols == 3:
            # Like a flattened tree control using square headers
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "#808080")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "#808080")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#808080")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "#808080")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, "white", "#808080")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
            self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, "white", "#808080")



        self.CreateStatusBar()
        self.UpdateLineCol(self)
        self.StatusBar.SetBackgroundColour((100,100,100))

        filemenu = wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open an existing document")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save", "Save the document")
        menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "Save &As", "Save as new document")
        menuClose = filemenu.Append(wx.ID_CLOSE, "&Close", "Close current document")

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

        terminalmenu = wx.Menu()
        menuOpenTerminal = terminalmenu.Append(wx.ID_ANY, "&Open", "Open up a terminal")
        menuRun = terminalmenu.Append(wx.ID_ANY, "&Run", "Run the current python file")

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
        menubar.Append(editmenu, "&Edit")
        menubar.Append(prefmenu, "&Preferences")
        menubar.Append(helpmenu, "&Help")
        menubar.Append(terminalmenu, "&Terminal")
        self.SetMenuBar(menubar)

        self.toolbar = self.CreateToolBar(wx.TB_TEXT | wx.TB_NOICONS, -1)
        self.SetToolBar(self.toolbar)


        #start new code here
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menuSaveAs)

        self.Bind(wx.EVT_MENU, self.OnOpenTerminal, menuOpenTerminal)
        self.Bind(wx.EVT_MENU, self.OnRun, menuRun)

        self.Bind(wx.EVT_MENU, self.OnUndo, menuUndo)
        self.Bind(wx.EVT_MENU, self.OnRedo, menuRedo)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, menuSelectAll)
        self.Bind(wx.EVT_MENU, self.OnCopy, menuCopy)
        self.Bind(wx.EVT_MENU, self.OnCut, menuCut)
        self.Bind(wx.EVT_MENU, self.OnPaste, menuPaste)

        self.Bind(wx.EVT_MENU, self.OnToggleLinbeNumbers, menuLineNumbers)

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        self.control.Bind(wx.EVT_KEY_UP, self.UpdateLineCol)
        self.control.Bind(wx.EVT_CHAR_HOOK, self.OnCharEvent)
        self.control.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Show()

        # defaulting the style
        self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
        self.control.StyleClearAll()  # reset all to be like default

        # global default styles for all languages
        self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.control.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")
        self.control.SetBackSpaceUnIndents(1)
        self.control.SetTabIndents(1)
        self.control.SetUseTabs(1)
        self.SetStyling()

    def AddTool(self):
        if len(self.toolbars) < 11:
            self.toolbars.append(self.toolbar.AddLabelTool(wx.ID_ANY, self.filename, wx.Bitmap("Blank.gif")))
            print(len(self.toolbars))
            self.sources.append(self.control.GetValue())
            self.filenames.append(self.filename)
            self.dirnames.append(self.dirname)
            self.toolbar.Realize()

            if len(self.toolbars) == 1:
                self.Bind(wx.EVT_MENU, self.onOne, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 2:
                self.Bind(wx.EVT_MENU, self.onTwo, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 3:
                self.Bind(wx.EVT_MENU, self.onThree, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 4:
                self.Bind(wx.EVT_MENU, self.onFour, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 5:
                self.Bind(wx.EVT_MENU, self.onFive, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 6:
                self.Bind(wx.EVT_MENU, self.onSix, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 7:
                self.Bind(wx.EVT_MENU, self.onSeven, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 8:
                self.Bind(wx.EVT_MENU, self.onEight, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 9:
                self.Bind(wx.EVT_MENU, self.onNine, self.toolbars[len(self.toolbars)-1])
            elif len(self.toolbars) == 10:
                self.Bind(wx.EVT_MENU, self.onTen, self.toolbars[len(self.toolbars)-1])

    def onOne(self,e):
        print(self.sources[0])
        self.control.SetValue(self.sources[0])
        self.filename = self.filenames[0]
        self.dirname = self.dirnames[0]
        self.SetStyling()
    def onTwo(self,e):
        self.control.SetValue(self.sources[1])
        self.filename = self.filenames[1]
        self.dirname = self.dirnames[1]
        self.SetStyling()
    def onThree(self,e):
        self.control.SetValue(self.sources[2])
        self.filename = self.filenames[2]
        self.dirname = self.dirnames[2]
        self.SetStyling()
    def onFour(self,e):
        self.control.SetValue(self.sources[3])
        self.filename = self.filenames[3]
        self.dirname = self.dirnames[3]
        self.SetStyling()
    def onFive(self,e):
        self.control.SetValue(self.sources[4])
        self.filename = self.filenames[4]
        self.dirname = self.dirnames[4]
        self.SetStyling()
    def onSix(self,e):
        self.control.SetValue(self.sources[5])
        self.filename = self.filenames[5]
        self.dirname = self.dirnames[5]
        self.SetStyling()
    def onSeven(self,e):
        self.control.SetValue(self.sources[6])
        self.filename = self.filenames[6]
        self.dirname = self.dirnames[6]
        self.SetStyling()
    def onEight(self,e):
        self.control.SetValue(self.sources[7])
        self.filename = self.filenames[7]
        self.dirname = self.dirnames[7]
        self.SetStyling()
    def onNine(self,e):
        self.control.SetValue(self.sources[8])
        self.filename = self.filenames[8]
        self.dirname = self.dirnames[8]
        self.SetStyling()
    def onTen(self,e):
        self.control.SetValue(self.sources[9])
        self.filename = self.filenames[9]
        self.dirname = self.dirnames[9]
        self.SetStyling()

    def OnOpen(self, e):
        try:
            dialog = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
            if (dialog.ShowModal() == wx.ID_OK):
                self.filename = dialog.GetFilename()
                self.dirname = dialog.GetDirectory()
                self.SetStyling()
                f = open(os.path.join(self.dirname, self.filename), 'r')
                self.control.SetValue(f.read())
                self.AddTool()
                f.close()
            dialog.Destroy()
        except:
            dialog = wx.MessageDialog(self, "couldn't open file", "Error", wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()

    def OnSave(self, e):
        try:
            f = open(os.path.join(self.dirname, self.filename), 'w')
            f.write(self.control.GetValue())
            f.close()
        except:
            try:
                dlg = wx.FileDialog(self, "Save file as", self.dirname, "Untitled", "*.*",
                                    wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if (dlg.ShowModal() == wx.ID_OK):
                    self.filename = dlg.GetFilename()
                    self.fileExtension = self.filename.split('.')[1]
                    self.dirname = dlg.GetDirectory()
                    self.SetStyling()
                    f = open(os.path.join(self.dirname, self.filename), 'w')
                    f.write(self.control.GetValue())
                    f.close()
                dlg.Destroy()
            except:
                pass

    def OnSaveAs(self, e):
        try:
            dlg = wx.FileDialog(self, "Save file as", self.dirname, self.filename, "*.*",
                                wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if (dlg.ShowModal() == wx.ID_OK):
                self.filename = dlg.GetFilename()
                self.fileExtension = self.filename.split('.')[1]
                self.dirname = dlg.GetDirectory()
                self.SetStyling()
                f = open(os.path.join(self.dirname, self.filename), 'w')
                f.write(self.control.GetValue())
                self.AddTool(self)
                f.close()
            dlg.Destroy()
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

    def OnOpenTerminal(self,e):
        os.system("termite")

    def OnRun(self,e):
        if (self.fileExtension == "py"):
            os.system("python -m" + self.filename)

    def UpdateLineCol(self,e):
        line = self.control.GetCurrentLine() + 1
        col = self.control.GetColumn(self.control.GetCurrentPos())
        pos = self.control.GetCurrentPos()
        stat = "Line %s, Column %s, Pos %s" % (line, col, pos)
        self.StatusBar.SetStatusText(stat, 0)

    def OnLeftUp(self, e):
        # This way if you click on another position in the text box
        # it will update the line/col number in the status bar (like it should)
        self.UpdateLineCol(self)
        e.Skip()


    def OnCharEvent(self,e):
        keycode = e.GetKeyCode()
        altdown = e.AltDown()
        col =self.control.GetColumn(self.control.GetCurrentPos())
        line = self.control.GetCurrentLine()
        tempstring = ''
        if self.tabIndent != True and keycode == 13 and self.control.GetLineIndentation(self.control.GetCurrentLine()) >= self.control.GetTabWidth():
            if (line < self.control.GetLineCount()-1):
                self.tabs = self.control.GetLineIndentation(self.control.GetCurrentLine()) / self.control.GetTabWidth()
                tempPos = self.control.GetCurrentPos()
                self.control.SetSelectionStart(self.control.GetCurrentPos())
                self.control.SetSelectionEnd(self.control.GetLineEndPosition(self.control.GetCurrentLine()))
                print(self.control.GetCurrentPos())
                print(self.control.GetSelectedText())
                tempstring = self.control.GetSelectedText()
                self.control.DeleteRange(tempPos, self.control.GetCurrentPos() - tempPos)
                self.control.LineDown()
                self.control.Home()
                for x in range(0,int(self.tabs)):
                    self.control.Tab()
                self.control.AddText(tempstring)
                self.control.NewLine()
                self.control.LineUp()
                self.control.LineEnd()

            else:
                self.control.NewLine()
                self.tabs = self.control.GetLineIndentation(self.control.GetCurrentLine()-1) / self.control.GetTabWidth()
                self.control.SetSelectionStart(self.control.GetCurrentPos())
                self.control.LineEnd()
                self.control.SetSelectionEnd(self.control.GetCurrentPos())
                print(self.control.GetSelection())
                self.control.MoveSelectedLinesDown()
                self.control.Home()
                for x in range(0,int(self.tabs)):
                    self.control.Tab()
                self.control.LineEnd()
            return
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

    def SetStyling(self):
        self.control.StyleClearAll()


        style = {'comment': {'color': '#bc9458', 'font-style': 'italic'},
                 'constant.numeric': {'color': '#8927ff', 'font-weight': 'normal'},
                 'constant.numeric.keyword': {'color': '#6d9cbe'},
                 'keyword': {'color': '#bc3a38', 'font-strike-through': 'none', 'font-weight': 'normal'},
                 'keyword.control': {'color': '#cc7833'},
                 'keyword.type': {'color': '#cc7833'},
                 'language.function': {'color': '#fac56d'},
                 'language.operator': {'color': '#5e9f00'},
                 'language.variable': {'color': '#d0d1ff'},
                 'markup.comment': {'color': '#bc9458', 'font-style': 'italic'},
                 'markup.constant.entity': {'color': '#6e9cbe'},
                 'markup.declaration': {'color': '#e8c06a'},
                 'markup.inline.cdata': {'color': '#e9c053'},
                 'markup.processing': {'color': '#68685b', 'font-weight': 'bold'},
                 'markup.tag': {'color': '#e8c06a'},  #
                 'markup.tag.attribute.name': {'color': '#e8c06a'},
                 'markup.tag.attribute.value': {'color': '#a5c261', 'font-style': 'italic'},
                 'meta.default': {'background-color': '#333333', 'color': '#e6e1dc'},
                 'meta.highlight.currentline': {'background-color': '#FFFFFF'},
                 'meta.important': {'color': '#b66418', 'font-style': 'italic'},
                 'meta.invalid': {'background-color': '#333333', 'color': '#ffffff', 'font-weight': 'bold'},
                 'meta.invisible.characters': {'color': '#404040'},
                 'meta.link': {'color': '#a5c261', 'font-style': 'normal', 'font-underline': 'none'},
                 'string': {'color': '#99e84d', 'font-style': 'italic'},
                 'string.regex': {'color': '#99b93e'},
                 'string.regex.escaped': {'color': '#4b8928'},
                 'style.at-rule': {'color': '#b96619', 'font-weight': 'bold'},
                 'style.comment': {'color': '#bc9458', 'font-style': 'italic', 'font-weight': 'normal'},
                 'style.property.name': {'color': '#6e9cbe'},
                 'style.value.color.rgb-value': {'color': '#6d9cbe'},
                 'style.value.keyword': {'color': '#a5c261'},
                 'style.value.numeric': {'color': '#99b62d'},
                 'style.value.string': {'color': '#a5c261', 'font-style': 'italic'},
                 'support': {'color': '#da4939'}
                 }

        self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
        self.control.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "front:#000000,back:#333333,face:%(helv)s,size:%(size2)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.control.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")
        self.control.SetSelAlpha(60)

        # Global default styles for all languages
        if (self.filename != '' and self.filename.split('.')[1] == ""):
            self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, "#FFFFFF")
            self.control.StyleSetForeground(stc.STC_STYLE_DEFAULT, "#777777")
            self.control.SetSelBackground(True, "#333333")
            self.control.SetSelForeground(True, "#FF0000")

        else:
            self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, "#333333")
            self.control.StyleSetForeground(stc.STC_STYLE_DEFAULT, "#777777")
            self.control.SetSelBackground(True, "#FFFFFF")

        if (self.filename != '' and self.filename.split('.')[1] == "cpp" or self.filename != '' and self.filename.split('.')[1] == "h"):
            self.control.SetKeyWords(0, keywords.c_kw)
            self.control.StyleSetSpec(stc.STC_C_DEFAULT,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_COMMENTLINE,
                                     "fore:" + style["comment"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",italic,face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_COMMENTLINEDOC,
                                     "fore:" + style["comment"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",italic,face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_COMMENT,
                                     "fore:" + style["comment"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",italic,face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_COMMENTDOC,
                                     "fore:" + style["comment"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",italic,face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_NUMBER,
                                     "fore:" + style["constant.numeric"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_STRING,
                                     "fore:" + style["string"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_STRINGEOL,
                                     "fore:" + style["string"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_CHARACTER,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            try:
                self.control.StyleSetSpec(stc.STC_C_WORD,
                                         "fore:" + style["keyword"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
                self.control.StyleSetSpec(stc.STC_C_WORD2,
                                         "fore:" + style["keyword.control"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            except:
                self.control.StyleSetSpec(stc.STC_C_WORD,
                                         "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
                self.control.StyleSetSpec(stc.STC_C_WORD2,
                                         "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(stc.STC_C_OPERATOR,
                                     "fore:" + style["language.operator"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(stc.STC_C_GLOBALCLASS,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(stc.STC_C_IDENTIFIER,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(stc.STC_C_REGEX,
                                     "fore:" + style["string.regex"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
        elif (self.filename != '' and self.filename.split('.')[1] == "py"):
            self.control.SetKeyWords(0, keywords.p_kw)
            self.control.StyleSetSpec(wx.stc.STC_P_COMMENTLINE,
                                     "fore:" + style["comment"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",italic,face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_NUMBER,
                                     "fore:" + style["constant.numeric"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_STRING,
                                     "fore:" + style["string"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_STRINGEOL,
                                     "fore:" + style["string"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(wx.stc.STC_P_TRIPLE,
                                     "fore:" + style["string"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE,
                                     "fore:" + style["string"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(wx.stc.STC_P_CHARACTER,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            try:
                self.control.StyleSetSpec(wx.stc.STC_P_WORD,
                                         "fore:" + style["keyword.control"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
                self.control.StyleSetSpec(wx.stc.STC_P_WORD2,
                                         "fore:" + style["keyword.control"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            except:
                self.control.StyleSetSpec(wx.stc.STC_P_WORD,
                                         "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
                self.control.StyleSetSpec(wx.stc.STC_P_WORD2,
                                         "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                             'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(wx.stc.STC_P_OPERATOR,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_DECORATOR,
                                     "fore:" + style["meta.important"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_DEFAULT,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK,
                                     "fore:" + style["comment"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",italic,face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(wx.stc.STC_P_CLASSNAME,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)
            self.control.StyleSetSpec(wx.stc.STC_P_DEFNAME,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            self.control.StyleSetSpec(wx.stc.STC_P_IDENTIFIER,
                                     "fore:" + style["meta.default"]['color'] + ",back:" + style["meta.default"][
                                         'background-color'] + ",face:%(other)s,size:%(size)d" % faces)

            # Caret/Insertion Point
            self.control.SetCaretForeground("#ffffff")
            self.control.SetCaretLineBackground("#ffffff")


app = wx.App(False)
frame = MainWindow(None, "Rutext")
app.MainLoop()