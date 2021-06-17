# util_db.py
# Where all the database stuff happens.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
# 2020.05.26 - 2021.04.08
#
# Notes:
#

import sqlite3
from datetime import datetime

from Util.globals import DBDATEFORMAT


class Database:
    """ Simplified API between the app and an SQLite3 database. """

    def __init__(self, name):
        self.path = name

    def backup(self, toPath):
        """ Copy this database to another location. """
        source = sqlite3.connect(self.path)
        dest = sqlite3.connect(toPath)
        with dest:
            source.backup(dest)
        dest.close()
        source.close()

    def connect(self):
        """ Create a DB connection. Return connection and cursor. """
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn, conn.cursor()

    def createIndex(self, indexName, tableName, sql):
        """ Create an index, if it hasn't already. """
        script = 'CREATE UNIQUE INDEX IF NOT EXISTS ' + indexName + ' ON ' + \
                 tableName + ' (' + sql + ');'
        conn, curs = self.connect()
        curs.execute(script)
        curs.close()

    def createTable(self, tableName, sql):
        """ Create a table, if it hasn't already. """
        script = 'CREATE TABLE IF NOT EXISTS ' + tableName + ' (\n' + sql + ');'
        conn, curs = self.connect()
        curs.executescript(script)
        curs.close()

    @staticmethod
    def dateIn(date):
        """ Converts date to string going into the database. """
        return date.strftime(DBDATEFORMAT)

    @staticmethod
    def dateOut(dateString: str):
        """ Converts date from string coming out of the database. """
        if not dateString:
            return datetime.now()
        else:
            return datetime.strptime(dateString, DBDATEFORMAT)

    def delete(self, table, idNum):
        """ Delete a record by its ID. """
        sql = 'DELETE FROM ' + table + ' WHERE id=?'
        conn, curs = self.connect()
        curs.execute(sql, (idNum,))
        conn.commit()
        curs.close()

    def getCount(self, table):
        """ Returns the number of records in this table. """
        conn, curs = self.connect()
        curs.execute('SELECT COUNT(*) FROM ' + table)
        return curs.fetchone()[0]

    def getIds(self, table):
        """ Returns a list of ids from all records. """
        conn, curs = self.connect()
        curs.execute('SELECT ROWID FROM ' + table)
        rows = curs.fetchall()
        idList = []
        for row in rows:
            idList.append(row[0])
        curs.close()
        return idList

    def insert(self, table, data):
        """ Insert a record from a fielddname:value dictionary. """
        sql = 'INSERT INTO ' + table + ' ('
        sql += ", ".join(map(str, data.keys())) + ") "
        sql += "VALUES (" + '?, ' * (len(data) - 1) + '?);'
        # Execute the SQL statement
        conn, curs = self.connect()
        vals = list(data.values())
        curs.execute(sql, vals)
        conn.commit()
        # Return the new recod's ID
        newId = curs.lastrowid
        curs.close()
        return newId

    def query(self, sql):
        """ A general query (I intend to use primarily for testing only). """
        conn, curs = self.connect()
        curs.execute(sql)
# Todo: finish this?

    def selectById(self, table, idNum):
        """ Load a card, returning a dictionary "Row" of fields (or None). """
        conn, curs = self.connect()
        sql = 'SELECT * FROM {} WHERE ROWID = {}'.format(table, str(idNum))
        curs.execute(sql)
        result = curs.fetchone()
        curs.close()
        return result

    def update(self, idNum, table, data):
        """ Update an existing record from a fieldname:value dictionary. """
        sql = 'UPDATE ' + table + ' SET '
        for key in data.keys():
            sql += key + ' = ?, '
        sql = sql.rstrip(', ') + ' WHERE ROWID = ?'
        vals = list(data.values())
        vals.append(str(idNum))
        # Execute the SQL statement
        conn, curs = self.connect()
        curs.execute(sql, vals)
        conn.commit()
        curs.close()
