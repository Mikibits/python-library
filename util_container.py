# util_container.py
# Handy reusable things: container stuff.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
# 2021.04.07 - 2021.04.08
#
# Notes:


# Classes .....................................................................
class DoubleLinkList:
    """ Implementing a double linked list, capable of nesting itself. """

    class Node:
        """ The list's data holder:
            recId = my database record ID key (for list persistence)
            nref = pointer to next record (sibling)
            pref = pointer to previous record (sibling)
            childId = any child data, like the foreign key to another table record
            sublist = pointer to another LL, for multidimensional lists
            label = optional text for testing or for titles or whatever. """

        def __init__(self, nodeId=None, childId=None, sublist=None, label=''):
            self.nodeId = nodeId
            self.nref = None
            self.pref = None
            self.childId = childId
            self.sublist = sublist
            self.label = label

    def __init__(self):
        self.head = None
        self.tail = None
        self.cursor = None

    def addNode(self, appendIt=False, nodeId=None, childId=None, sublist=None, label=''):
        """ Create a node and insert it before the cursor node, or append it at the end
            of the list when requested. """
        node = DoubleLinkList.Node(nodeId=nodeId, childId=childId, sublist=sublist, label=label)
        if not self.head:
            # Empty list, add as the first entity
            self.head = self.tail = self.cursor = node
        else:
            if appendIt:
                node.pref = self.tail
                node.pref.nref = node
                self.tail = self.cursor = node
            else:
                nodeAfter = self.cursor
                nodeBefore = self.cursor.pref
                node.nref = nodeAfter
                nodeAfter.pref = node
                if self.atHead():
                    self.head = self.cursor = node
                else:
                    node.pref = nodeBefore
                    nodeBefore.nref = node
                    self.cursor = node
        return node

    def atHead(self):
        """ Check if this node is the first in the list. """
        return self.cursor == self.head

    def atTail(self):
        """ Check if this node is the first in the list. """
        return self.cursor == self.tail

    def delete(self, atNode=None):
        """ Delete this node (or the current node) from the list. """
        # Todo: Check for childId not None, and either recursively delete or abort.
        if not atNode:
            atNode = self.cursor
        if atNode == self.head:
            self.head = atNode.nref
            if self.head:
                self.head.pref = None
            self.cursor = self.head
        else:
            if atNode == self.tail:
                self.tail = atNode.pref
                if self.tail:
                    self.tail.nref = None
                self.cursor = self.tail
            else:
                atNode.pref.nref = atNode.nref
                atNode.nref.pref = atNode.pref
                self.cursor = atNode.nref
        del atNode
        return self.cursor

    def find(self, node):
        """ Set the cursor position to this node. """
        saveCursor = self.cursor
        if self.first() and self.cursor.nodeId == node.nodeId:
            return self.cursor
        while self.next():
            if self.cursor.nodeId == node.nodeId:
                return self.cursor
        self.cursor = saveCursor
        return None

    def findAt(self, index):
        """ Given a zero-based index position, find the item at that position. """
        saveCursor = self.cursor
        i = 0
        if self.first():
            if index == i:
                return self.cursor
            else:
                while self.next():
                    i += 1
                    if index == i:
                        return self.cursor
        self.cursor = saveCursor
        return None

    def first(self):
        """ Set cursor to head and return value. """
        if self.head:
            self.cursor = self.head
            return self.cursor
        return None

    def getChildId(self):
        """ Return the data at the current node. """
        if self.cursor:
            return self.cursor.childId
        return None

    def getLabel(self):
        if self.cursor:
            return self.cursor.label
        return ''

    def getNodeId(self):
        """ Return the data at the current node. """
        if self.cursor:
            return self.cursor.nodeId
        return None

    def getSublist(self):
        """ Return child list for the current node, if it has one. """
        if self.cursor:
            return self.cursor.sublist
        return None

    def last(self):
        """ Set cursor to head and return value. """
        if self.tail:
            self.cursor = self.tail
            return self.cursor
        return None

    def next(self):
        """ Set cursor to next node and return value. """
        if self.cursor.nref:
            self.cursor = self.cursor.nref
            return self.cursor
        return None

    def previous(self):
        """ Set cursor to previous node and return value. """
        if self.cursor.pref:
            self.cursor = self.cursor.pref
            return self.cursor
        return None

    def setChildId(self, childId):
        """ Update the child pointer ID for the current node. """
        if self.cursor:
            self.cursor.childId = childId

    def setLabel(self, label):
        """ Update the label for the current node. """
        if self.cursor:
            self.cursor.label = label

    def setNodeId(self, recId):
        """ Update the node Id for the current node. """
        if self.cursor:
            self.cursor.nodeId = recId

    def setSublist(self, sublist):
        """ Update the sublist for the current node. """
        if self.cursor:
            self.cursor.sublist = sublist


