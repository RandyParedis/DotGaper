"""Preferences window for the GraphDonkey application.

Author: Randy Paredis
Date:   17/12/2019
"""
from PyQt5 import QtWidgets, QtGui, uic
from main.extra.IOHandler import IOHandler
from main.extra import Constants
import configparser
import glob
import re
import os


def bool(name: str):
    if name in ["True", "true"]:
        return True
    if name in ["False", "false"]:
        return False
    return name

class Preferences(QtWidgets.QDialog):
    def __init__(self, parent):
        super(Preferences, self).__init__(parent)
        uic.loadUi(IOHandler.dir_ui("Preferences.ui"), self)
        self.buttonBox.clicked.connect(self.restoreDefaults)
        self.check_monospace.toggled.connect(self.setFontCombo)

        self.themes = []
        self.preferences = IOHandler.get_preferences()
        self.check_parse.toggled.connect(self.parseDisable)
        self._setColorPickers()
        self.fillQuickSelect()
        self.rectify()

        self.combo_theme.activated.connect(self.setTheme)
        self.pb_reload.clicked.connect(self.setTheme)
        self.pb_saveTheme.clicked.connect(self.saveTheme)

    def parseDisable(self, b):
        if not b:
            self.check_autorender.setChecked(False)
            self.check_autorender.setEnabled(False)

    def fillQuickSelect(self):
        self.combo_theme.clear()
        files = [f for f in glob.glob(IOHandler.dir_styles() + "**/*.ini", recursive=True)]
        self.themes = sorted([Theme(f) for f in files])
        for theme in self.themes:
            self.combo_theme.addItem(theme.name, theme)

    def setFontCombo(self, on):
        f = QtWidgets.QFontComboBox.MonospacedFonts if on else QtWidgets.QFontComboBox.AllFonts
        self.font_editor.setFontFilters(f)

    def _setColorPickers(self):
        self.names_general = [
            "col_foreground",
            "col_window",
            "col_base",
            "col_alternateBase",
            "col_tooltipBase",
            "col_tooltipText",
            "col_text",
            "col_button",
            "col_buttonText",
            "col_brightText",
            "col_highlight",
            "col_highlightedText",
            "col_link",
            "col_visitedLink"
        ]
        self.names_editor =[
            "col_cline",
            "col_lnf",
            "col_lnb",
            "col_clnf",
            "col_clnb",
            "col_find"
        ]
        self.names_syntax =[
            "col_keyword",
            "col_attribute",
            "col_number",
            "col_string",
            "col_html",
            "col_comment",
            "col_hash",
            "col_error"
        ]
        lo = self.box_general.layout()
        for i in range(len(self.names_general)):
            name = self.names_general[i]
            setattr(self, name, ColorButton(parent=self))
            lo.addWidget(getattr(self, name), i, 2)

        lo = self.box_editor.layout()
        for i in range(len(self.names_editor)):
            name = self.names_editor[i]
            setattr(self, name, ColorButton(parent=self))
            lo.addWidget(getattr(self, name), i, 2)

        lo = self.box_syntax.layout()
        for i in range(len(self.names_syntax)):
            name = self.names_syntax[i]
            setattr(self, name, ColorButton(parent=self))
            lo.addWidget(getattr(self, name), i, 2)

    def setTheme(self, idx):
        name = self.combo_theme.currentText()
        theme = [x for x in self.themes if x.name == name][0]
        lst = self.names_general + self.names_editor + self.names_syntax
        for i in range(len(lst)):
            name = lst[i]
            getattr(self, name).setColor(QtGui.QColor(theme.color(name[4:].lower(), getattr(self, name).colorName())))

    def findColor(self, identifier):
        name = self.combo_theme.currentText()
        theme = [x for x in self.themes if x.name == name][0]
        return theme.color(identifier)

    def rectify(self):
        # GENERAL
        if True:
            self.check_rememberLayout.setChecked(bool(self.preferences.value("rememberLayout", True)))
            self.check_autohide.setChecked(bool(self.preferences.value("autohide", True)))
            restore = int(self.preferences.value("restore", 0))
            if restore == 0:
                self.radio_ws_openempty.setChecked(True)
                self.radio_ws_restore.setChecked(False)
                self.radio_ws_none.setChecked(False)
            elif restore == 1:
                self.radio_ws_openempty.setChecked(False)
                self.radio_ws_restore.setChecked(True)
                self.radio_ws_none.setChecked(False)
            else:
                self.radio_ws_openempty.setChecked(False)
                self.radio_ws_restore.setChecked(False)
                self.radio_ws_none.setChecked(True)
            self.num_recents.setValue(int(self.preferences.value("recents", 5)))
            self.combo_encoding.setCurrentText(self.preferences.value("encoding", "UTF-8").upper())
            self.combo_lineEndings.setCurrentIndex(int(self.preferences.value("endings",
                                                                              Constants.ENDINGS.index(os.linesep))))

        # EDITOR
        if True:
            defFont = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
            self.font_editor.setCurrentFont(QtGui.QFont(self.preferences.value("font", defFont.family())))
            self.num_font.setValue(int(self.preferences.value("fontsize", 12)))
            self.num_tabwidth.setValue(int(self.preferences.value("tabwidth", 4)))
            self.check_lineNumbers.setChecked(bool(self.preferences.value("showLineNumbers", True)))
            self.check_highlightLine.setChecked(bool(self.preferences.value("highlightCurrentLine", True)))
            self.check_parentheses.setChecked(bool(self.preferences.value("parentheses", True)))
            self.check_spaceTabs.setChecked(bool(self.preferences.value("spacesOverTabs", False)))
            self.check_monospace.setChecked(bool(self.preferences.value("monospace", True)))
            self.check_syntax.setChecked(bool(self.preferences.value("syntaxHighlighting", True)))
            self.check_parse.setChecked(bool(self.preferences.value("useParser", True)))
            self.check_autorender.setChecked(bool(self.preferences.value("autorender", True)))
            self.parseDisable(self.check_parse.isChecked())

        # APPEARANCE
        if True:
            self.combo_style.setCurrentIndex(int(self.preferences.value("style", 0)))
            self.combo_theme.setCurrentText(self.preferences.value("theme", "Light Lucy"))
            # lst = self.names_general + self.names_editor + self.names_syntax
            # for i in range(len(lst)):
            #     name = lst[i]
            #     cname = name.replace("_", ".")
            #     getattr(self, name).setColor(QtGui.QColor(self.preferences.value(cname, self.findColor(cname[4:]))))

            # BUILTIN STANDARD THEME IN CASE SOMEONE MESSES WITH THE FILES:
            self.col_foreground.setColor(QtGui.QColor(self.preferences.value("col.foreground", "#000000")))
            self.col_window.setColor(QtGui.QColor(self.preferences.value("col.window", "#efefef")))
            self.col_base.setColor(QtGui.QColor(self.preferences.value("col.base", "#ffffff")))
            self.col_alternateBase.setColor(QtGui.QColor(self.preferences.value("col.alternateBase", "#f7f7f7")))
            self.col_tooltipBase.setColor(QtGui.QColor(self.preferences.value("col.tooltipBase", "#ffffdc")))
            self.col_tooltipText.setColor(QtGui.QColor(self.preferences.value("col.tooltipText", "#000000")))
            self.col_text.setColor(QtGui.QColor(self.preferences.value("col.text", "#000000")))
            self.col_button.setColor(QtGui.QColor(self.preferences.value("col.button", "#efefef")))
            self.col_buttonText.setColor(QtGui.QColor(self.preferences.value("col.buttonText", "#000000")))
            self.col_brightText.setColor(QtGui.QColor(self.preferences.value("col.brightText", "#dcdcff")))
            self.col_highlight.setColor(QtGui.QColor(self.preferences.value("col.highlight", "#30acc6")))
            self.col_highlightedText.setColor(QtGui.QColor(self.preferences.value("col.highlightedText", "#ffffff")))
            self.col_link.setColor(QtGui.QColor(self.preferences.value("col.link", "#8be9fd")))
            self.col_visitedLink.setColor(QtGui.QColor(self.preferences.value("col.visitedLink", "#253fe8")))
            self.col_cline.setColor(QtGui.QColor(self.preferences.value("col.cline", "#fffeb5")))
            self.col_lnf.setColor(QtGui.QColor(self.preferences.value("col.lnf", "#000000")))
            self.col_lnb.setColor(QtGui.QColor(self.preferences.value("col.lnb", "#f7f7f7")))
            self.col_clnf.setColor(QtGui.QColor(self.preferences.value("col.clnf", "#ffffff")))
            self.col_clnb.setColor(QtGui.QColor(self.preferences.value("col.clnb", "#30acc6")))
            self.col_find.setColor(QtGui.QColor(self.preferences.value("col.find", "#8be9fd")))
            self.col_keyword.setColor(QtGui.QColor(self.preferences.value("col.keyword", "#800000")))
            self.col_attribute.setColor(QtGui.QColor(self.preferences.value("col.attribute", "#000080")))
            self.col_number.setColor(QtGui.QColor(self.preferences.value("col.number", "#ff00ff")))
            self.col_string.setColor(QtGui.QColor(self.preferences.value("col.string", "#158724")))
            self.col_html.setColor(QtGui.QColor(self.preferences.value("col.html", "#158724")))
            self.col_comment.setColor(QtGui.QColor(self.preferences.value("col.comment", "#0000ff")))
            self.col_hash.setColor(QtGui.QColor(self.preferences.value("col.hash", "#0000ff")))
            self.col_error.setColor(QtGui.QColor(self.preferences.value("col.error", "#ff0000")))

        # SHORTCUTS
        if True:
            self.ks_new.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.new", "CTRL+N")))
            self.ks_open.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.open", "CTRL+O")))
            self.ks_save.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.save", "CTRL+S")))
            self.ks_save_all.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.save_all", "")))
            self.ks_save_as.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.save_as", "CTRL+SHIFT+S")))
            self.ks_export.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.export", "CTRL+E")))
            self.ks_clear_recents.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.clear_recents", "")))
            self.ks_preferences.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.preferences", "CTRL+P")))
            self.ks_close_file.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.close_file", "CTRL+W")))
            self.ks_exit.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.exit", "CTRL+Q")))
            self.ks_undo.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.undo", "CTRL+Z")))
            self.ks_redo.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.redo", "CTRL+SHIFT+Z")))
            self.ks_select_all.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.select_all", "CTRL+A")))
            self.ks_delete.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.delete", "")))
            self.ks_copy.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.copy", "CTRL+C")))
            self.ks_cut.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.cut", "CTRL+X")))
            self.ks_paste.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.paste", "CTRL+V")))
            self.ks_duplicate.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.duplicate", "CTRL+D")))
            self.ks_comment.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.comment", "CTRL+/")))
            self.ks_indent.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.indent", "TAB")))
            self.ks_unindent.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.unindent", "SHIFT+TAB")))
            self.ks_auto_indent.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.auto_indent", "CTRL+SHIFT+I")))
            self.ks_find.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.find", "CTRL+F")))
            self.ks_autocomplete.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.autocomplete", "CTRL+SPACE")))
            self.ks_show_render_area.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.show_render_area", "")))
            self.ks_render.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.render", "CTRL+R")))
            self.ks_snippets.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.snippets", "F2")))
            # self.ks_updates.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.updates", "")))
            self.ks_graphDonkey.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.graphDonkey", "")))
            self.ks_graphviz.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.graphviz", "")))
            self.ks_qt.setKeySequence(QtGui.QKeySequence(self.preferences.value("ks.qt", "")))

    def apply(self):
        # GENERAL
        if True:
            self.preferences.setValue("rememberLayout", self.check_rememberLayout.isChecked())
            self.preferences.setValue("autohide", self.check_autohide.isChecked())
            if self.radio_ws_openempty.isChecked():
                self.preferences.setValue("restore", 0)
            elif self.radio_ws_restore.isChecked():
                self.preferences.setValue("restore", 1)
            else:
                self.preferences.setValue("restore", 2)
            self.preferences.setValue("recents", self.num_recents.value())
            self.preferences.setValue("encoding", self.combo_encoding.currentText())
            self.preferences.setValue("endings", self.combo_lineEndings.currentIndex())

        # EDITOR
        if True:
            self.preferences.setValue("font", self.font_editor.currentFont().family())
            self.preferences.setValue("fontsize", self.num_font.value())
            self.preferences.setValue("showLineNumbers", self.check_lineNumbers.isChecked())
            self.preferences.setValue("highlightCurrentLine", self.check_highlightLine.isChecked())
            self.preferences.setValue("syntaxHighlighting", self.check_syntax.isChecked())
            self.preferences.setValue("spacesOverTabs", self.check_spaceTabs.isChecked())
            self.preferences.setValue("parentheses", self.check_parentheses.isChecked())
            self.preferences.setValue("monospace", self.check_monospace.isChecked())
            self.preferences.setValue("tabwidth", self.num_tabwidth.value())
            self.preferences.setValue("useParser", self.check_parse.isChecked())
            self.preferences.setValue("autorender", self.check_autorender.isChecked())

        # APPEARANCE
        if True:
            self.preferences.setValue("style", self.combo_style.currentIndex())
            self.preferences.setValue("theme", self.combo_theme.currentText())
            self.preferences.setValue("col.foreground", self.col_foreground.colorName())
            self.preferences.setValue("col.window", self.col_window.colorName())
            self.preferences.setValue("col.base", self.col_base.colorName())
            self.preferences.setValue("col.alternateBase", self.col_alternateBase.colorName())
            self.preferences.setValue("col.tooltipBase", self.col_tooltipBase.colorName())
            self.preferences.setValue("col.tooltipText", self.col_tooltipText.colorName())
            self.preferences.setValue("col.text", self.col_text.colorName())
            self.preferences.setValue("col.button", self.col_button.colorName())
            self.preferences.setValue("col.buttonText", self.col_buttonText.colorName())
            self.preferences.setValue("col.brightText", self.col_brightText.colorName())
            self.preferences.setValue("col.highlight", self.col_highlight.colorName())
            self.preferences.setValue("col.link", self.col_link.colorName())
            self.preferences.setValue("col.visitedLink", self.col_visitedLink.colorName())
            self.preferences.setValue("col.cline", self.col_cline.colorName())
            self.preferences.setValue("col.lnf", self.col_lnf.colorName())
            self.preferences.setValue("col.lnb", self.col_lnb.colorName())
            self.preferences.setValue("col.clnf", self.col_clnf.colorName())
            self.preferences.setValue("col.clnb", self.col_clnb.colorName())
            self.preferences.setValue("col.find", self.col_find.colorName())
            self.preferences.setValue("col.keyword", self.col_keyword.colorName())
            self.preferences.setValue("col.attribute", self.col_attribute.colorName())
            self.preferences.setValue("col.number", self.col_number.colorName())
            self.preferences.setValue("col.string", self.col_string.colorName())
            self.preferences.setValue("col.html", self.col_html.colorName())
            self.preferences.setValue("col.comment", self.col_comment.colorName())
            self.preferences.setValue("col.hash", self.col_hash.colorName())
            self.preferences.setValue("col.error", self.col_error.colorName())

        # SHORTCUTS
        if True:
            self.preferences.setValue("ks.new", self.ks_new.keySequence().toString())
            self.preferences.setValue("ks.open", self.ks_open.keySequence().toString())
            self.preferences.setValue("ks.save", self.ks_save.keySequence().toString())
            self.preferences.setValue("ks.save_all", self.ks_save_all.keySequence().toString())
            self.preferences.setValue("ks.save_as", self.ks_save_as.keySequence().toString())
            self.preferences.setValue("ks.export", self.ks_export.keySequence().toString())
            self.preferences.setValue("ks.clear_recents", self.ks_clear_recents.keySequence().toString())
            self.preferences.setValue("ks.preferences", self.ks_preferences.keySequence().toString())
            self.preferences.setValue("ks.close_file", self.ks_close_file.keySequence().toString())
            self.preferences.setValue("ks.exit", self.ks_exit.keySequence().toString())
            self.preferences.setValue("ks.undo", self.ks_undo.keySequence().toString())
            self.preferences.setValue("ks.redo", self.ks_redo.keySequence().toString())
            self.preferences.setValue("ks.select_all", self.ks_select_all.keySequence().toString())
            self.preferences.setValue("ks.delete", self.ks_delete.keySequence().toString())
            self.preferences.setValue("ks.copy", self.ks_copy.keySequence().toString())
            self.preferences.setValue("ks.cut", self.ks_cut.keySequence().toString())
            self.preferences.setValue("ks.paste", self.ks_paste.keySequence().toString())
            self.preferences.setValue("ks.duplicate", self.ks_duplicate.keySequence().toString())
            self.preferences.setValue("ks.comment", self.ks_comment.keySequence().toString())
            self.preferences.setValue("ks.indent", self.ks_indent.keySequence().toString())
            self.preferences.setValue("ks.unindent", self.ks_unindent.keySequence().toString())
            self.preferences.setValue("ks.auto_indent", self.ks_auto_indent.keySequence().toString())
            self.preferences.setValue("ks.find", self.ks_find.keySequence().toString())
            self.preferences.setValue("ks.autocomplete", self.ks_autocomplete.keySequence().toString())
            self.preferences.setValue("ks.show_render_area", self.ks_show_render_area.keySequence().toString())
            self.preferences.setValue("ks.snippets", self.ks_snippets.keySequence().toString())
            self.preferences.setValue("ks.render", self.ks_render.keySequence().toString())
            # self.preferences.setValue("ks.updates", self.ks_updates.keySequence().toString())
            self.preferences.setValue("ks.graphDonkey", self.ks_graphDonkey.keySequence().toString())
            self.preferences.setValue("ks.graphviz", self.ks_graphviz.keySequence().toString())
            self.preferences.setValue("ks.qt", self.ks_qt.keySequence().toString())

        self.preferences.sync()
        self.applyEditor()
        self.applyStyle()
        self.applyShortcuts()

    def applyShortcuts(self):
        actions = [
            "New", "Open", "Save", "Save_As", "Save_All", "Export", "Preferences", "Close_File", "Exit",
            "Undo", "Redo", "Select_All", "Delete", "Copy", "Cut", "Paste", "Duplicate",
            "Comment", "Indent", "Unindent", "Auto_Indent", "Find", "Autocomplete",
            "Show_Render_Area", "Snippets", "Render"
        ]
        for action in actions:
            getattr(self.parent(), "action_" + action).setShortcut(getattr(self, "ks_" + action.lower()).keySequence())
        # self.parent().action_CheckUpdates.setShortcut(self.ks_updates.keySequence())
        self.parent().action_AboutGraphDonkey.setShortcut(self.ks_graphDonkey.keySequence())
        self.parent().action_AboutGraphviz.setShortcut(self.ks_graphviz.keySequence())
        self.parent().action_AboutQt.setShortcut(self.ks_qt.keySequence())

    def applyStyle(self):
        app = QtWidgets.QApplication.instance()
        app.setStyle(self.combo_style.currentText())
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.WindowText, self.col_foreground.color())
        palette.setColor(QtGui.QPalette.Window, self.col_window.color())
        palette.setColor(QtGui.QPalette.Base, self.col_base.color())
        palette.setColor(QtGui.QPalette.AlternateBase, self.col_alternateBase.color())
        palette.setColor(QtGui.QPalette.ToolTipBase, self.col_tooltipBase.color())
        palette.setColor(QtGui.QPalette.ToolTipText, self.col_tooltipText.color())
        palette.setColor(QtGui.QPalette.Text, self.col_text.color())
        palette.setColor(QtGui.QPalette.Button, self.col_button.color())
        palette.setColor(QtGui.QPalette.ButtonText, self.col_buttonText.color())
        palette.setColor(QtGui.QPalette.BrightText, self.col_brightText.color())
        palette.setColor(QtGui.QPalette.Highlight, self.col_highlight.color())
        palette.setColor(QtGui.QPalette.HighlightedText, self.col_highlightedText.color())
        palette.setColor(QtGui.QPalette.Link, self.col_link.color())
        palette.setColor(QtGui.QPalette.LinkVisited, self.col_visitedLink.color())
        app.setPalette(palette)

    def applyEditor(self):
        self.parent().files.setTabBarAutoHide(self.check_autohide.isChecked())
        editor = self.parent().editor()
        if editor is not None:
            font = QtGui.QFont()
            font.setFamily(self.font_editor.currentFont().family())
            font.setFixedPitch(self.check_monospace.isChecked())
            font.setPointSize(self.num_font.value())
            editor.setFont(font)
            fontWidth = QtGui.QFontMetrics(font).averageCharWidth()
            editor.setTabStopWidth(self.num_tabwidth.value() * fontWidth)
            editor.updateLineNumberArea(None)
            editor.highlighter.rehighlight()

            self.parent().encIndicator.setText(self.combo_lineEndings.currentText() + "  " +
                                               self.combo_encoding.currentText())

            cursor = editor.textCursor()
            seltxt = cursor.selectedText()
            cstart = cursor.selectionStart()
            cend = cursor.selectionEnd()
            cursor.setPosition(0)
            cursor.setPosition(cstart, QtGui.QTextCursor.KeepAnchor)
            before = cursor.selectedText()
            tw = self.num_tabwidth.value()
            txt = editor.toPlainText()
            if self.check_spaceTabs.isChecked():
                e = "\t"
                b4 = before.count(e) * (tw - 1)
                cstart += b4
                cend += seltxt.count(e) * (tw - 1) + b4
                txt = txt.replace(e, " " * tw)
            else:
                e = " " * tw
                b4 = before.count(e) * (tw - 1)
                cstart -= b4
                cend -= seltxt.count(e) * (tw - 1) + b4
                txt = txt.replace(e, "\t")
            editor.setText(txt)
            cursor.setPosition(cstart)
            cursor.setPosition(cend, QtGui.QTextCursor.KeepAnchor)
            editor.setTextCursor(cursor)

    def open(self):
        self.rectify()
        QtWidgets.QDialog.open(self)

    def accept(self):
        self.apply()
        QtWidgets.QDialog.accept(self)

    def restoreDefaults(self, button):
        if button.text() == "Restore Defaults":
            self.preferences.clear()
            self.preferences.sync()
            self.rectify()

    def saveTheme(self, b):
        title, ok = "", True
        while ok and title == "":
            title, ok = QtWidgets.QInputDialog.getText(self, "Enter a Theme Name", "Theme Name",
                                                       text=self.combo_theme.currentText())
            if title in [x.name for x in self.themes]:
                btn = QtWidgets.QMessageBox.question(self,
                                                     "Enter a Title Name",
                                                     "The theme '%s' already exists.\n"
                                                     "Do you want to replace it?" % title)
                if btn == QtWidgets.QMessageBox.No:
                    title = ""

        config = configparser.ConfigParser()
        config["info"] = {"name": title, "description": title + " Theme"}
        lst = self.names_general + self.names_editor + self.names_syntax
        config["styles"] = {x[4:]: getattr(self, x).colorName() for x in lst}
        with open(IOHandler.dir_styles(re.sub(r'[^a-z0-9]', "-", title.lower()) + ".ini"), "w") as f:
            config.write(f)
        self.fillQuickSelect()
        self.combo_theme.setCurrentText(title)




