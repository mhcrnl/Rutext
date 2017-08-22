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

        self.foldSymbols = 2
        self.leftMarginWidth = 25
        self.lineNumbersEnable = True

        wx.Frame.__init__(self, parent, title=title, size=(1024,720))
        self.control = stc.StyledTextCtrl(self, style=wx.TE_MULTILINE | wx.TE_WORDWRAP)

        self.control.CmdKeyAssign(ord('='), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.control.CmdKeyAssign(ord('-'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.control.SetLexer(stc.STC_LEX_PYTHON)
        self.control.SetKeyWords(0, " ".join(keyword.kwlist))

        # Set some properties of the text control
        self.control.SetViewWhiteSpace(False)
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

        #start new code here
        self.Bind(wx.EVT_MENU, self.OnNew, menuNew)
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
        self.control.Bind(wx.EVT_CHAR, self.OnCharEvent)
        self.control.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        \
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

        self.SetStyling()

    def OnNew(self, e):
        self.filename = ''
        self.fileExtension = ''
        self.control.SetValue("")

    def OnOpen(self, e):
        try:
            dialog = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN)
            if (dialog.ShowModal() == wx.ID_OK):
                self.filename = dialog.GetFilename()
                self.fileExtension = self.filename.split('.')[1]
                self.dirname = dialog.GetDirectory()
                self.SetStyling()
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
        os.system("termite 'ls'")

    def OnRun(self,e):
        if (self.fileExtension == "py"):
            os.system("python -m" + self.filename)

    def UpdateLineCol(self,e):
        line = self.control.GetCurrentLine() + 1
        col = self.control.GetColumn(self.control.GetCurrentPos())
        stat = "Line %s, Column %s" % (line, col)
        self.StatusBar.SetStatusText(stat, 0)

    def OnLeftUp(self, e):
        # This way if you click on another position in the text box
        # it will update the line/col number in the status bar (like it should)
        self.UpdateLineCol(self)
        e.Skip()

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
        self.control.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.control.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")
        self.control.SetSelAlpha(120)

        # Global default styles for all languages
        if (self.fileExtension == ""):
            self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, "#FFFFFF")
            self.control.SetSelBackground(True, "#FFFFFF")
        else:
            self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, "#333333")
            self.control.SetSelBackground(True, "#333333")

        if (self.fileExtension == "cpp" or self.fileExtension == "h"):
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
        elif (self.fileExtension == "py"):
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