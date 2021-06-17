# util.py
# Handy reusable things: general stuff.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
# 2020.05.23 - 2020.06.07
#
# Notes:
import os
from threading import Timer


# Numbers .....................................................................
def even(n):
    return n % 2 == 0


def odd(n):
    return not even(n)


# Files .......................................................................
def getFilePathInfo(absolute):
    """ Break an absolute path into it's components. """
    dirname = os.path.dirname(absolute)
    basename = os.path.basename(absolute)
    info = os.path.splitext(basename)
    filename = info[0]
    extension = info[1]
    return dirname, filename, extension


def writeLine(file, *items):
    """ Wrapper to simplify adding newlines while writing to files. """
    line = ''
    for item in items:
        line += item
    line += os.linesep
    file.write(line)


# Strings .....................................................................
def prettyPath(path):
    """ Convert a project path into a title-worthy 'file.ext (path)' string. """
    title = ''
    if path:
        folder, file, ext = getFilePathInfo(path)
        title = file + ext + '  (' + folder + ')'
    return title


# Classes .....................................................................

class PollTimer(object):
    """ Repeating timer that calls a function every <interval> minutes.
    Usage:
        # Start an auto-save timer
        self.saveTimer = PollTimer(self.saveInterval, self.onSaveTimer)
        self.saveTimer.start()
        ...
        def onSaveTimer(self):
            ''' Tell desktop to save any changed cards. '''
            self.desktop.save()
    """

    def __init__(self, interval, func, *args, **kwargs):
        self.interval = interval * 60
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.timer = None

    def callback(self):
        """ Call the callback function, then restart the timer. """
        self.func(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        """ Shut down the poll timer. """
        self.timer.cancel()

    def start(self):
        """ Start the poll timer. """
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()


class Singleton:
    """ Modelled after Alex Martelli's 'Borg' faux-singleton class, which is
        a truly elegant way to create objects that all share the same state. """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
