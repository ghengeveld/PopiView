import unittest
import doctest

FLAGS = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
GLOBS = {}

class PopiViewTest(unittest.TestCase):

    def test_something(self):
        pass


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests([
        doctest.DocFileSuite('README.txt',
                             package='popiview',
                             globs=GLOBS,
                             optionflags=FLAGS),
        unittest.makeSuite(PopiViewTest)
    ])
    return test_suite
