import unittest
import doctest

from tests import test_hit
from tests import test_dummy
from tests import test_analyzer

FLAGS = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
GLOBS = {}


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocFileSuite('README.txt',
                                        package='popiview',
                                        globs=GLOBS,
                                        optionflags=FLAGS))
    suite.addTests(test_hit.test_suite())
    suite.addTests(test_dummy.test_suite())
    suite.addTests(test_analyzer.test_suite())
    return suite
