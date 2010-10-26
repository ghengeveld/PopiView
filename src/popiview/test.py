import unittest
import doctest

from tests import test_hit

FLAGS = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
GLOBS = {}


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocFileSuite('README.txt',
                                        package='popiview',
                                        globs=GLOBS,
                                        optionflags=FLAGS))
    suite.addTests(test_hit.test_suite())
    return suite
