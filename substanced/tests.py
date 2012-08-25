import unittest
from pyramid import testing

class Test_root_factory(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _callFUT(self, request, transaction, get_connection):
        from . import root_factory
        return root_factory(request, transaction, get_connection)

    def _makeRequest(self, app_root=None):
        request = Dummy()
        request.registry = Dummy()
        request.registry.content = Dummy()
        request.registry.content.create = lambda *arg: app_root
        return request

    def test_without_app_root(self):
        txn = DummyTransaction()
        root = {}
        gc = Dummy_get_connection(root)
        app_root = object()
        request = self._makeRequest(app_root)
        result = self._callFUT(request, txn, gc)
        self.assertEqual(result, app_root)
        self.assertTrue(txn.committed)
        
    def test_with_app_root(self):
        txn = DummyTransaction()
        app_root = object()
        root = {'app_root':app_root}
        gc = Dummy_get_connection(root)
        request = testing.DummyRequest()
        result = self._callFUT(request, txn, gc)
        self.assertEqual(result, app_root)
        self.assertFalse(txn.committed)

class DummyTransaction(object):
    committed = False
    def commit(self):
        self.committed = True

class Dummy_get_connection(object):
    def __init__(self, root):
        self._root = root

    def root(self):
        return self._root

    def __call__(self, request):
        return self

class Dummy(object):
    pass

