# Util.util_tkgrid.py
# A reusable version of my "Cards on a Desktop" for implementing self-arranging
# draggable widgets on a scrollable desktop surface. Based on Util.util_tk.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
#
# 2021.02.13 - 2021.02.24
#
# Notes:    - Initially extracted from desktop.py in Cardz project.
#           - Todo: Widgets do not need to know their position (row,col),
#               that's the Desktop's thing.
#
from tkinter import FLAT, IntVar, StringVar

from Util.globals import GRIDROWS, DESKTOPPADX, WIDGETWIDTH, WIDGETHEIGHT, GRIDCOLS, DESKTOPPADY, DESKTOPBG, AFTER
from Util.util_tk import DraggableFrame, ScrollFrame, askAtRowsOrColumns


class WidgetFrame(DraggableFrame):
    """ The draggable widget, for use by DesktopFrame class. """

    def __init__(self, parent, row, col, fg='black', bg='white', bd=0,
                 hlbg='black', hlfg='cyan'):
        super().__init__(parent.viewport, bg=bg, bd=bd, relief=FLAT,
                         highlightbackground=hlbg, highlightcolor=hlfg,
                         highlightthickness=3)
        self.parent = parent
        self.viewport = parent.viewport
        self._row = row
        self._col = col
        self.fg = fg
        self.bg = bg
        self.hlbg = hlbg
        self.hlfg = hlfg
        self.oldRow = -1
        self.oldCol = -1
        # Bind mouse and keyboard events to controls
        self.bind('<Button-3>', self.onRightClick)
        # Pass mouse scroll bindings through widget to the desktop viewport
        self.parent.bindScrollToViewport(self)

    def bindControl(self, control):
        """ Set mouse button, pass-through scrolling, and drag & drop bindings
            for each control that occupies a widget. """
        control.bind('<Button-3>', self.onRightClick)
        control.bind('<Double-Button-1>', self.onDoubleClick)
        self.bindMouseToParent(control)
        self.parent.bindScrollToViewport(control)

    def getColor(self):
        """ Return current widget color value. """
        return self.cget('bg')

    def getPosition(self):
        """ Get current position, ignoring hidden (negative) status. """
        return abs(self._row), abs(self._col)

    def hide(self):
        """ Temporarily hide a widget in the database (by setting its keys
        negative) to open that key for saving another widget when moving
        multiple widgets, to avoid duplicate key conflicts.
        To unhide:  widget.position(newRow, newCol) saves the widget at this
        new position. Never deliberately leave widgets in a hidden state. """
        # todo: this will become obsolete soon.
        self._row = -self._row
        self._col = -self._col
        self.save()

    def save(self):
        """ Override this to save the database record at key moments. """
        pass

    def setSelected(self, active=True):
        """ Set the highlight state for this widget. """
        self.config(highlightbackground=self.hlfg if active else self.hlbg)

    def setColor(self, color):
        """ Change widget color. """
        self.config(background=color)
        self.save()

    def setPosition(self, row, col):
        """  Set a new position and save. """
        self._row = row
        self._col = col
        self.save()

    # Event Handlers ..........................................................
    def onClick(self, _event):
        """ Select a single widget, making it the origin for block-selects.
            Call from overridden method, where needed. """
        self.parent.selectAll(False)
        self.parent.selectOne(self)

    def onCtrlClick(self, _event):
        """ Toggle selection of this widget randomly. """
        self.parent.selectToggle(self)

    def onDoubleClick(self, _event):
        """ Override to perform custom action for application. """
        # Stop second click from firing onClick(), which then fires onDrop()
        return "break"

    def onDrag(self, event):
        """ Possible drag, save old position. """
        self.oldRow, self.oldCol = self._row, self._col

    def onDrop(self, event):
        """ If moved, pass drop to desktop to update widget's position. """
        if self._row != self.oldRow or self._col != self.oldCol:
            self.oldRow, self.oldCol = -1, -1
            self.parent.onDrop(self, self.newX, self.newY)
            # Valid drop
            return True
        else:
            # Clean up inadvertent mini-drag
            self.parent.arrange()
            self.onClick(event)
            return False

    def onRightClick(self, event):
        """ Right-click on widget: Context menu. """
        pass

    def onShiftClick(self, _event):
        """ Block selects widgets, if an origin has been set. """
        self.parent.selectBlock(self)


