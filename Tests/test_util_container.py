# test_util_container.py
# A set of unit tests for util.py code.
# .............................................................................
# Miki R. Marshall (Mikibits.com)
# 2021.03.24 - 2021.04.14
#
# Notes:
#   - This is as much an integration test as a set of unit tests:
#       - Each test is designed to test only that method comprehensively, but...
#       - Each test sometimes relies on preceding tests to create a complex enough
#         data context to fully test the following methods.
#       - This is the reason for the X index (test_X_methodname), in case unittest
#         wants to run the tests alphabetically.
import os
import unittest
from pathlib import Path
from unittest import TestCase

from Util.util_container import DoubleLinkList, ListTable, ListOfLists, PersistentDoubleLinkList, PersistentListOfLists
from Util.util_db import Database


class TestDoubleLinkList(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dList = DoubleLinkList()

    def test_1_addNode(self):
        print('**TestDoubleLinkList**')
        print('TEST APPEND: First, checking list is empty')
        self.assertIsNone(self.dList.head, 'init, list head is None')
        self.assertIsNone(self.dList.tail, 'init, list tail is None')
        self.assertIsNone(self.dList.cursor, 'init, list cursor is None')
        print('Appending node-1')
        node1 = self.dList.addNode(appendIt=True, label='node-1')
        self.assertIsNotNone(node1, 'node-1 created')
        self.assertEqual(self.dList.head, node1, 'node-1 is at head')
        self.assertEqual(self.dList.tail, node1, 'node-1 is at tail')
        self.assertEqual(self.dList.cursor, node1, 'cursor is at node-1')
        self.assertIsNone(node1.nodeId, 'node-1 nodeId is None')
        self.assertIsNone(node1.nref, 'node-1 next reference is None')
        self.assertIsNone(node1.pref, 'node-1 previous reference is None')
        self.assertEqual(node1.label, 'node-1', 'node-1 data correct')
        self.assertIsNone(node1.childId, "child ID None")
        self.assertIsNone(node1.sublist, 'node-1 sublist is None')
        print('TEST APPEND: Appending node-2')
        node2 = self.dList.addNode(appendIt=True, label='node-2', nodeId=222,
                                   childId=11111)
        self.assertIsNotNone(node2, 'node-2 created')
        self.assertNotEqual(self.dList.head, node2, 'node-2 not at head')
        self.assertEqual(self.dList.tail, node2, 'node-2 is at tail')
        self.assertEqual(self.dList.cursor, node2, 'cursor is at node-2')
        self.assertEqual(node2.nodeId, 222, 'node-2 nodeId is correct')
        self.assertIsNone(node2.nref, 'node-2 next reference is None')
        self.assertEqual(node2.pref, node1, 'node-2 previous ref is node-1')
        self.assertEqual(node1.nref, node2, 'node-1 next ref is node-2')
        self.assertIsNone(node1.pref, 'node-1 previous reference still None')
        self.assertEqual(node2.label, 'node-2', 'node-2 data correct')
        self.assertEqual(node2.childId, 11111, "child ID correct")
        self.assertIsNone(node2.sublist, 'node-2 sublist is None')
        print('TEST APPEND: Appending node-3')
        node3 = self.dList.addNode(appendIt=True, label='node-3', nodeId=333,
                                   sublist=DoubleLinkList())
        self.assertIsNotNone(node3, 'node-3 created')
        self.assertNotEqual(self.dList.head, node3, 'node-3 not at head')
        self.assertEqual(self.dList.tail, node3, 'node-3 is at tail')
        self.assertEqual(self.dList.cursor, node3, 'cursor is at node-3')
        self.assertEqual(node3.nodeId, 333, 'node-3 nodeId is correct')
        self.assertIsNone(node3.nref, 'node-3 next reference is None')
        self.assertEqual(node3.pref, node2, 'node-3 previous ref is node-2')
        self.assertEqual(node2.nref, node3, 'node-2 next ref is node-3')
        self.assertEqual(node2.pref, node1, 'node-2 previous ref still node-1')
        self.assertEqual(node1.nref, node2, 'node-1 next ref still node-2')
        self.assertIsNone(node1.pref, 'node-1 previous reference still None')
        self.assertEqual(node3.label, 'node-3', 'node-2 data correct')
        self.assertIsNone(node3.childId, "child ID None")
        self.assertIsNotNone(node3.sublist, 'node-3 sublist is not None')

    def test_2_first(self):
        print('TEST FIRST:')
        self.dList.cursor = None
        self.dList.first()
        self.assertEqual(self.dList.head, self.dList.cursor, 'cursor is at head')

    def test_3_atHead(self):
        print('TEST ATHEAD:')
        self.dList.cursor = None
        self.assertFalse(self.dList.atHead(), 'cursor is at atHead is false')
        self.dList.first()
        self.assertTrue(self.dList.atHead(), 'cursor is at atHead is true')

    def test_4_next(self):
        print('TEST NEXT:')
        # Note: Relies on previous tests for data and start location
        self.assertTrue(self.dList.atHead(), 'start at beginning')
        self.assertIsNone(self.dList.cursor.nodeId, 'at first record, node ID is None')
        self.assertTrue(self.dList.next(), 'next successful')
        self.assertEqual(self.dList.cursor.nodeId, 222, 'at second record')
        self.assertTrue(self.dList.next(), 'next successful')
        self.assertEqual(self.dList.cursor.nodeId, 333, 'at third record')
        self.assertFalse(self.dList.next(), 'next found the end of list')
        self.assertEqual(self.dList.cursor.nodeId, 333, 'still at third record')

    def test_5_getLabel(self):
        print('TEST GETDATA:')
        # Note: assumes initial setup from test_append()
        self.dList.first()
        self.assertEqual(self.dList.getLabel(), 'node-1', 'node-1 data found')
        self.dList.next()
        self.assertEqual(self.dList.getLabel(), 'node-2', 'node-2 data found')

    def test_6_setLabel(self):
        print('TEST SETDATA: revising data on node-1')
        self.dList.first()
        self.assertEqual(self.dList.getLabel(), 'node-1', 'node-1 data found')
        self.dList.setLabel('node-1a')
        self.assertEqual(self.dList.getLabel(), 'node-1a', 'node-1 revised data found')

    def test_7_getNodeId(self):
        print('TEST GETDATA:')
        # Note: assumes initial setup from test_append()
        self.dList.first()
        self.assertIsNone(self.dList.getNodeId(), 'node-1 recId not found')
        self.dList.next()
        self.assertEqual(self.dList.getNodeId(), 222, 'node-2 recId found')

    def test_8_setNodeId(self):
        print('TEST SETDATA: revising record ID on node-1')
        self.dList.first()
        self.assertIsNone(self.dList.getNodeId(), 'node-1 recId not found')
        self.dList.setNodeId(111)
        self.assertEqual(self.dList.getNodeId(), 111, 'node-1 revised data found')

    def test_9_last(self):
        print('TEST LAST:')
        self.dList.cursor = None
        self.dList.last()
        self.assertEqual(self.dList.tail, self.dList.cursor, 'cursor is at tail')

    def test_A_atTail(self):
        print('TEST ATTAIL:')
        self.dList.cursor = None
        self.assertFalse(self.dList.atTail(), 'cursor is at atTail is false')
        self.dList.last()
        self.assertTrue(self.dList.atTail(), 'cursor is at atTail is true')

    def test_B_previous(self):
        print('TEST PREVIOUS:')
        self.assertTrue(self.dList.atTail(), 'start at the end')
        self.assertEqual(self.dList.cursor.nodeId, 333, 'at last record')
        self.assertTrue(self.dList.previous(), 'previous successful')
        self.assertEqual(self.dList.cursor.nodeId, 222, 'at second record')
        self.assertTrue(self.dList.previous(), 'previous successful')
        self.assertEqual(self.dList.cursor.nodeId, 111, 'at first record')
        self.assertFalse(self.dList.previous(), 'previous found the start of list')
        self.assertEqual(self.dList.cursor.nodeId, 111, 'still at first record')

    def test_C_delete(self):
        print('TEST DELETE: Appending some nodes with red IDs.')
        # Create more nodes to delete (relies on test_append() setup)
        node4 = self.dList.addNode(appendIt=True, label='node-4', nodeId=444)
        node5 = self.dList.addNode(appendIt=True, label='node-5', nodeId=555)
        node6 = self.dList.addNode(appendIt=True, label='node-6', nodeId=666)
        node7 = self.dList.addNode(appendIt=True, label='node-7', nodeId=777)
        print("Check all data is gooood")
        self.dList.first()
        testId = 111
        self.assertEqual(self.dList.getNodeId(), testId, 'node correct')
        while self.dList.next():
            testId += 111
            self.assertEqual(self.dList.getNodeId(), testId, 'node correct')
        print('Delete at cursor (node 6)')
        self.dList.previous()
        self.assertEqual(self.dList.cursor, node6, 'cursor is node-6 (tail -1)')
        self.dList.delete()
        self.assertTrue(self.dList.atTail(), 'node-6 deleted, at tail now')
        self.assertEqual(self.dList.cursor, node7, 'tail is node-7')
        self.assertEqual(node7.pref, node5, 'node-5 precedes node-7 now')
        self.assertEqual(node5.nref, node7, 'node-7 comes after node-5')
        self.assertEqual(self.dList.cursor, node7, 'cursor at node-7')
        print('Delete head node')
        self.dList.first()
        self.assertEqual(self.dList.getNodeId(), 111, 'head is node-1')
        self.dList.delete()
        self.assertTrue(self.dList.atHead(), 'node-1 deleted, still at head')
        self.assertEqual(self.dList.cursor.nodeId, 222, 'cursor at node-2 (new head)')
        self.assertEqual(self.dList.cursor.nref.nodeId, 333, 'next node is still node-3')
        self.dList.next()
        self.assertEqual(self.dList.cursor.pref.nodeId, 222, 'node-2 still before node-3')
        print('Delete "at" node 4')
        self.dList.delete(node4)
        self.assertEqual(self.dList.cursor, node5, 'deleted node-4, cursor at node-5')
        self.assertEqual(self.dList.cursor.pref.nodeId, 333, 'node-3 now before node-5')
        self.dList.previous()
        self.assertEqual(self.dList.getNodeId(), 333, 'cursor at node-3')
        self.assertEqual(self.dList.cursor.nref, node5, 'node-5 after node-3')
        print('Delete tail node')
        self.dList.last()
        self.assertEqual(self.dList.cursor, node7, 'node-7 still tail')
        self.dList.delete()
        self.assertTrue(self.dList.atTail(), 'node-7 deleted, cursor still at tail')
        self.assertEqual(self.dList.cursor, node5, 'tail is node-5 now')
        self.assertEqual(self.dList.cursor.pref.nodeId, 333, 'prev node still node-3')
        self.assertIsNone(self.dList.cursor.nref, 'next after tail is None')

    def test_D_insert(self):
        print('TEST INSERT (addnode again): Insert node at head of list')
        # reinsert nodes 1, 4 at appropriate locations
        self.dList.first()
        self.assertEqual(self.dList.getNodeId(), 222, 'node-2 is still head')
        node1 = self.dList.addNode(label='node-1', nodeId=111)
        self.assertIsNotNone(node1, 'node-2 created/added')
        self.assertTrue(self.dList.atHead(), 'insert new node-1, still at head')
        self.assertEqual(self.dList.cursor, node1, 'node-2 is still head')
        self.assertEqual(node1.nodeId, 111, 'node-1 id is set')
        self.assertIsNone(node1.sublist, 'node-1 sublist is None')
        print('Insert at tail (will insert before tail item)')
        self.dList.last()
        self.assertEqual(self.dList.getNodeId(), 555, 'node-5 is still tail')
        node4 = self.dList.addNode(label='node-4', nodeId=444,
                                   sublist=DoubleLinkList())
        self.assertIsNotNone(node4, 'node-4 created/added')
        self.assertEqual(self.dList.cursor, node4, 'node-4 inserted, at cursor')
        self.assertEqual(self.dList.tail.nodeId, 555, 'node-5 is still tail')
        self.assertEqual(node4.nodeId, 444, 'node-4 id set')
        self.assertIsNotNone(node4.sublist, 'node-4 sublist set')
        print('Check entire order is correct')
        self.dList.first()
        testId = 111
        self.assertEqual(self.dList.getNodeId(), testId, 'node correct')
        while self.dList.next():
            testId += 111
            self.assertEqual(self.dList.getNodeId(), testId, 'node correct')

    def test_E_find(self):
        nodes = [self.dList.first()]
        while self.dList.next():
            nodes.append(self.dList.cursor)
        self.assertEqual(len(nodes), 5, '5 nodes in list')
        print('TEST FIND: Finding each node in random order')
        self.assertTrue(self.dList.find(nodes[2]), 'node-3 found')
        self.assertEqual(self.dList.getNodeId(), 333, 'node-3 confirmed')
        self.assertTrue(self.dList.find(nodes[0]), 'node-1 found')
        self.assertEqual(self.dList.getNodeId(), 111, 'node-1 confirmed')
        self.assertTrue(self.dList.find(nodes[4]), 'node-5 found')
        self.assertEqual(self.dList.getNodeId(), 555, 'node-5 confirmed')
        self.assertTrue(self.dList.find(nodes[3]), 'node-4 found')
        self.assertEqual(self.dList.getNodeId(), 444, 'node-4 confirmed')
        self.assertTrue(self.dList.find(nodes[1]), 'node-2 found')
        self.assertEqual(self.dList.getNodeId(), 222, 'node-2 confirmed')
        print('Find a nonexistent node')
        alienNode = DoubleLinkList.Node(nodeId=999)
        self.assertFalse(self.dList.find(alienNode), 'alien-node not found')
        self.assertEqual(self.dList.getNodeId(), 222, 'still at node-2')

    def test_F_findAt(self):
        print('TEST FINDAT: Finding nodes using random index locations')
        self.assertTrue(self.dList.findAt(3), 'node found at index 3')
        self.assertEqual(self.dList.getNodeId(), 444, 'node-4 confirmed')
        self.assertTrue(self.dList.findAt(1), 'node found at index 1')
        self.assertEqual(self.dList.getNodeId(), 222, 'node-2 confirmed')
        self.assertTrue(self.dList.findAt(4), 'node found at index 4')
        self.assertEqual(self.dList.getNodeId(), 555, 'node-5 confirmed')
        self.assertTrue(self.dList.findAt(2), 'node found at index 2')
        self.assertEqual(self.dList.getNodeId(), 333, 'node-3 confirmed')
        self.assertTrue(self.dList.findAt(0), 'node found at index 0')
        self.assertEqual(self.dList.getNodeId(), 111, 'node-1 confirmed')
        print('Find using an invalid (out of bounds) index')
        self.assertFalse(self.dList.findAt(5), 'node not found at index 5')
        self.assertEqual(self.dList.getNodeId(), 111, 'still at node-1')

    def test_G_getSublist(self):
        print('TEST getList: checks there are sublists still set')
        self.assertTrue(self.dList.findAt(3), 'node found at index 3')
        self.assertIsNotNone(self.dList.getSublist(), 'List returned from node-4')
        self.assertTrue(self.dList.findAt(2), 'node found at index 2')
        self.assertIsNotNone(self.dList.getSublist(), 'List returned from node-3')
        print('Looks for a sublist that is not there')
        self.assertTrue(self.dList.findAt(1), 'node found at index 1')
        self.assertIsNone(self.dList.getSublist(), 'List not returned from node-2')
        print('TEST COMPLETE')

    def test_Z_done(self):
        print('----- DoubleLinkList test completed -----')


class TestListOfLists(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tList = ListOfLists()

    def test_1_addList(self):
        print('**TestListOfLists**')
        print('TEST addList: First, checking list of lists is empty')
        self.assertIsNone(self.tList.head, 'list head is None')
        self.assertIsNone(self.tList.tail, 'list tail is None')
        self.assertIsNone(self.tList.cursor, 'list cursor is None')
        print('Adding list-1, appended in empty list')
        list1 = self.tList.addList(appendIt=True, label='list-1', nodeId=111)
        self.assertIsNotNone(list1, 'list-1 created')
        self.assertEqual(self.tList.head, list1, 'list-1 is at head')
        self.assertEqual(self.tList.tail, list1, 'list-1 is at tail')
        self.assertEqual(self.tList.cursor, list1, 'cursor is at list-1')
        self.assertEqual(list1.nodeId, 111, 'list-1 nodeId is correct')
        self.assertIsNone(list1.nref, 'list-1 next reference is None')
        self.assertIsNone(list1.pref, 'list-1 previous reference is None')
        self.assertEqual(list1.label, 'list-1', 'list-1 data correct')
        self.assertIsNone(list1.childId, "child ID None")
        self.assertIsNotNone(list1.sublist, 'list-1 sublist is initialized')
        print('Adding list-2, appended')
        list2 = self.tList.addList(appendIt=True, label='list-2', nodeId=222)
        self.assertIsNotNone(list2, 'list-2 created')
        self.assertNotEqual(self.tList.head, list2, 'list-2 is not at head')
        self.assertEqual(self.tList.tail, list2, 'list-2 is at tail')
        self.assertEqual(self.tList.cursor, list2, 'cursor is at list-2')
        self.assertEqual(list2.nodeId, 222, 'list-2 nodeId is correct')
        self.assertIsNone(list2.nref, 'list-2 next reference is None')
        self.assertEqual(list2.pref, list1, 'list-2 previous reference is list-1')
        self.assertEqual(list2.label, 'list-2', 'list-2 data correct')
        self.assertIsNone(list2.childId, "child ID None")
        self.assertIsNotNone(list2.sublist, 'list-2 sublist is initialized')
        print('Adding list-3 at head')
        self.tList.first()
        list3 = self.tList.addList(appendIt=False, label='list-3', nodeId=333)
        self.assertIsNotNone(list3, 'list-3 created')
        self.assertEqual(self.tList.head, list3, 'list-3 is at head')
        self.assertNotEqual(self.tList.tail, list3, 'list-3 is at tail')
        self.assertEqual(self.tList.cursor, list3, 'cursor is at list-3')
        self.assertEqual(list3.nodeId, 333, 'list-3 nodeId is correct')
        self.assertEqual(list3.nref, list1, 'list-3 next reference is list-1')
        self.assertIsNone(list3.pref, 'list-3 previous reference is None')
        self.assertEqual(list3.label, 'list-3', 'list3 data correct')
        self.assertIsNone(list3.childId, "child ID None")
        self.assertIsNotNone(list3.sublist, 'list-3 sublist is initialized')

    def test_2_addNode(self):
        print('TEST addNode: Adding a node on the first sublist.')
        # Note: Current list order is 3 - 1 - 2.
        list3 = self.tList.first()
        list1 = self.tList.next()
        list2 = self.tList.next()
        self.assertIsNotNone(list1 or list2 or list3, 'list-1, 2, and 3 created')
        self.assertIsNone(self.tList.next(), 'Correct number of lists')
        self.assertEqual(list1.label, 'list-1', 'correct list-1')
        self.assertIsNone(list1.childId, 'no child ID')
        self.assertEqual(list2.label, 'list-2', 'correct list-2')
        self.assertIsNone(list2.childId, 'no child ID')
        self.assertEqual(list3.label, 'list-3', 'correct list-3')
        self.assertIsNone(list3.childId, 'no child ID')
        print('Add nodes to all three lists')
        # Reminder: Current list order is 3 - 1 - 2.
        self.tList.first()
        node31 = self.tList.addNode(appendIt=True, label='node-31', nodeId=31)
        node32 = self.tList.addNode(appendIt=True, label='node-32', nodeId=32)
        node33 = self.tList.addNode(appendIt=True, label='node-33', nodeId=33)
        self.assertIsNotNone(node31 or node32 or node33, 'nodes for list-3 created')
        self.tList.next()
        node11 = self.tList.addNode(appendIt=True, label='node-11', nodeId=11)
        node12 = self.tList.addNode(appendIt=True, label='node-12', nodeId=12)
        node13 = self.tList.addNode(appendIt=True, label='node-13', nodeId=13)
        self.assertIsNotNone(node11 or node12 or node13, 'nodes for list-1 created')
        self.tList.next()
        node21 = self.tList.addNode(appendIt=True, label='node-21', nodeId=21)
        node22 = self.tList.addNode(appendIt=True, label='node-22', nodeId=22)
        node23 = self.tList.addNode(appendIt=True, label='node-23', nodeId=23)
        self.assertIsNotNone(node21 or node22 or node23, 'nodes for list-2 created')
        print('Check head nodes, cursors are set correctly')
        self.tList.first()
        self.assertEqual(self.tList.getHeadId(), 31, 'list-3 head (child ID) is node3-1')
        self.assertEqual(self.tList.getSublist().cursor, node33, 'list-3 @ node3-3')
        self.tList.next()
        self.assertEqual(self.tList.getHeadId(), 11, 'list-1 head (child ID)  is node1-1')
        self.assertEqual(self.tList.getSublist().cursor, node13, 'list-1 @ node1-3')
        self.tList.next()
        self.assertEqual(self.tList.getHeadId(), 21, 'list-2 head (child ID)  is node2-1')
        self.assertEqual(self.tList.getSublist().cursor, node23, 'list-2 @ node2-3')

    def test_Z_done(self):
        print('----- ListOfLists test completed -----')


class TestListTable(TestCase):
    @classmethod
    def setUpClass(cls):
        if Path('test.db').exists():
            os.remove('test.db')
        cls.db = Database('test.db')
        cls.testTable = ListTable(cls.db, 'test_table')
        cls.tList = DoubleLinkList()
        cls.n1 = cls.tList.addNode(appendIt=True, childId=101, label='node-1')
        cls.n2 = cls.tList.addNode(appendIt=True, childId=202, label='node-2')
        cls.n3 = cls.tList.addNode(appendIt=True, childId=303, label='node-3')
        cls.n4 = cls.tList.addNode(appendIt=True, childId=404, label='node-4')

    def test_1_initTable(self):
        print('**TestListTable**')
        print('TEST initTable():  Check that test DB and table initialized correctly.')
        self.assertEqual(self.db.path, 'test.db', 'database path good')
        self.assertEqual(self.testTable.tableName, 'test_table', 'table name good')
        self.assertEqual(self.db.getCount('test_table'), 1,
                         'table is empty (only Head record exists)')

    def test_2_save(self):
        print('TEST save(): Four nodes in a list')
        self.assertEqual(self.db.getCount('test_table'), 1, 'header record')
        self.testTable.save(self.n1)
        # HeadId not set yet, since ListTable doesn't handle this automatically
        self.assertEqual(self.db.getCount('test_table'), 2, '1 node in table')
        self.testTable.save(self.n2)
        self.assertEqual(self.db.getCount('test_table'), 3, '2 nodes in table')
        self.testTable.save(self.n3)
        self.assertEqual(self.db.getCount('test_table'), 4, '3 nodes in table')
        self.testTable.save(self.n4)
        self.assertEqual(self.db.getCount('test_table'), 5, '4 nodes in table')

    def test_3_headId(self):
        print('TEST loadHeadId() and saveHeadId(): save and check setting first node ID.')
        self.assertIsNone(self.testTable.loadHeadId(), 'no head id')
        self.testTable.saveHeadId(self.n1.nodeId)
        self.assertEqual(self.testTable.loadHeadId(), self.n1.nodeId, 'n1 is head ID')

    def test_4_saveNodeAndSiblings(self):
        print('TEST saveNodeAndSiblings(): Insert a node and check its neighbors.')
        self.assertIsNotNone(self.tList.find(self.n3), 'cursor at n3')
        n2a = self.tList.addNode(childId=255, label='node-2.5')
        self.assertIsNotNone(n2a, 'node-2.5 created')
        self.assertEqual(n2a.pref, self.n2, 'previous node is n2')
        self.assertEqual(n2a.nref, self.n3, 'next node is n3')
        self.testTable.saveNodeAndSiblings(n2a)
        self.assertEqual(self.db.getCount('test_table'), 6, '5 nodes in table')

    def test_5_load(self):
        print('TEST load(): via new table, checking all records are where they belong')
        db = Database('test.db')
        t2 = ListTable(db, 'test_table')
        l2 = DoubleLinkList()
        t2.load(l2)
        self.assertEqual(l2.first().label, 'node-1', 'node-1 ok')
        self.assertEqual(l2.next().label, 'node-2', 'node-2 ok')
        self.assertEqual(l2.next().label, 'node-2.5', 'node-2.5 ok')
        self.assertEqual(l2.next().label, 'node-3', 'node-3 ok')
        self.assertEqual(l2.next().label, 'node-4', 'node-4 ok')

    def test_Z_done(self):
        print('----- ListTable test completed -----')


class TestPersistentDoubleLinkList(TestCase):
    @classmethod
    def setUpClass(cls):
        if Path('test.db').exists():
            os.remove('test.db')
        cls.tpList = PersistentDoubleLinkList(Database('test.db'), 'test_table')
        cls.saveHeadId = None

    def test_1_initTable(self):
        print('**TestPersistentDoubleLinkList**')
        print('TEST initTable():  Check DB, table, and list initialized correctly.')
        self.assertEqual(self.tpList.db.path, 'test.db', 'database path good')
        self.assertEqual(self.tpList.tableName, 'test_table', 'table name good')
        self.assertIsNone(self.tpList.head, 'empty list of sublists')
        self.assertEqual(self.tpList.db.getCount('test_table'), 1, 'table is empty (only Head record exists)')

    def test_2_addNode(self):
        print('TEST addNode():  Check that it is empty.')
        self.assertIsNone(self.tpList.head, 'init, list head is None')
        self.assertIsNone(self.tpList.tail, 'init, list tail is None')
        self.assertIsNone(self.tpList.cursor, 'init, list cursor is None')
        print('Appending node-1 as the first node')
        node1 = self.tpList.addNode(appendIt=True, label='node-1')
        self.assertIsNotNone(node1, 'node1 created')
        self.assertEqual(self.tpList.head, node1, 'node-1 is at head')
        self.assertEqual(self.tpList.tail, node1, 'node-1 is at tail')
        self.assertEqual(self.tpList.cursor, node1, 'cursor is at node-1')
        self.assertIsNotNone(node1.nodeId, 'node-1 nodeId was set by save()')
        self.assertEqual(self.tpList.headId, node1.nodeId, 'node-1 ID is head ID')
        self.assertIsNone(node1.nref, 'node-1 next reference is None')
        self.assertIsNone(node1.pref, 'node-1 previous reference is None')
        self.assertEqual(node1.label, 'node-1', 'node-1 label correct')
        self.assertIsNone(node1.childId, "child ID None")
        self.assertIsNone(node1.sublist, 'node-1 sublist is None')
        self.assertEqual(self.tpList.db.getCount('test_table'), 2, 'table has 1 node')
        print('TEST APPEND: Appending node-2')
        node2 = self.tpList.addNode(appendIt=True, label='node-2', childId=11111)
        self.assertIsNotNone(node2, 'node2 created')
        self.assertNotEqual(self.tpList.head, node2, 'node-2 is not at head')
        self.assertEqual(self.tpList.tail, node2, 'node-2 is at tail')
        self.assertEqual(self.tpList.cursor, node2, 'cursor is at node-2')
        self.assertIsNotNone(node2.nodeId, 'node-2 nodeId was set by save()')
        self.assertNotEqual(self.tpList.headId, node2.nodeId, 'node-2 ID is not head ID')
        self.assertIsNone(node2.nref, 'node-2 next reference is None')
        self.assertEqual(node2.pref, node1, 'node-2 previous ref is node-1')
        self.assertEqual(node1.nref, node2, 'node-1 next ref is node-2')
        self.assertIsNone(node1.pref, 'node-1 previous reference still None')
        self.assertEqual(node2.label, 'node-2', 'node-2 label correct')
        self.assertEqual(node2.childId, 11111, "child ID correct")
        self.assertIsNone(node2.sublist, 'node-2 sublist is None')
        self.assertEqual(self.tpList.db.getCount('test_table'), 3, 'table has 2 nodes')
        print('TEST Insert: Inserting node-3 at head')
        self.tpList.first()
        node3 = self.tpList.addNode(label='node-3', sublist=DoubleLinkList())
        self.assertIsNotNone(node3, 'node3 created')
        self.assertEqual(self.tpList.head, node3, 'node-3 is at head')
        self.assertNotEqual(self.tpList.tail, node3, 'node-3 is not at tail')
        self.assertEqual(self.tpList.cursor, node3, 'cursor is at node-3')
        self.assertIsNotNone(node3.nodeId, 'node-3 nodeId was set by save()')
        self.assertEqual(self.tpList.headId, node3.nodeId, 'node-3 ID is head ID')
        self.assertIsNone(node3.pref, 'node-3 previous reference is None')
        self.assertEqual(node3.nref, node1, 'node-3 next reference is node-1')
        self.assertEqual(node1.pref, node3, 'node-1 previous ref node-3')
        self.assertEqual(node1.nref, node2, 'node-1 next ref still node-2')
        self.assertEqual(node3.label, 'node-3', 'node-3 label correct')
        self.assertIsNone(node3.childId, "child ID None")
        self.assertIsNotNone(node3.sublist, 'node-3 sublist is not None')
        self.assertEqual(self.tpList.db.getCount('test_table'), 4, 'table has 3 nodes')

    def test_3_load(self):
        print('TEST load(): check all nodes in a new list from the same table.')
        # Note: node order (by label) is 3 - 1 - 2
        lp2 = PersistentDoubleLinkList(Database('test.db'), 'test_table')
        self.assertEqual(lp2.db.getCount('test_table'), 4, 'table has 3 nodes')
        self.assertEqual(lp2.headId, lp2.first().nodeId, 'table head ID is correct')
        self.assertEqual(lp2.getLabel(), 'node-3', 'rec 1 is node-3, ok')
        self.assertEqual(lp2.next().label, 'node-1', 'rec 2 is node-1, ok')
        self.assertEqual(lp2.next().label, 'node-2', 'rec 3 is node-2, ok')
        self.assertIsNone(lp2.next(), 'That was the last record')

    def test_Z_done(self):
        print('----- PersistentDoubleLinkList test completed -----')


class TestPersistentListOfLists(TestCase):
    @classmethod
    def setUpClass(cls):
        if Path('test.db').exists():
            os.remove('test.db')
        cls.plList = PersistentListOfLists(Database('test.db'), 'test_table')
        cls.saveHeadId = []

    def test_1_initTable(self):
        print('**TestPersistentListOfLists**')
        print('TEST initTable():  Check DB, table, and list initialized correctly.')
        self.assertEqual(self.plList.db.path, 'test.db', 'database path good')
        self.assertEqual(self.plList.tableName, 'test_table', 'table name good')
        self.assertIsNone(self.plList.head, 'empty list of sublists')
        self.assertEqual(self.plList.db.getCount('test_table'), 1, 'table is empty (only Head record exists)')

    def test_2_addList(self):
        print('TEST addList():  Check that it is empty first.')
        self.assertIsNone(self.plList.head, 'list head is None')
        self.assertIsNone(self.plList.tail, 'list tail is None')
        self.assertIsNone(self.plList.cursor, 'list cursor is None')
        print('Appending list-1 as first sublist')

        # todo: Continue morphing ListOfLists test code to PersistentListOfLists here...

        list1 = self.plList.addList(appendIt=True, label='list-1')
        self.assertIsNotNone(list1, 'list-1 created')
        self.assertEqual(self.plList.head, list1, 'list-1 is at head')
        self.assertEqual(self.plList.tail, list1, 'list-1 is at tail')
        self.assertEqual(self.plList.cursor, list1, 'cursor is at list-1')
        self.assertIsNotNone(list1.nodeId, 'list-1 nodeId set by save()')
        self.assertIsNone(list1.nref, 'list-1 next reference is None')
        self.assertEqual(list1.label, 'list-1', 'list-1 label is correct')
        self.assertIsNone(list1.pref, 'list-1 previous reference is None')
        self.assertEqual(list1.label, 'list-1', 'list-1 data correct')
        self.assertIsNone(list1.childId, "child ID None")
        self.assertIsNotNone(list1.sublist, 'list-1 sublist is initialized')
        self.assertEqual(self.plList.db.getCount('test_table'), 2,
                         'table has 1 list node')
        print('Adding list-2, appended')
        list2 = self.plList.addList(appendIt=True, label='list-2')
        self.assertIsNotNone(list2, 'list-2 created')
        self.assertNotEqual(self.plList.head, list2, 'list-2 is not at head')
        self.assertEqual(self.plList.tail, list2, 'list-2 is at tail')
        self.assertEqual(self.plList.cursor, list2, 'cursor is at list-2')
        self.assertIsNotNone(list2.nodeId, 'list-2 nodeId set by save()')
        self.assertEqual(list2.label, 'list-2', 'list-2 label is correct')
        self.assertIsNone(list2.nref, 'list-2 next reference is None')
        self.assertEqual(list2.pref, list1, 'list-2 previous reference is list-1')
        self.assertEqual(list2.label, 'list-2', 'list-2 data correct')
        self.assertIsNone(list2.childId, "child ID None")
        self.assertIsNotNone(list2.sublist, 'list-2 sublist is initialized')
        self.assertEqual(self.plList.db.getCount('test_table'), 3,
                         'table has 2 list nodes')
        print('Indserting list-3 at head')
        self.plList.first()
        list3 = self.plList.addList(label='list-3')
        self.assertIsNotNone(list3, 'list-3 created')
        self.assertEqual(self.plList.head, list3, 'list-3 is at head')
        self.assertEqual(self.plList.tail, list2, 'list-2 is at tail')
        self.assertEqual(self.plList.cursor, list3, 'cursor is at list-3')
        self.assertIsNotNone(list3.nodeId, 'list-3 nodeId set by save()')
        self.assertEqual(list3.label, 'list-3', 'list-3 label is correct')
        self.assertIsNone(list3.pref, 'list-3 previous reference is None')
        self.assertEqual(list3.nref, list1, 'list-3 next reference is list-1')
        self.assertEqual(list1.pref, list3, 'list-1 previous reference is list-3')
        self.assertEqual(list1.nref, list2, 'list-1 next reference is list-2')
        self.assertEqual(list2.pref, list1, 'list-2 previous reference is list-1')
        self.assertIsNone(list2.nref, 'list-2 next reference is None')
        self.assertEqual(list3.label, 'list-3', 'list3 data correct')
        self.assertIsNone(list3.childId, "list-3 child ID None")
        self.assertIsNotNone(list3.sublist, 'list-3 sublist is initialized')
        self.assertEqual(self.plList.db.getCount('test_table'), 4,
                         'table has 3 list nodes')

    def test_3_addNode(self):
        print('TEST addNode: Adding a node on the first sublist.')
        # Note: Current list order is 3 - 1 - 2.
        list3 = self.plList.first()
        list1 = self.plList.next()
        list2 = self.plList.next()
        self.assertIsNone(self.plList.next(), 'Correct number of lists')
        self.assertEqual(list1.label, 'list-1', 'correct first list')
        self.assertIsNone(list1.childId, 'no child ID')
        self.assertEqual(list2.label, 'list-2', 'correct first list')
        self.assertIsNone(list2.childId, 'no child ID')
        self.assertEqual(list3.label, 'list-3', 'correct first list')
        self.assertIsNone(list3.childId, 'no child ID')
        print('Add nodes in to all three lists')
        self.plList.first()
        node31 = self.plList.addNode(appendIt=True, label='node-31')
        node32 = self.plList.addNode(appendIt=True, label='node-32')
        node33 = self.plList.addNode(appendIt=True, label='node-33')
        self.assertIsNotNone(node31 or node32 or node33, 'nodes for list-3 created')
        self.assertEqual(self.plList.db.getCount('test_table'), 7,
                         'table has 3 list nodes with 3 child nodes')
        self.plList.next()
        node11 = self.plList.addNode(appendIt=True, label='node-11')
        node12 = self.plList.addNode(appendIt=True, label='node-12')
        node13 = self.plList.addNode(appendIt=True, label='node-13')
        self.assertIsNotNone(node11 or node12 or node13, 'nodes for list-1 created')
        self.assertEqual(self.plList.db.getCount('test_table'), 10,
                         'table has 3 list nodes with 6 child nodes')
        self.plList.next()
        node21 = self.plList.addNode(appendIt=True, label='node-21')
        node22 = self.plList.addNode(appendIt=True, label='node-22')
        node23 = self.plList.addNode(appendIt=True, label='node-23')
        self.assertIsNotNone(node21 or node22 or node23, 'nodes for list-2 created')
        self.assertEqual(self.plList.db.getCount('test_table'), 13,
                         'table has 3 list nodes with 9 child nodes')
        print('Check head nodes, cursors are set correctly')
        self.plList.first()
        self.assertEqual(self.plList.getChildId(), node31.nodeId, 'list-3 head is node3-1')
        self.assertEqual(self.plList.getSublist().cursor, node33, 'list-3 @ node3-3')
        self.plList.next()
        self.assertEqual(self.plList.getChildId(), node11.nodeId, 'list-1 head is node1-1')
        self.assertEqual(self.plList.getSublist().cursor, node13, 'list-1 @ node1-3')
        self.plList.next()
        self.assertEqual(self.plList.getChildId(), node21.nodeId, 'list-2 head is node2-1')
        self.assertEqual(self.plList.getSublist().cursor, node23, 'list-2 @ node2-3')
        # Save IDs for next test
        self.saveHeadId.append(self.plList.headId)
        self.saveHeadId.append(node11.nodeId)
        self.saveHeadId.append(node21.nodeId)
        self.saveHeadId.append(node31.nodeId)

    def test_4_load(self):
        print('TEST load(): check all nodes in a new list from the same table.')
        # Note: list order (by label) is 3 - 1 - 2
        lp2 = PersistentListOfLists(Database('test.db'), 'test_table')
        self.assertEqual(lp2.db.getCount('test_table'), 13, 'table has 3 lists + 9 nodes')
        self.assertEqual(lp2.headId, self.saveHeadId[0], "head ID is list-3")
        list3 = lp2.first()
        self.assertEqual(lp2.getChildId(), self.saveHeadId[3], 'list-3 headId is good')
        self.assertIsNotNone(list3, 'list-3 good')
        self.assertEqual(list3.label, 'list-3', 'rec 1 - list-3, ok')
        list1 = lp2.next()
        self.assertEqual(lp2.getChildId(), self.saveHeadId[1], 'list-1 headId is good')
        self.assertIsNotNone(list1, 'list-1 good')
        self.assertEqual(list1.label, 'list-1', 'rec 2 - list-1, ok')
        list2 = lp2.next()
        self.assertEqual(lp2.getChildId(), self.saveHeadId[2], 'list-2 headId is good')
        self.assertIsNotNone(list2, 'list-2 good')
        self.assertEqual(list2.label, 'list-2', 'rec 3 - list-2, ok')
        self.assertIsNone(lp2.next(), 'That was the last record')
        print('Check nodes in each sublist')
        sublist = lp2.first().sublist
        self.assertEqual(sublist.first().label, 'node-31', 'list-3, node-1:')
        self.assertEqual(sublist.next().label, 'node-32', 'list-3, node-2:')
        self.assertEqual(sublist.next().label, 'node-33', 'list-3, node-3:')
        self.assertIsNone(sublist.next(), 'end of list-3')
        sublist = lp2.next().sublist
        self.assertEqual(sublist.first().label, 'node-11', 'list-1, node-1:')
        self.assertEqual(sublist.next().label, 'node-12', 'list-1, node-2:')
        self.assertEqual(sublist.next().label, 'node-13', 'list-1, node-3:')
        self.assertIsNone(sublist.next(), 'end of list-1')
        sublist = lp2.next().sublist
        self.assertEqual(sublist.first().label, 'node-21', 'list-2, node-1:')
        self.assertEqual(sublist.next().label, 'node-22', 'list-2, node-2:')
        self.assertEqual(sublist.next().label, 'node-23', 'list-2, node-3:')
        self.assertIsNone(sublist.next(), 'end of list-2')
        self.assertIsNone(lp2.next(), 'end of list of lists')

    def test_Z_done(self):
        print('----- PersistentListOfLists test completed -----')


if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()
