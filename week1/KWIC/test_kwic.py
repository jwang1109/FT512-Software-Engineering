import unittest
from kwic import kwic
import io
import sys
from unittest.mock import patch

class TestKwic(unittest.TestCase):
    """ Unittest for kwic.py"""
    """ 1.Value Error"""
    @patch('sys.stdin')
    def test_upper_case(self,wtf):
        sys.stdin = io.StringIO("The\nOf\nmAn\n::\nThE DescenT of MaN\n")
        result = kwic()
        self.assertEqual(result,["the DESCENT of man"])
    """2.No symbol "::" to separate title or word of ignore."""

    def test_Equal(self):
        with self.assertRaises(ValueError):
            sys.stdin = io.StringIO("a file with no symbol\n")
            result = kwic()
