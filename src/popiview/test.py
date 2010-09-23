import unittest
import doctest

FLAGS = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
GLOBS = {}

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests([
        doctest.DocFileSuite('README.txt',
                             package='popiview',
                             globs=GLOBS,
                             optionflags=FLAGS)
        ])
    return test_suite
