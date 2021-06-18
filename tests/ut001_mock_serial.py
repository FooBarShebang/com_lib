#usr/bin/python3
"""
Module com_lib.tests.ut001_mock_serial

Unit tests for com_lib.mock_serial module.
"""

__version__ = "1.0.0.0"
__date__ = "18-06-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import unittest

#+ 3rd party libraries

from serial import SerialException

#+ modules to be tested

#+ my libraries

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ module to be tested

from com_lib.mock_serial import MockSerial

#+ test cases

class Test_MockSerial(unittest.TestCase):
    """
    Test cases for the com_lib.mock_serial module.
    
    Test id TEST-T-101. Covers the requirements REQ-AWM-100, REQ-AWM-101,
    REQ-AWM-102.
    
    Version 0.1.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 0.1.0.0
        """
        cls.TestClass = MockSerial
        cls.TestException = SerialException
    
    def test_openRaises(self):
        """
        Tests that the already open connection cannot be open again.
        
        REQ-AWM-100
        
        Version 0.1.0.0
        """
        objTest = self.TestClass()
        with self.assertRaises(self.TestException):
            objTest.open()
        objTest.close()
        del objTest
    
    def test_closeRaises(self):
        """
        Tests that the already closed connection cannot be closed again.
        
        REQ-AWM-101
        
        Version 0.1.0.0
        """
        objTest = self.TestClass()
        objTest.close()
        with self.assertRaises(self.TestException):
            objTest.close()
        del objTest
    
    def test_in_waitingRaises(self):
        """
        Tests that the already closed connection cannot be asked for the buffer
        size.
        
        REQ-AWM-102
        
        Version 0.1.0.0
        """
        objTest = self.TestClass()
        objTest.close()
        with self.assertRaises(self.TestException):
            iSize = objTest.in_waiting
        del objTest
    
    def test_writeRaises(self):
        """
        Tests that the already closed connection cannot be written into.
        
        REQ-AWM-102
        
        Version 0.1.0.0
        """
        objTest = self.TestClass()
        objTest.close()
        with self.assertRaises(self.TestException):
            objTest.write('whatever')
        del objTest
    
    def test_readRaises(self):
        """
        Tests that the already closed connection cannot be read from.
        
        REQ-AWM-102
        
        Version 0.1.0.0
        """
        objTest = self.TestClass()
        objTest.close()
        with self.assertRaises(self.TestException):
            objTest.read()
        del objTest

#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_MockSerial)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, ])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.mock_serial module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)