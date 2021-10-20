#usr/bin/python3
"""
Module com_lib.tests.ut003_serialization

Unit tests for com_lib.serialization

Covered classes:
    SimpleCOM_API
"""

__version__ = "1.0.0.0"
__date__ = "18-10-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import types
import unittest
import ctypes

#+ my libraries

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ module to be tested

from com_lib.serialization import SerNULL, SerArray, SerDynamicArray, SerStruct

#classes

#+ helper classes

#++ native endianness

class BaseStruct(SerStruct):
    
    _Fields = (
        ('a', ctypes.c_short),
        ('b', ctypes.c_float)
    )

class BaseArray(SerArray):
    
    _ElementType = ctypes.c_short
    
    _Length = 2

class Test_Basis(unittest.TestCase):
    """
    Prototype test suite for the classes in serialization module.
    
    Test ids: TEST-T-300, TEST-T-301 and TEST-T-303
    Covers requrements: REQ-FUN-302, REQ-AWM-303 and REQ-AWM-305
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        cls.TestClass = None # must be re-defined
        cls.ExpectedAPI = (
            ('getSize', types.MethodType),
            ('unpackBytes', types.MethodType),
            ('unpackJSON', types.MethodType),
            ('packBytes', types.FunctionType),
            ('packJSON', types.FunctionType),
            ('getNative', types.FunctionType)
        )
        cls.CheckAttributes = ('__dict__', '_Fields', '_ElementType', '_Length')
    
    def test_API(self):
        """
        Checks that the required attributes are present and they are either a
        class method or an instance method.
        
        Test ID: TEST-T-300
        
        Covers requirement: REQ-FUN-302
        
        Version 1.0.0.0
        """
        for strName, tType in self.ExpectedAPI:
            self.assertTrue(hasattr(self.TestClass, strName))
            gTemp = getattr(self.TestClass, strName)
            self.assertIsInstance(gTemp, tType)
    
    def test_Read_AttributeError(self):
        """
        Checks that AttribureError or its sub-class if the read access
        limitations are violated.
        
        Test ID: TEST-T-301
        
        Covers requirement: REQ-AWM-305
        
        Version 1.0.0.0
        """
        objTest = self.TestClass()
        #not existing 'normal' attribute
        with self.assertRaises(AttributeError):
            a = objTest.SomeNotPresentAttribute
        for strName in self.CheckAttributes:
            with self.assertRaises(AttributeError):
                a = getattr(objTest, strName)
        del objTest
    
    def test_Write_AttributeError(self):
        """
        Checks that AttribureError or its sub-class if the write access
        limitations are violated.
        
        Test ID: TEST-T-301
        
        Covers requirement: REQ-AWM-305
        
        Version 1.0.0.0
        """
        objTest = self.TestClass()
        #not existing 'normal' attribute
        with self.assertRaises(AttributeError):
            objTest.SomeNotPresentAttribute = 1
        for strName in self.CheckAttributes:
            with self.assertRaises(AttributeError):
                setattr(objTest, strName, 1)
        for strName, _ in self.ExpectedAPI:
            with self.assertRaises(AttributeError):
                setattr(objTest, strName, 1)
        del objTest
    
    def test_unpackJSON_TypeError(self):
        """
        Checks that unpackJSON method raises sub-class of TypeError if the
        input is not a string.
        
        Test ID: TEST-T-302
        
        Covers requirement: REQ-AWM-303
        
        Version 1.0.0.0
        """
        for gValue in (1, 2.0, str, bytes, b'123', (1,2)):
            with self.assertRaises(TypeError):
                self.TestClass.unpackJSON(gValue)
    
    def test_unpackBytes_TypeError(self):
        """
        Checks that unpackBytes method raises sub-class of TypeError if the
        input is not a bytestring
        
        Test ID: TEST-T-302
        
        Covers requirement: REQ-AWM-303
        
        Version 1.0.0.0
        """
        for gValue in (1, 2.0, str, bytes, '123', (1,2)):
            with self.assertRaises(TypeError):
                self.TestClass.unpackBytes(gValue)
    
    def test_Improper_JSON(self):
        """
        Checks that a not proper JSON but string argument passed into the
        method unpackJSON results in ValueError or its sub-class exception.
        
        Version 1.0.0.0
        """
        #improper JSON strings!
        for strValue in ("'a'", '{"a"=1}', '{a : 1}', 'Null', 'name', 'True'):
            with self.assertRaises(ValueError):
                self.TestClass.unpackJSON(strValue)

#+ test cases

class Test_SerNULL(Test_Basis):
    """
    Test cases for the SerNULL class.
    
    Test ids: TEST-T-300, TEST-T-301, TEST-T-302, TEST-T-303, TEST-T-310 and
    TEST-T-311
    Covers requrements: REQ-FUN-302, REQ-FUN-310, REQ-FUN-311, REQ-AWM-303,
    REQ-AWM-304 and REQ-AWM-305
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        super().setUpClass()
        cls.TestClass = SerNULL
    
    def test_init(self):
        """
        Checks instantiation with a single argument, which should be simply
        ignored.
        
        Test ID: TEST-T-311
        
        Covers requirement: REQ-FUN-311
        
        Version 1.0.0.0
        """
        for gValue in (1, 1.0, int, str, "1", None, bool, True, [1], (1,2)):
            objTest = self.TestClass(gValue)
            self.assertIsNone(objTest.getNative())
            self.assertEqual(objTest.packJSON(), "null")
            self.assertEqual(objTest.packBytes(), b'')
            del objTest
    
    def test_main_functionality(self):
        """
        Checks the basic functionality - default instantiation, unpacking from
        JSON and bytestring as well as serialization into JSON and bytestring.
        
        Test ID: TEST-T-310
        
        Covers requirement: REQ-FUN-310
        
        Version 1.0.0.0
        """
        for objTest in (self.TestClass(), self.TestClass.unpackBytes(b''),
                                            self.TestClass.unpackJSON("null")):
            self.assertIsNone(objTest.getNative())
            self.assertEqual(objTest.packJSON(), "null")
            self.assertEqual(objTest.packBytes(), b'')
            del objTest
    
    def test_unpackBytes_ValueError(self):
        """
        Checks that the data sanity checks are performed.
        
        Test ID: TEST-T-303
        
        Covers requirement: REQ-AWM-304
        
        Version 1.0.0.0
        """
        #any non-empty bytestring!
        for strValue in (b'1', b'abc', b'\x00'):
            with self.assertRaises(ValueError):
                self.TestClass.unpackBytes(strValue)
    
    def test_unpackJSON_TypeError(self):
        """
        Checks that unpackJSON method raises sub-class of TypeError if the
        input is not a string, or it is a proper JSON string, but not evaluating
        into a native Python object compatible with the test class structure.
        
        Test ID: TEST-T-302
        
        Covers requirement: REQ-AWM-303
        
        Version 1.0.0.0
        """
        super().test_unpackJSON_TypeError()
        #proper JSON, but not compatible types
        for gValue in ('true', '1', '"a"', '[1, 2]', '{"a" : 1}'):
            with self.assertRaises(TypeError):
                self.TestClass.unpackJSON(gValue)

