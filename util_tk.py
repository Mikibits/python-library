# Util.util_tk.py
# Handy reusable things of the Tkinter variety.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
#
# 2020.05.23 - 2020.06.22
#
# Notes:
#   - The Dialog class code was borrowed from an awesome example on
#     effbot.org and evolved for my use (I cannot take credit for most of it).

from tkinter import Frame, TOP, Button, BOTTOM, Toplevel, PhotoImage, Label, \
    Radiobutton, Spinbox, FLAT
from tkinter import HORIZONTAL, RIGHT, INSERT, NORMAL, DISABLED, END, SEL, Text
from tkinter import Y, SUNKEN, LEFT, ACTIVE, Canvas, Scrollbar, VERTICAL, \
    BOTH, NW
from tkinter.filedialog import askopenfilename, asksaveasfile

from Util.globals import *


# Class wrappers ..............................................................
def askAtRowsOrColumns(parent, title, rowVar=None, colVar=None, sideVar=None):
    """ Common dialog to query user about rows, columns, and which side
        (BEFORE|AFTER) is desired. It only asks about a particular item
        when an instance variable has been passed for that item.
        Parameters:  rowVar: IntVar(), colVar: IntVar(), sideVar: StringVar().
        Returns: True if OK button clicked, False if Cancel clicked. """
    dlg = ModalDialog(parent, title)
    # rows
    if rowVar:
        rowVar.set(1)
        box1 = Frame(dlg.body, pady=5)
        box1.pack(side=TOP)
        lbl1 = Label(box1, text='# of rows')
        lbl1.pack(side=LEFT)
        spin1 = Spinbox(box1, width=3, textvariable=rowVar, from_=0, to=10)
        spin1.pack(side=RIGHT)
    # columns
    if colVar:
        colVar.set(1)
        box2 = Frame(dlg.body, pady=5)
        box2.pack(side=TOP)
        lbl2 = Label(box2, text='# of columns')
        lbl2.pack(side=LEFT)
        spin2 = Spinbox(box2, width=3, textvariable=colVar, from_=0, to=10)
        spin2.pack(side=RIGHT)
    # side (before/after)
    if sideVar:
        sideVar.set(BEFORE)
        box3 = Frame(dlg.body, pady=5)
        box3.pack(side=TOP)
        rb1 = Radiobutton(box3, text="Before", variable=sideVar, value=BEFORE)
        rb1.pack(side=LEFT)
        rb2 = Radiobutton(box3, text="After", variable=sideVar, value=AFTER)
        rb2.pack(side=RIGHT)
    # Display the dialog, return OK clicked status
    dlg.showModal()
    return dlg.okClicked


def askButtonSelect(parent, title, selections, **kw):
    """ Simple wrapper for ButtonSelectDialog class that returns the
        selected value without needing to pass a callback function. """
    # Create the dialog and add buttons
    dlg = ButtonSelectDialog(parent, title, **kw)
    for item in selections:
        if not item == 'None':
            dlg.addButton(item)
    # Display and return selection
    dlg.showModal()
    return dlg.result


def askInitialProject(parent, recent, fileType, cwd='./', **kw):
    """ If the application requires a project to be open or created from the start,
        this selects an existing or recent file, or creates a new one.
        recent:     from util_config.recentFiles,
        fileType:   list, description and type, e.g.: ("Cardz File", "*.cdz"),
        current:    current path,
        cwd:        last path. """
    # Select from recent files, with New or Open options
    choices = recent.copy()
    choices.append(OPENPROJECT)
    choices.append(NEWPROJECT)
    selection = askRecentProject(parent, choices, **kw)
    # If user cancels, assume new project
    if not selection:
        selection = NEWPROJECT
    # Open or create a new project
    if selection == OPENPROJECT:
        selection = askOpenProject(cwd, fileType)
    elif selection == NEWPROJECT:
        selection = askNewProject(cwd, fileType)
    return selection


def askNewProject(fileType, cwd='./'):
    """ Prompt for a path/file to create a new project. """
    title = 'Choose a name and location for this project'
    ftype = (fileType, ("All Files", "*.*"))
    path = asksaveasfile(initialdir=cwd, filetypes=ftype, title=title).name
    return path


def askOpenMarkdown(cwd='./'):
    """ Open an existing project file. """
    title = 'Choose a project'
    ftype = (("Markdown Files", "*.md"), ("All Files", "*.*"))
    path = askopenfilename(initialdir=cwd, filetypes=ftype, title=title)
    return path


def askOpenProject(fileType, cwd='./'):
    """ Open an existing project file. """
    title = 'Choose a project'
    ftype = (fileType, ("All Files", "*.*"))
    path = askopenfilename(initialdir=cwd, filetypes=ftype, title=title)
    return path