class ListOfLists(DoubleLinkList):
    """ The parent list of other lists, creating a ragged 2-dimensional
        grid of lists (think solitaire, where cards can be moved in their list
        columns, and columns themselves can be manipulated likewise).
    """

    def __init__(self):
        super().__init__()

    def addNode(self, appendIt=False, nodeId=None, childId=None, sublist=None, label=''):
        """ Adds a node at the current location of the current sublist, which means
            it is using two cursors: one for each dimension of the list of lists.
            Returns the node added and sets it as the new cursor position in this sublist.
            Use returned node.sublist, or getSublist() to access the current sublist. """
        currentList = self.getSublist()
        node = currentList.addNode(appendIt=appendIt, nodeId=nodeId, childId=childId,
                                   label=label)
        # Update head for this sublist if head node added
        if currentList.atHead():
            self.setChildId(node.nodeId)
        return node

    def addList(self, appendIt=False, nodeId=None, childId=None, label=''):
        """ Create a new list and a new node to store it in (as a sublist).
            Adds it in the list of lists before the cursor node, or appends it at
            the end of the list when requested.
            Returns the node containing the sublist and makes it the new cursor. """
        sublist = DoubleLinkList()
        return super().addNode(appendIt=appendIt, nodeId=nodeId, childId=childId,
                               sublist=sublist, label=label)

    def getHeadId(self):
        """ Returns the current list's head node ID, which is the ID of the first node
            in the sublist. Stored as the child ID in the cursor sublist node. """
        if self.cursor:
            return self.cursor.childId
        return None


class ListTable:
    """ Adds a table designed to hold lists and list of lists, while supporting a
        mutable editing and reording of this data with minimal updates needed in the
        database. Used as a base class for 'persistent' classes:
         - PersistentDoubleLinkList
         - PersistentListOfLists. """

    def __init__(self, db, tableName):
        super().__init__()
        self.db = db
        self.tableName = tableName
        self.headId = None
        self.initTable()

    def initTable(self):
        """ Create the table, if it doesn't already exist in the current database.
            It also reserves the very first record to store the 'head' record ID,
            since this is mutable (the user can shift data around), thus we need
            a solid starting point, pointing to the head, wherever it may be in the
            table at the moment. """
        sql = """ ( nodeId integer PRIMARY KEY,
                    nextId integer,
                    childId integer,
                    label text);
            """
        self.db.createTable(self.tableName + sql)
        # Reserve the first record as the head pointer, if it's not there
        found = self.db.selectById(self.tableName, 1)
        if not found:
            record = dict(nextId=None, childId=None, label='head pointer')
            self.db.insert(self.tableName, record)

    def load(self, theList: DoubleLinkList):
        """ Load all connected nodes beginning with the Head ID from the first
            record into the provided DoubleLinkList (1-dimensional). """
        nextId = self.loadHeadId()
        while nextId:
            rec = self.db.selectById(self.tableName, nextId)
            theList.addNode(appendIt=True, nodeId=rec['nodeId'], childId=rec['childId'],
                            label=rec['label'])
            nextId = rec['nextId']

    def loadListOfLists(self, theList: ListOfLists):
        """ Load all connected nodes beginning with the Head ID from the first
            record into the provided ListOfLists (2-dimensional), as sublists.
            Then load each sublist. """
        nextListId = self.loadHeadId()
        while nextListId:
            rec = self.db.selectById(self.tableName, nextListId)
            childId = rec['childId']
            theList.addList(appendIt=True, nodeId=rec['nodeId'], childId=childId,
                            label=rec['label'])
            nextListId = rec['nextId']
            if childId:
                nextNodeId = childId
                while nextNodeId:
                    rec = self.db.selectById(self.tableName, nextNodeId)
                    theList.addNode(appendIt=True, nodeId=rec['nodeId'],
                                    childId=rec['childId'], label=rec['label'])
                    nextNodeId = rec['nextId']

    def loadHeadId(self):
        """ Loads the first record of the table, which holds the record ID of
            the head node in the saved link list. This node ID can change whenever
            a new head node or sublist node is added or deleted. """
        rec = self.db.selectById(self.tableName, 1)
        if rec:
            self.headId = rec['childId']
            return self.headId
        print('Error! No first sublist record found.')
        return None

    def save(self, node):
        """ Update node data to the database, filtering out passed siblings
            which are None. Inserts if there's no node ID, to acquire one from
            the new record ID, which also updates the previous nodes next ID.
            Otherwise it updates the old record. """
        if node:
            nextId = node.nref.nodeId if node.nref else None
            record = dict(nextId=nextId, childId=node.childId, label=node.label)
            if not node.nodeId:
                node.nodeId = self.db.insert(self.tableName, record)
                self.save(node.pref)
            else:
                self.db.update(node.nodeId, self.tableName, record)

    def saveHeadId(self, headId):
        """ Updates the record id of the head sublist record. """
        self.headId = headId
        record = dict(nextId=None, childId=headId, label='head pointer')
        self.db.update(1, self.tableName, record)

    def saveNodeAndSiblings(self, node):
        """ Saves this node, plus its sibling nodes that also changed due to
            an add or move operation. The save() method automatically ignores
            sibling nodes that are None. """
        self.save(node)
        self.save(node.pref)
        self.save(node.nref)


