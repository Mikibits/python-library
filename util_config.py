# util_config.py
# Easy configuration manager for [application].cfg file, including keeping
# track of recent files, window geometry, and general application-level data.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
# 2020.05.26 - 2020.06.22
#
# Notes:
#

import os
from configparser import RawConfigParser
from pathlib import Path
from tkinter import Tk

from Util.globals import *


class Config:
    """ Creates and manages a configuration file for an application.
        The name of the config file defaults to [appName].cfg. """

    def __init__(self, appName):
        super().__init__()
        self.config = RawConfigParser()
        self.filename = os.path.join(str(Path.home()), appName + '.cfg')
        self.recentFiles = []
        self.lastPath = None
        # Read in the file and populate attributes
        self.refresh()

    # General data section ("general") ........................................
    def get(self, item, default=''):
        """ Return the associated configuration string value if it exists,
        otherwise return the passed default value. """
        value = self.getSection(CFG_GENERAL, item)
        return default if not value else value

    def getInt(self, item, default=0):
        """ Return the associated configuration integer value if it exists,
        otherwise return the passed default value. """
        value = self.getSection(CFG_GENERAL, item)
        return default if not value else int(value)

    def refresh(self):
        """ Re-read the configuration file to refresh memory. """
        self.config.read(self.filename)
        self.loadRecentFiles()

    def set(self, item, data):
        """ Save a key:value pair in the config file, for a string value. """
        self.setSection(CFG_GENERAL, item, data)

    def setInt(self, item, data):
        """ Save a key:value pair in the config file, for a n integer value. """
        self.set(item, str(data))

    # Geometry section ........................................................
    def restoreGeometry(self, app: Tk, default=APPDIMENSIONS):
        """ Update frame with saved geometry data. """
        found = self.getSection(CFG_GEOM, CFG_APP)
        app.geometry(default if not found else found)

    def saveGeometry(self, app: Tk):
        """ Extract geometry data from this frame and save it. """
        geometry = GEOMETRYFORMAT.format(app.winfo_width(),
                                         app.winfo_height(),
                                         app.winfo_x(),
                                         app.winfo_y())
        self.setSection(CFG_GEOM, CFG_APP, geometry)

    # Recent files/projects section ...........................................
    def addRecentFile(self, name):
        """ Add a new recent file to the top of the list and save. """
        if self.recentFiles.count(name) > 0:
            self.recentFiles.remove(name)
        self.recentFiles.insert(0, name)
        # Save only the last X filenames
        count = len(self.recentFiles)
        for n in range(RECENTFILEMAX):
            if n < count:
                self.setSection(CFG_RECENT, str(n), self.recentFiles[n])
            else:
                self.setSection(CFG_RECENT, str(n), None)
        # Save path as default for opening next project
        self.setLastPath(name)

    def clearRecentFiles(self):
        """ User-requested clearing of the recent file list. """
        self.recentFiles.clear()
        for n in range(RECENTFILEMAX):
            self.setSection(CFG_RECENT, str(n), None)

    def getLastFile(self):
        """ Return the most recent file used. """
        lastFile = None if len(self.recentFiles) == 0 else self.recentFiles[0]
        self.setLastPath(lastFile)
        return lastFile

    def loadRecentFiles(self):
        """ Read the last 9 recent files into a list. """
        self.recentFiles.clear()
        for n in range(RECENTFILEMAX):
            rf = self.getSection(CFG_RECENT, str(n))
            if rf:
                self.recentFiles.append(rf)
            else:
                break

    # Last working path section ...............................................
    def getLastPath(self):
        """ Retrieve last data path to use to open next project. """
        return self.getSection(CFG_GENERAL, CFG_LASTPATH)

    def setLastPath(self, path):
        """ Save last path data. """
        self.setSection(CFG_GENERAL, CFG_LASTPATH, os.path.dirname(path))

    # The worker bees, doing all the real work ................................
    def getSection(self, section, item):
        """ Get an item from a section, if either exist; else None. """
        if self.config.has_section(section):
            if self.config.has_option(section, item):
                return self.config.get(section, item)
        return None

    def setSection(self, section, item, data):
        """ Set an item in a section, creating either if they don't exist. """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, item, data)
        # Write the updated file whenever anything changes
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
