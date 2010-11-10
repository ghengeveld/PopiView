import unittest
import doctest

FLAGS = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
GLOBS = {}

class DoctestTestCase(unittest.TestCase):
  def __new__(self, test):
    return getattr(self, test)()

  @classmethod
  def test_readme(cls):
      return doctest.DocFileSuite('README.txt',
                           package='popiview',
                           globs=GLOBS,
                           optionflags=FLAGS)