class PersistentDoubleLinkList(DoubleLinkList, ListTable):
    """ Adds persistence to the DoubleLinkList, by handling saving all nodes to the
        passed database table. To make this class reusable, it is assumed the 'child'
        data from the DoubleLinkList is an ID to lookup a more robust data object
        defined and handled in the overall application. """

    def __init__(self, db, tableName):
        DoubleLinkList.__init__(self)
        ListTable.__init__(self, db, tableName)
        # Load the table into memory
        self.load(self)

    def addNode(self, appendIt=False, nodeId=None, childId=None, sublist=None, label=''):
        """ A wrapper for DoubleLinkList.addNode(), which calls the base class,
            then updates the database for this node and its immediate siblings.
            If the new node replaced the head node, also update the head pointer
            record (record 1). """
        node = super().addNode(appendIt=appendIt, nodeId=nodeId, childId=childId,
                               sublist=sublist, label=label)
        self.save(node)
        if self.atHead():
            self.saveHeadId(node.nodeId)
        return node


class PersistentListOfLists(ListOfLists, ListTable):
    """ Adds persistence to the ListOfLists class, pretty much the same as
        PersistentDoubleLinkList does, but recursively. """

    def __init__(self, db, tableName):
        ListOfLists.__init__(self)
        ListTable.__init__(self, db, tableName)
        # Load the table into memory
        self.loadListOfLists(self)

    def addNode(self, appendIt=False, nodeId=None, childId=None, sublist=None, label=''):
        """ Adds a node at the current location of the current sublist, which means
            it is using two cursors: one for each dimension of the list of lists.
            Returns the node added and sets it as the new cursor position in this sublist.
            Use returned node.sublist or getSublist() to access the current sublist. """
        node = super().addNode(appendIt=appendIt, nodeId=nodeId, childId=childId,
                               label=label)
        self.save(node)
        if self.getSublist().atHead():
            # Update childID (sublist head) if this node is first in the sublist
            self.setChildId(node.nodeId)
            self.save(self.cursor)
        return node

    def addList(self, appendIt=False, nodeId=None, childId=None, label=''):
        """ Create a new list and a new node to store it in (as a sublist).
            Adds it in the list of lists before the cursor node, or appends it at
            the end of the list when requested.
            Returns the node containing the sublist and makes it the new cursor. """
        node = super().addList(appendIt=appendIt, nodeId=nodeId, childId=childId,
                               label=label)
        self.save(node)
        if self.atHead():
            self.saveHeadId(node.nodeId)
        return node