class ColorButton(QtWidgets.QPushButton):
    def __init__(self, color=None, parent=None):
        QtWidgets.QPushButton.__init__(self, parent)
        if color:
            self.setColor(color)
        self.clicked.connect(lambda x: self.colorPicker())

    def color(self):
        pal = self.palette()
        return pal.color(QtGui.QPalette.Button)

    def colorName(self):
        return self.color().name()

    def setColor(self, col):
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Button, col)
        pal.setColor(QtGui.QPalette.ButtonText,
                     QtGui.QColor.fromHsv(col.hue(), col.saturation(), (col.value() - 100) % 255))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.setText(col.name())

    def colorPicker(self):
        color = self.color()
        dialog = QtWidgets.QColorDialog(color, self.parent())
        dialog.setOption(QtWidgets.QColorDialog.DontUseNativeDialog)
        dialog.setCurrentColor(color)
        dialog.currentColorChanged.connect(self.setColor)
        dialog.open()


class Theme:
    def __init__(self, fname:str):
        self.file = fname
        self.config = configparser.ConfigParser()
        self.config.read(self.file)
        self.name = self.config.get("info", "name", fallback=self.file)
        self.description = self.config.get("info", "description", fallback="")

    def __lt__(self, other):
        return self.name < other.name

    def color(self, name:str="", default=None):
        return self.config.get("styles", name, fallback=default)