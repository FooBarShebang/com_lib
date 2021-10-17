#usr/bin/python3
"""
Module com_lib.tests.ut003_serialization

Unit tests for com_lib.serialization

Covered classes:
    SimpleCOM_API
"""

__version__ = "1.0.0.0"
__date__ = "15-10-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import unittest


#+ my libraries

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ module to be tested

from com_lib.serialization import ???

#classes

#+ helper classes

class Test_Basis(unittest.TestCase):
    """
    Test cases for the SimpleCOM_API class.
    
    Test ids: TEST-T-210, TEST-T-220, TEST-T-221, TEST-T-222, TEST-T-223,
    TEST-T-224, TEST-T-225, TEST-T-226, TEST-T-227, TEST-T-228
    Covers requrements: REQ-FUN-210, REQ-FUN-220, REQ-FUN-221, REQ-FUN-222,
    REQ-FUN-223, REQ-FUN-224, REQ-FUN-225, REQ-FUN-226, REQ-FUN-227,
    REQ-FUN-228, REQ-AWM-220, REQ-AWM-221, REQ-AWM-222, REQ-AWM-223, REQ-AWM-224
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        cls.TestClass = None # must be re-defined

#+ test cases

class Test_SimpleCOM_API(unittest.TestCase):
    """
    Test cases for the SimpleCOM_API class.
    
    Test ids: TEST-T-210, TEST-T-220, TEST-T-221, TEST-T-222, TEST-T-223,
    TEST-T-224, TEST-T-225, TEST-T-226, TEST-T-227, TEST-T-228
    Covers requrements: REQ-FUN-210, REQ-FUN-220, REQ-FUN-221, REQ-FUN-222,
    REQ-FUN-223, REQ-FUN-224, REQ-FUN-225, REQ-FUN-226, REQ-FUN-227,
    REQ-FUN-228, REQ-AWM-220, REQ-AWM-221, REQ-AWM-222, REQ-AWM-223, REQ-AWM-224
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        cls.TestClass = MockCom


#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_SimpleCOM_API)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, ])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.serialization module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)