def askRecentProject(parent, choices, **kw):
    """ Prompt for a selection from the recent file list. """
    title = 'Select a project'
    if len(choices) < 1:
        return None
    path = askButtonSelect(parent, title, choices, **kw)
    return path


def askSaveMarkdown(cwd='./'):
    """ Prompt for filepath to save a markdown file. """
    title = 'Choose a name and location for this project'
    ftype = (("Markdown Files", "*.md"), ("All Files", "*.*"))
    path = asksaveasfile(initialdir=cwd, filetypes=ftype, title=title).name
    return path


# Classes .....................................................................
class AboutDialog(Toplevel):
    """ An application About box with a standard look & feel. """

    def __init__(self, parent, appName, title, gifStr, version, copy, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.transient(parent)
        self.title('About ' + appName)
        self.img = None
        bg = Frame(self, padx=10, pady=10)
        bg.pack(side=TOP, fill=BOTH, expand=True)
        # Icon-Title banner
        hBox = Frame(bg, padx=5, pady=5)
        hBox.pack(side=TOP, anchor=NW)
        # Display a large icon
        self.img = PhotoImage(data=gifStr)
        imgLbl = Label(hBox, image=self.img, width=64, height=64,
                       bg='#99bb99')
        imgLbl.pack(side=LEFT)
        # Application name and version number
        rBox = Frame(hBox, padx=15, pady=5)
        rBox.pack(side=RIGHT)
        # Name
        appLbl = Label(rBox, text=appName, font=("Georgia", 18), pady=5)
        appLbl.pack(side=TOP, anchor=NW)
        # Version
        versLbl = Label(rBox, text='version ' + version)
        versLbl.pack(side=TOP, anchor=NW)
        # Middle box
        mBox = Frame(bg, padx=5, pady=5)
        mBox.pack(side=TOP)
        # Application title/description
        titleLbl = Label(mBox, text=title, font=("Georgia", 14))
        titleLbl.pack(side=TOP)
        # Copyright information
        copyLbl = Label(mBox, text=copy, font=("Arial", 10), pady=5)
        copyLbl.pack(side=TOP)
        # Buttons
        bBox = Frame(bg, pady=5)
        bBox.pack(side=BOTTOM)
        # An okay key, to leave
        okBtn = Button(bBox, text='Okay', command=self.onClose)
        okBtn.pack()
        # Leave if the user clicks outside
        self.bind("<FocusOut>", self.onClose)

    def showModal(self):
        # Make modal and set initial focused body-widget
        self.grab_set()
        # Handle dialog-closing event
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.focus_set()
        self.wait_window(self)

    def onClose(self, _event=None):
        """ Handle Cancel button clikc (or Escape key). """
        # Place focus back to the parent and quit
        self.parent.focus_set()
        self.destroy()


class ButtonSelectDialog(Toplevel):
    """ Selection dialog providing a column of buttons. """

    def __init__(self, parent, title, btnFg='white', btnBg='darkgray'):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent  # redundant?
        self.result = None
        self.buttons = list()
        self.buttonBg = btnBg
        self.buttonFg = btnFg
        self.body = Frame(self, bg=self.cget('bg'), padx=10, pady=15,
                          relief=SUNKEN)
        self.body.pack(padx=5, pady=5)

    def addButton(self, text):
        btn = Button(self.body, text=text, width=60, padx=10, pady=8,
                     command=lambda: self.onSelect(text),
                     relief=FLAT, bd=3, highlightthickness=0,
                     bg=self.buttonBg, fg=self.buttonFg)
        self.buttons.append(btn)
        btn.pack(side=TOP, padx=10, pady=2, expand=Y)
        # Focus on first
        if len(self.buttons) == 1:
            btn.focus_set()

    def showModal(self):
        # Make modal and set initial focus
        self.grab_set()
        # Handle dialog-closing event
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        # Take focus and attention away from main app for a bit
        self.wait_window(self)

    # Event handlers ..........................................................
    def onClose(self):
        """ Handle Cancel button click (or Escape key). """
        self.destroy()

    def onSelect(self, selection):
        """ Selection made, callback with value. """
        self.result = selection
        self.destroy()


class ModalDialog(Toplevel):
    """ A customizable modal dialog box with built in OK and Cancel buttons. """

    def __init__(self, parent, title='Choose', **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.transient(parent)
        self.title(title)
        self.okClicked = False
        self.body = Frame(self, relief=SUNKEN)
        self.body.pack(padx=5, pady=5)
        # Initialize default buttons
        box = Frame(self)
        box.pack()
        okBtn = Button(box, text="OK", width=10, command=self.onOk,
                       default=ACTIVE)
        okBtn.pack(side=LEFT, padx=5, pady=5)
        cancelBtn = Button(box, text="Cancel", width=10, command=self.onCancel)
        cancelBtn.pack(side=LEFT, padx=5, pady=5)
        # Bind Enter -> OK, Esc -> Cancel buttons
        self.bind("<Return>", self.onOk)
        self.bind("<Escape>", self.onCancel)

    def showModal(self):
        """ Make dialog modal pause for user input """
        self.grab_set()
        # Capture window close as a Cancel
        self.protocol("WM_DELETE_WINDOW", self.onCancel)
        self.wait_window(self)

    # Event handlers ..........................................................
    def onOk(self):
        """ Handle OK button-click (or Enter key). """
        self.okClicked = True
        # Clean up and close dialog
        self.withdraw()
        self.update_idletasks()
        self.onCancel()

    def onCancel(self):
        """ Handle Cancel button clikc (or Escape key). """
        self.parent.focus_set()
        self.destroy()


class DraggableFrame(Frame):
    """ A frame with built-in drag and drop functionality. """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.widget = None
        self.startX = 0
        self.startY = 0
        self.newX = 0
        self.newY = 0
        self.dropEvent = None
        self.dragInProgess = False
        self.clickSpecial = False
        # Bind mouseclick events
        self.bind('<Button-1>', self.onDragStart)
        self.bind('<B1-Motion>', self.onDragMotion)
        self.bind('<ButtonRelease-1>', self.onDrop)

    def bindMouseToParent(self, widget):
        """ Allows drag motion to 'pass-thru' a widget to its parent. """
        self.widget = widget
        widget.bind('<Double-Button-1>', self.onDoubleClick)
        widget.bind('<Button-1>', self.onDragStart)
        widget.bind('<B1-Motion>', self.onDragMotion)
        widget.bind('<ButtonRelease-1>', self.onDragStop)
        widget.bind('<Shift-Button-1>', self.onShiftClickStart)
        widget.bind('<Control-Button-1>', self.onCtrlClickStart)

    def dragPosition(self, event):
        """ Calculate relative drag position on parent. """
        self.newX = self.winfo_x() - self.startX + event.x
        self.newY = self.winfo_y() - self.startY + event.y

    def onClick(self, event):
        """ Override this in subclass to handle click event. """
        pass

    def onCtrlClick(self, event):
        """ Override this in subclass to handle Ctrl-click event. """
        pass

    def onCtrlClickStart(self, event):
        """ Gets ready to handle a Ctrl-click event. """
        self.clickSpecial = True
        self.onCtrlClick(event)

    def onDoubleClick(self, event):
        """ Override this for double-click that skips drag&drop process. """
        pass

    def onDrag(self, event):
        """ Override this to know when drag begins. """
        pass

    def onDragMotion(self, event):
        """ Mouse is dragging this frame, begin drag operation. """
        if not self.clickSpecial:
            self.dragInProgess = True
            # Move item with mouse
            self.dragPosition(event)
            self.place(x=self.newX, y=self.newY)

    def onDragStart(self, event):
        """ Mouse button-down, save start location. """
        self.clickSpecial = False
        self.startX = event.x
        self.startY = event.y
        # Ensure it floats "over" the others
        self.tkraise()
        # Let object know
        self.onDrag(event)

    def onDragStop(self, event):
        """ Mouse released, drop here (if drag occured). """
        if self.dragInProgess:
            self.newX += self.startX
            self.newY += self.startY
            # Call overloaded drop method, to handle its own drop
            self.onDrop(event)
            self.dragInProgess = False
            # self.focus()
        else:
            # Normal click check
            if not self.clickSpecial:
                self.onClick(event)

    def onDrop(self, event):
        """ Override in subclass to handle drop event. """
        pass

    def onShiftClick(self, event):
        """ Override in subclass to handle Shift-Click event. """
        pass

    def onShiftClickStart(self, event):
        """ Get ready to handle Shift-Click event. """
        self.clickSpecial = True
        self.onShiftClick(event)


class ScrollFrame(Frame):
    """ Scrollable Frame Class with Viewport (REUSABLE)
        Note: Place widgets on (ScrollFrame).viewport """

    def __init__(self, parent, bg='black', **kw):
        super().__init__(parent, bg=bg, **kw)
        # Place canvas on frame (self) and viewport on canvas
        self.canvas = Canvas(self, borderwidth=10, bg=bg, highlightthickness=0)
        self.viewport = Frame(self.canvas, highlightthickness=0)
        self.widget = None
        # Create and attach scrollbars
        self.scrollV = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.scrollH = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scrollV.set)
        self.canvas.configure(xscrollcommand=self.scrollH.set)
        # Pack canvas and scrollbars to appropriate sides
        self.scrollV.pack(side=RIGHT, fill="y")
        self.scrollH.pack(side=BOTTOM, fill='both')
        self.canvas.pack(side=LEFT, fill="both", expand=True)
        # Add viewport frame to window  (??)
        self.canvasWin = self.canvas.create_window((4, 4), window=self.viewport,
                                                   anchor="nw", tags="self.viewPort")
        # bind viewport and canvas resize events
        self.viewport.bind("<Configure>", self.onViewportResize)
        self.canvas.bind("<Configure>", self.onCanvasResize)
        # Bind mousewheel to scroll only when over viewport
        self.canvas.bind('<Enter>', self.onCanvasEntered)
        self.canvas.bind('<Leave>', self.onCanvasLeft)
        # Initial resize
        self.onViewportResize(None)

    def bindScrollToViewport(self, widget):
        """ Passes mouse scrolling through widgets to the viewport. """
        self.widget = widget
        # For Linux
        widget.bind('<Button-4>', self.onMouseWheel)
        widget.bind('<Button-5>', self.onMouseWheel)
        # For Windows
        widget.bind("<MouseWheel>", self.onMouseWheel)

    def onCanvasEntered(self, _event):
        """ Bind mousewheel to scroll when mouse is over canvas. """
        # For Linux
        self.viewport.bind('<Button-4>', self.onMouseWheel)
        self.viewport.bind('<Button-5>', self.onMouseWheel)
        # For Windows
        self.viewport.bind("<MouseWheel>", self.onMouseWheel)

    def onCanvasLeft(self, _event):
        """ Unbind mousewheel when mouse leaves canvas. """
        # For Linux
        self.viewport.unbind("<Button-4>")
        self.viewport.unbind("<Button-5>")
        # For Windows
        self.viewport.unbind("<MouseWheel>")

    def onCanvasResize(self, event):
        """ Reset the canvas window to encompass inner frame when required. """
        self.canvas.itemconfig(self.canvasWin, width=event.width)

    def onDrop(self, widget, x, y):
        """ Override in subclass to handle drop event (see DraggableFrame). """
        pass

    def onMouseWheel(self, event):
        """ Scroll canvas vertically with mousewheel. """
        # For Linux (event.num) and Windows (event.delta)
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")

    def onViewportResize(self, _event):
        """ Reset the scroll region to encompass the inner frame. """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class TextBox(Text):
    """ Somewhat smarter text field with common tasks simplified and
        knows when its data has changed. """

    def __init__(self, parent, text, leaveCallback, changeCallback,
                 multiline=False, tabNext=False, **kw):
        super().__init__(parent, **kw)
        self.parent = parent
        self.oldValue = text
        self.leaveCallback = leaveCallback
        self.changeCallback = changeCallback
        self.multiline = multiline
        self.tabNext = tabNext
        # Display initial text
        self.insert(INSERT, text)
        if not multiline:
            self.bind("<Return>", self.onTab)
        self.bind("<FocusOut>", self.onLeaving)
        self.bind("<Tab>", self.onTab)

    def activate(self, active=True):
        """ Set text field as editable, or not. """
        self.config(state=NORMAL if active else DISABLED)

    def get(self, start='1.0', end=END):
        """ Get all of the text in the field (simplified wrapper). """
        text = super().get(start, end)
        return text.rstrip('\n')

    def inputOver(self):
        """ Select current contents and let user type over it. """
        self.tag_add(SEL, "1.0", END)
        self.mark_set(INSERT, "1.0")
        self.see(INSERT)
        self.focus_set()

        return "break"

    def set(self, text=''):
        """ Set all the text in the field to this value. """
        self.delete('1.0', END)
        self.insert(INSERT, text)
        self.oldValue = text

    def unselect(self):
        """ Clear any selections in field. """
        self.tag_remove(SEL, "1.0", END)

    # Event Handlers ..........................................................
    def onLeaving(self, event):
        """ Leaving field: use callback if data was modified. """
        # Call leave callback
        self.leaveCallback(event)
        # Call modified callback if contents changed
        newValue = self.get()
        if not newValue == self.oldValue:
            self.changeCallback(event)
            self.oldValue = newValue
        # Unselect text
        self.unselect()

    def onTab(self, event):
        """ Navigate to the next field, if any, instead of changing text. """
        if self.tabNext:
            event.widget.tk_focusNext().focus()
        else:
            self.parent.focus()
        # Stop input from reaching text field
        return "break"
