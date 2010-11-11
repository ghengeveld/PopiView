import unittest
import doctest

FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('README.txt',
        package='popiview', optionflags=FLAGS))
    return suite