class Test_SerStruct(Test_Basis):
    """
    Test cases for the SerStruct class.
    
    Test ids: TEST-T-300, TEST-T-301, TEST-T-302, TEST-T-303, ...
    Covers requrements: REQ-FUN-302, ... ,  REQ-AWM-303,
    REQ-AWM-304 and REQ-AWM-305
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        super().setUpClass()
        cls.TestClass = SerStruct
    
    def test_unpackJSON_TypeError(self):
        """
        Checks that unpackJSON method raises sub-class of TypeError if the
        input is not a string, or it is a proper JSON string, but not evaluating
        into a native Python object compatible with the test class structure.
        
        Test ID: TEST-T-302
        
        Covers requirement: REQ-AWM-303
        
        Version 1.0.0.0
        """
        super().test_unpackJSON_TypeError()
        #proper JSON, but not compatible types
        for gValue in ('true', '1', '"a"', '[1, 2]', 'null'):
            with self.assertRaises(TypeError):
                self.TestClass.unpackJSON(gValue)
    
    def test_init_TypeError(self):
        """
        Checks that the TypeError is raised if the wrong type argument is
        passed into the initialization method of the class being tested.
        
        Test ID: TEST-T-304
        
        Covers requirement: REQ-AWM-301
        
        Version 1.0.0.0
        """
        for gValue in (1, 2.0, 'a', int, float, str, tuple, list, dict, bool,
                        True, SerNULL(), SerArray(), SerDynamicArray(), b'a',
                        [1, 2, 3], (1, 2, 3)):
            with self.assertRaises(TypeError, msg='{}'.format(gValue)):
                self.TestClass(gValue)

class Test_SerArray(Test_Basis):
    """
    Test cases for the SerArray class.
    
    Test ids: TEST-T-300, TEST-T-301, TEST-T-302, TEST-T-303, ...
    Covers requrements: REQ-FUN-302, ... ,  REQ-AWM-303,
    REQ-AWM-304 and REQ-AWM-305
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        super().setUpClass()
        cls.TestClass = SerArray
    
    def test_unpackJSON_TypeError(self):
        """
        Checks that unpackJSON method raises sub-class of TypeError if the
        input is not a string, or it is a proper JSON string, but not evaluating
        into a native Python object compatible with the test class structure.
        
        Test ID: TEST-T-302
        
        Covers requirement: REQ-AWM-303
        
        Version 1.0.0.0
        """
        super().test_unpackJSON_TypeError()
        #proper JSON, but not compatible types
        for gValue in ('true', '1', '"a"', 'null', '{"a" : 1}'):
            with self.assertRaises(TypeError):
                self.TestClass.unpackJSON(gValue)
    
    def test_init_TypeError(self):
        """
        Checks that the TypeError is raised if the wrong type argument is
        passed into the initialization method of the class being tested.
        
        Test ID: TEST-T-304
        
        Covers requirement: REQ-AWM-301
        
        Version 1.0.0.0
        """
        for gValue in (1, 2.0, 'a', int, float, str, tuple, list, dict, bool,
                        b'a', True, SerNULL(), SerStruct(), {'a' : 1}):
            with self.assertRaises(TypeError, msg='{}'.format(gValue)):
                self.TestClass(gValue)

class Test_SerDynamicArray(Test_SerArray):
    """
    Test cases for the SerDynamicArray class.
    
    Test ids: TEST-T-300, TEST-T-301, TEST-T-302, TEST-T-303, ...
    Covers requrements: REQ-FUN-302, ... ,  REQ-AWM-303,
    REQ-AWM-304 and REQ-AWM-305
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        super().setUpClass()
        cls.TestClass = SerDynamicArray


#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_SerNULL)
TestSuite2 = unittest.TestLoader().loadTestsFromTestCase(Test_SerStruct)
TestSuite3 = unittest.TestLoader().loadTestsFromTestCase(Test_SerArray)
TestSuite4 = unittest.TestLoader().loadTestsFromTestCase(Test_SerDynamicArray)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, TestSuite2, TestSuite3, TestSuite4])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.serialization module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)