class DesktopFrame(ScrollFrame):
    """ A frame that automagically aligns widget-like widgets in rows and columns.
        NOTE: Must place widgets on self.viewport, not self. """

    def __init__(self, parent, parentFrame, **kw):
        super().__init__(parentFrame, **kw)
        self.parent = parent
        self.gridRows = GRIDROWS
        self.gridCols = GRIDCOLS
        self.widgetH = WIDGETHEIGHT
        self.widgetW = WIDGETWIDTH
        self.marginX = DESKTOPPADX
        self.marginY = DESKTOPPADY
        self.bgColor = DESKTOPBG
        self.bgImage = None
        self.widgets = {}
        self.selections = Selection(self)
        # Display an empty grid space on viewport
        self.arrange()
        # Bind mouseclick events
        self.viewport.bind('<Button-1>', self.onClick)
        self.viewport.bind('<Double-Button-1>', self.onDoubleClick)
        self.viewport.bind('<Button-3>', self.onRightClick)
        # self.bind('<Alt-Key>', self.parent.onAltKey)

    def addColumns(self, atCol=None):
        """ Insert a new column at this column, or after the last (-1) column """
        cols = IntVar()
        side = StringVar()
        if askAtRowsOrColumns(self.viewport, 'Insert Column(s)',
                              colVar=cols, sideVar=side):
            # Adjust column insertion point
            if not atCol:
                atCol = self.gridCols + 1
            elif side.get() == AFTER:
                atCol += 1
            # Bump up the max desktop columns and save
            self.gridCols += cols.get()
            self.save()
            # Shift widgets to make space, if necessary, and save changes
            self.selectRange(left=atCol, hilight=False)
            self.move(cols=cols.get())

    def addRows(self, atRow=None):
        """ Insert a new row at this row, or after the last row (default). """
        rows = IntVar()
        side = StringVar()
        if askAtRowsOrColumns(self.viewport, 'Insert Row(s)',
                              rowVar=rows, sideVar=side):
            # Adjust row to insert new rows
            if not atRow:
                atRow = self.gridRows + 1
            elif side.get() == AFTER:
                atRow += 1
            # Bump up the max rows and save
            self.gridRows += rows.get()
            self.save()
            # Shift widgets to make space, if necessary and save changes
            self.selectRange(top=atRow, hilight=False)
            self.move(rows=rows.get())

    def arrange(self):
        """ Arrange and resize widgets and canvas viewport. """
        # Resize the viewport
        h, w = self.viewSize()
        self.viewport.config(height=h, width=w, bg=self.bgColor)
        # Place each widget where it belongs
        for key, widget in self.widgets.items():
            x, y = self.viewPosition(*widget.getPosition())
            widget.place(x=x, y=y, height=self.widgetH, width=self.widgetW)

    def clear(self):
        """ Clears widgets from desktop, without deleting from their database. """
        for widget in self.widgets.values():
            # Unplace and delete each widget widget
            widget.place_forget()
            del widget
        # Clear the list
        self.widgets.clear()

    def getWidgetAt(self, row, col):
        """ Return the widget at this position, if one exists there. """
        return self.widgets.get(self.key(row, col))

    def gridPosition(self, x, y):
        """ Convert viewport x,y coordinates to widget position. """
        col = x // (self.widgetW + self.marginX)
        row = y // (self.widgetH + self.marginY)
        return row, col

    @staticmethod
    def key(row, col):
        """ Return a dictionary key based on this position "RRR:CCC" """
        return "{:03d}:{:03d}".format(row, col)

    def move(self, rows=0, cols=0):
        """ Move selected widgets to a new location. """
        # Todo: Check destination is clear (and deal with it)
        # Cut affected widgets from desktop/database
        for widget in self.selections.items:
            self.removeWidget(widget)
            widget.hide()
        # Paste each widget at new position
        for widget in self.selections.items:
            row, col = widget.getPosition()
            widget.setPosition(row + rows, col + cols)
            self.putWidget(widget)
        # Redraw all widgets in new places and clear selections
        self.arrange()
        self.selectAll(False)

    def popWidget(self, row, col):
        """ Remove widget from widget collection and return it. """
        key = self.key(row, col)
        widget = self.widgets[key]
        del self.widgets[key]
        return widget

    def putWidget(self, widget):
        """ Add widget to the widget collection. """
        key = self.key(*widget.getPosition())
        self.widgets[key] = widget

    def removeWidget(self, widget):
        """ Remove a widget from the desktop collection. """
        key = self.key(*widget.getPosition())
        del self.widgets[key]

    def resizeWidgets(self, height, width):
        """ Scale size of all widgets and refresh the grid. """
        self.widgetH = height
        self.widgetW = width
        self.arrange()
        self.save()

    def save(self):
        """ Override to save on changes to Desktop subclass. """
        pass

    def selectAll(self, active=True):
        """ Select or unselect all widgets, hilighting accordingly. """
        self.selections.clear()
        for widget in self.widgets.values():
            if active:
                self.selections.add(widget)
            widget.setSelected(active)
        self.selectState(active)

    def selectBlock(self, widget):
        """ Select a range from origin widget to this one (Shift-Click). """
        if self.selections.getOrigin():
            # Select all widgets in a box from the origin to this widget
            top, left = self.selections.origin.getPosition()
            bottom, right = widget.getPosition()
            self.selectRange(top, left, bottom, right)
        else:
            # No origin selected; make this the origin
            self.selectOne(widget)
        self.selectState(self.selections.count() > 0)

    def selectOne(self, widget):
        """ Select a widget and hilight it (Click). """
        self.selections.add(widget)
        widget.setSelected(True)
        widget.focus_set()
        self.selectState(True)

    def selectRange(self, top=0, left=0, bottom=None, right=None, hilight=True):
        """ Select a group of widgets in a rectangular area and hilight them. """
        self.selections.clear()
        # Ensure selection box is right-side-up
        if bottom and bottom < top:
            top, bottom = bottom, top
        if right and right < left:
            left, right = right, left
        # Assume full extent of desktop, if missing
        bottom = self.gridRows if not bottom else bottom
        right = self.gridCols if not right else right
        # Select widgets that fall in this rectangle
        for widget in self.widgets.values():
            row, col = widget.getPosition()
            if left <= col <= right and top <= row <= bottom:
                self.selections.add(widget)
                # Hilight widget, if not a background operation (eg, insert row)
                widget.setSelected(hilight)
            else:
                widget.setSelected(False)
        # Abort editing one single widget; show colorbar
        self.focus_set()
        self.selectState(self.selections.count() > 0)

    def selectState(self, active):
        """ Override in subclass to get updates on the selection state. """
        pass

    def selectToggle(self, widget):
        """ Toggles the selection of a widget (Ctrl-Click). """
        if self.selections.contains(widget):
            self.selections.remove(widget)
            widget.setSelected(False)
        else:
            self.selections.add(widget)
            widget.setSelected(True)
        self.selectState(self.selections.count() > 0)

    def setColor(self, color):
        """ Set all selected widgets to this color. """
        for widget in self.selections.items:
            widget.setColor(color)

    def setBackground(self, color, image=None):
        """ Set desktop background to a color or image. """
        self.bgColor = color
        self.bgImage = image

    def setGridSize(self, rows, cols):
        """ Set the number of rows and columns to display on the desktop. """
        self.gridRows = rows
        self.gridCols = cols

    def setMarginSize(self, x, y):
        """ Set between-widget margin sizes; x = to left, y = above. """
        self.marginX = x
        self.marginY = y

    def setWidgetSize(self, height, width):
        """ Set the size of widgets occupying the desktop. """
        self.widgetH = height
        self.widgetW = width

    def viewPosition(self, row, col):
        """ Return viewport coords based on grid position. """
        x = col * (self.widgetW + self.marginX)
        y = row * (self.widgetH + self.marginY)
        return x, y

    def viewSize(self):
        """ Calculate viewport size from rows, cols and and widget sizes. """
        h = (self.gridRows * (self.widgetH + self.marginY)) + self.marginY
        w = (self.gridCols * (self.widgetW + self.marginX)) + self.marginX
        return h, w

    # Event handlers ..........................................................
    def onClick(self, _event):
        """ Left-click on Desktop surface, clearing any widget selections. """
        self.selectAll(False)
        self.focus_set()

    def onDoubleClick(self, _event):
        """ Override for custom functionality. """
        pass

    def onDrop(self, widget, x, y):
        """ Called from DraggableFrame upon dropping a dragged child widget. """
        # Todo: New code to determine drop-on-margin-or-widget goes here
        row, col = self.gridPosition(x, y)
        found = self.getWidgetAt(row, col)
        if found:
            if found != widget:
                # Another widget exists there. TODO: Ask user what to do now
                pass
        else:  # All clear, drop it here
            self.move(row, col)

    def onRightClick(self, _event):
        """ Override for custom functionality. """
        pass


