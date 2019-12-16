"""The code editor of GraphDonkey, with a few features:

- Syntax Highlighting
- Line Numbers
    Based on https://stackoverflow.com/questions/2443358/how-to-add-lines-numbers-to-qtextedit

Author: Randy Paredis
Date:   12/14/2019
"""
from PyQt5 import QtGui, QtWidgets, QtCore
from main.extra import Constants, Config

class CodeEditor(QtWidgets.QTextEdit):
    def __init__(self, parent):
        super(CodeEditor, self).__init__(parent)
        self.lineNumberArea = LineNumberArea(self)

        fontWidth = QtGui.QFontMetrics(self.currentCharFormat().font()).averageCharWidth()
        self.setTabStopWidth(4 * fontWidth)

        self.document().blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.verticalScrollBar().valueChanged.connect(self.updateLineNumberAreaScroll)
        self.textChanged.connect(self.updateLineNumberAreaText)
        self.cursorPositionChanged.connect(self.updateLineNumberAreaText)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        self.highlighter = Highlighter(self.document())

    def event(self, event: QtCore.QEvent):
        if event.type() == QtCore.QEvent.ShortcutOverride:
            return False
        return QtWidgets.QTextEdit.event(self, event)

    def insertFromMimeData(self, QMimeData):
        self.insertPlainText(QMimeData.text())

    def highlightCurrentLine(self):
        selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            selection.format.setBackground(Config.STX_CLINE_COLOR)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)

        self.setExtraSelections(selections)

    def getFirstVisibleBlockId(self):
        curs = QtGui.QTextCursor(self.document())
        curs.movePosition(QtGui.QTextCursor.Start)
        for i in range(self.document().blockCount()):
            block = curs.block()
            r1 = self.viewport().geometry()
            r2 = self.document().documentLayout().blockBoundingRect(block).\
                translated(self.viewport().geometry().x(),
                           self.viewport().geometry().y() - self.verticalScrollBar().sliderPosition()).toRect()

            if r1.contains(r2, True): return i

            curs.movePosition(QtGui.QTextCursor.NextBlock)
        return 0

    def lineNumberAreaPaintEvent(self, event):
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().sliderPosition())
        painter = QtGui.QPainter(self.lineNumberArea)
        blockNumber = self.getFirstVisibleBlockId()

        block = self.document().findBlockByNumber(blockNumber)
        prev_block = self.document().findBlockByNumber(blockNumber - 1) if blockNumber > 0 else block
        translate_y = -self.verticalScrollBar().sliderPosition() if blockNumber > 0 else 0

        top = self.viewport().geometry().top()
        if blockNumber == 0:
            additionalMargin = self.document().documentMargin() - 1 - self.verticalScrollBar().sliderPosition()
        else:
            additionalMargin = self.document().documentLayout().blockBoundingRect(prev_block). \
                translated(0, translate_y).intersect(self.viewport().geometry()).height()

        top += additionalMargin

        bottom = top + self.document().documentLayout().blockBoundingRect(block).height()

        col_1 = Config.STX_CLNUM_COLOR
        col_0 = Config.STX_OLNUM_COLOR

        old = block, top, bottom, blockNumber

        painter.fillRect(event.rect(), Config.STX_OLNUM_BCOLOR)
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top() and self.textCursor().blockNumber() == blockNumber:
                painter.fillRect(QtCore.QRect(event.rect().x(), top, event.rect().width(), self.fontMetrics().height()),
                                 Config.STX_CLNUM_BCOLOR)
            block = block.next()
            top = bottom
            bottom = top + self.document().documentLayout().blockBoundingRect(block).height()
            blockNumber += 1

        block, top, bottom, blockNumber = old
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(col_1 if self.textCursor().blockNumber() == blockNumber else col_0)
                painter.drawText(-5, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.document().documentLayout().blockBoundingRect(block).height()
            blockNumber += 1

    def lineNumberAreaWidth(self):
        digits = 1
        _max = max(1, self.document().blockCount())
        while _max >= 10:
            _max /= 10
            digits += 1

        return 13 + self.fontMetrics().width('9') * digits

    def resizeEvent(self, event):
        QtWidgets.QTextEdit.resizeEvent(self, event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect):
        self.updateLineNumberAreaText()

    def updateLineNumberAreaScroll(self, dy):
        self.updateLineNumberAreaText()

    def updateLineNumberAreaText(self):
        self.highlightCurrentLine()
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().sliderPosition())

        rect = self.contentsRect()
        self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        self.updateLineNumberAreaWidth(0)

        dy = self.verticalScrollBar().sliderPosition()
        if dy > -1:
            self.lineNumberArea.scroll(0, dy)

        first_block_id = self.getFirstVisibleBlockId()
        if first_block_id == 0 or self.textCursor().block().blockNumber() == first_block_id - 1:
            self.verticalScrollBar().setSliderPosition(dy - self.document().documentMargin())


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)
        self.highlightingRules = []
        self.multiLineCommentFormat = None
        self.commentStartExpression = None
        self.commentEndExpression = None
        self.setPatterns()

    def setPatterns(self):
        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(Config.STX_KEYWORD_COLOR)
        keywordFormat.setFontWeight(QtGui.QFont.Bold)

        keywordPatterns = ["\\b%s\\b" % x for x in Constants.STRICT_KEYWORDS ]
        self.highlightingRules = [(QtCore.QRegExp(pattern), keywordFormat) for pattern in keywordPatterns]

        attributeFormat = QtGui.QTextCharFormat()
        attributeFormat.setForeground(Config.STX_ATTRIBUTE_COLOR)
        attributeFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightingRules.append((QtCore.QRegExp("(%s)(?=\\s*[=])" % "|".join(Constants.ATTRIBUTES)), attributeFormat))
        for a in Constants.SPECIAL_ATTRIBUTES:
            self.highlightingRules.append((QtCore.QRegExp("\\b%s\\b" % a), attributeFormat))

        hashCommentFormat = QtGui.QTextCharFormat()
        hashCommentFormat.setForeground(Config.STX_COMMENT_COLOR)
        self.highlightingRules.append((QtCore.QRegExp("^#[^\n]*$"), hashCommentFormat))

        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(Config.STX_COMMENT_COLOR)
        self.highlightingRules.append((QtCore.QRegExp("//[^\n]*"), singleLineCommentFormat))

        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        self.multiLineCommentFormat.setForeground(Config.STX_COMMENT_COLOR)
        self.commentStartExpression = QtCore.QRegExp("/\\*")
        self.commentEndExpression = QtCore.QRegExp("\\*/")

        numberFormat = QtGui.QTextCharFormat()
        numberFormat.setForeground(Config.STX_NUMBER_COLOR)
        self.highlightingRules.append((QtCore.QRegExp("\\b-?(\\.[0-9]+|[0-9]+(\\.[0-9]*)?)\\b"), numberFormat))

        quotedStringFormat = QtGui.QTextCharFormat()
        quotedStringFormat.setForeground(Config.STX_STRING_COLOR)
        self.highlightingRules.append((QtCore.QRegExp("\".*\""), quotedStringFormat))

        htmlStringFormat = QtGui.QTextCharFormat()
        htmlStringFormat.setForeground(Config.STX_STRING_COLOR)
        self.highlightingRules.append((QtCore.QRegExp("<.*>"), htmlStringFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

            self.setFormat(startIndex, commentLength,
                    self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text,
                    startIndex + commentLength)


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, QPaintEvent):
        self.editor.lineNumberAreaPaintEvent(QPaintEvent)