class Selection:
    """ Holds selected widgets pending some operation, like moving,
    deleting, updating or other batch operations, while keeping track of
    position stats to check for collisions. """

    def __init__(self, parent):
        self.parent = parent
        self.items = []
        self.originWidget = None
        self.top = None
        self.left = None
        self.bottom = None
        self.right = None
        self.dragFrame = None

    def add(self, widget):
        """ Add a widget to the list and update bounding box stats. """
        if not self.items.__contains__(widget):
            self.items.append(widget)
        self._setExtents()

    def clear(self):
        """ Clear the selection buffer when done for reuse. """
        self.items.clear()
        self.originWidget = None
        self.top = None
        self.left = None
        self.bottom = None
        self.right = None
        self._setExtents()

    def contains(self, widget):
        """ Indicate if the widget is selected. """
        return self.items.__contains__(widget)

    def count(self):
        """ Returns number of widgets currently selected. """
        return len(self.items)

    def getExtents(self):
        """ Return extent in t,l,b,r form. """
        return self.top, self.left, self.bottom, self.right

    def getOrigin(self):
        return self.originWidget

    def remove(self, widget):
        """ Remove a widget from the list, if it is there. """
        if self.items.__contains__(widget):
            self.items.remove(widget)
        self._setExtents()

    def _setExtents(self):
        """ Keep track of extents to check for position collisions on moves. """
        self.origin = None
        for widget in self.items:
            row, col = widget.getPosition()
            if not self.left or col < self.left:
                self.left = col
            if not self.right or col > self.right:
                self.right = col
            if not self.top or row < self.top:
                self.top = row
            if not self.bottom or row > self.bottom:
                self.bottom = row
            # Set the selection origin to the top-left-most widget
            if row == self.top and col == self.left:
                self.originWidget = widget
