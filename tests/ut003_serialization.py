#usr/bin/python3
"""
Module com_lib.tests.ut003_serialization

Unit tests for com_lib.serialization

Covered classes:
    SimpleCOM_API
"""

__version__ = "1.0.0.0"
__date__ = "25-10-2021"
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

#++ proper declaration
class BaseStruct(SerStruct):
    
    _Fields = (
        ('a', ctypes.c_short),
        ('b', ctypes.c_float)
    )

class BaseArray(SerArray):
    
    _ElementType = ctypes.c_short
    
    _Length = 2

class BaseDynamicArray(SerDynamicArray):
    
    _ElementType = ctypes.c_short

class NestedStruct(SerStruct):
    
    _Fields = (
        ('a', ctypes.c_short),
        ('b', ctypes.c_float),
        ('c', BaseArray)
    )

class NestedDynamicStruct(SerStruct):
    
    _Fields = (
        ('a', ctypes.c_short),
        ('b', ctypes.c_float),
        ('c', BaseDynamicArray)
    )

class NestedArray(SerArray):
    
    _ElementType = BaseStruct
    
    _Length = 2

class NestedDynamicArray(SerDynamicArray):
    
    _ElementType = BaseStruct

class ComplexStruct(SerStruct):
    
    _Fields = (
        ('a', ctypes.c_short),
        ('b', ctypes.c_float),
        ('c', NestedDynamicStruct)
    )

class ArrayArray(SerArray):

    _ElementType = BaseArray
    
    _Length = 3

class DynamicArrayArray(SerDynamicArray):

    _ElementType = BaseArray

#+ bad declaration

class BadStruct1(SerStruct): #not string key
    
    _Fields = (
        (1, ctypes.c_short),
        ('b', ctypes.c_float)
    )

class BadStruct2(SerStruct): #not a type
    
    _Fields = (
        ('a', 1), 
        ('b', ctypes.c_float)
    )

class BadStruct3(SerStruct): #improper type
    
    _Fields = (
        ('a', ctypes.c_short), 
        ('b', float)
    )

class BadStruct4(SerStruct): #dynamic element not in a final position
    
    _Fields = (
        ('a', BaseDynamicArray), 
        ('b', ctypes.c_float)
    )

class BadStruct5(SerStruct): #dynamic element not in a final position
    
    _Fields = (
        ('a', ComplexStruct), 
        ('b', ctypes.c_float)
    )

class BadStruct6(SerStruct): #nested bad declared class
    
    _Fields = (
        ('a', BadStruct1), 
        ('b', ctypes.c_float)
    )

class BadArray1(SerArray): #negative array length
    
    _Length = -2

class BadArray2(SerArray): #zero array length
    
    _Length = 0

class BadArray3(SerArray): #wrong type of the value
    
    _Length = ctypes.c_int(1)

class BadArray4(SerArray): #wrong type of the value
    
    _Length = 1.0

class BadArray5(SerArray): #wrong type of the value - not an instance
    
    _Length = int


class BadArray6(SerArray): #not a type for the elements type
    
    _Length = 2
    
    _ElementType = 1

class BadArray7(SerArray): #not a proper type for the elements type
    
    _Length = 2
    
    _ElementType = int

class BadArray8(SerArray): #not a fixed length type for the elements type
    
    _Length = 2
    
    _ElementType = BaseDynamicArray

class BadArray9(SerArray): #not a fixed length type for the elements type
    
    _Length = 2
    
    _ElementType = ComplexStruct

class BadArray10(SerArray): #bad declaration of the nested element type
    
    _Length = 2
    
    _ElementType = BadStruct6

class BadStruct7(SerStruct): #nested bad declared class
    
    _Fields = (
        ('a', BadArray10), 
        ('b', ctypes.c_float)
    )

class BadDynamicArray1(SerDynamicArray): #not a type for the elements type
    
    _ElementType = 1

class BadDynamicArray2(SerDynamicArray): #not a proper type for the elements type
    
    _ElementType = int

class BadDynamicArray3(SerDynamicArray): #not a fixed length type for the elements type
    
    _ElementType = BaseDynamicArray

class BadDynamicArray4(SerDynamicArray): #not a fixed length type for the elements type
    
    _ElementType = ComplexStruct

class BadDynamicArray5(SerDynamicArray): #bad declaration of the nested element type
    
    _ElementType = BadStruct6

#+ tests prototype class

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
        cls.TestClass = ComplexStruct
    
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
    
    def test_Additional_API(self):
        """
        Checks the implementation of the required additional API.

        Test ID: TEST-T-340

        Covers requirements: REQ-FUN-340, REQ-FUN-348.

        Version 1.0.0.0
        """
        self.assertIsInstance(BaseStruct.getMinSize, types.MethodType)
        self.assertIsInstance(BaseStruct.getCurrentSize, types.FunctionType)
        objTest = BaseStruct()
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 6)
        objTest = BaseStruct({'a' : 1})
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 6)
        objTest = BaseStruct({'b' : 1.0})
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 6)
        objTest = BaseStruct({'a' : 1, 'b' : 1.0, 'c' : 1})
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 6)
        self.assertIsInstance(NestedStruct.getMinSize, types.MethodType)
        self.assertIsInstance(NestedStruct.getCurrentSize, types.FunctionType)
        objTest = NestedStruct()
        self.assertEqual(objTest.getMinSize(), 10)
        self.assertEqual(objTest.getCurrentSize(),10)
        objTest = NestedStruct({'a' : 1})
        self.assertEqual(objTest.getMinSize(), 10)
        self.assertEqual(objTest.getCurrentSize(), 10)
        objTest = NestedStruct({'b' : 1.0})
        self.assertEqual(objTest.getMinSize(), 10)
        self.assertEqual(objTest.getCurrentSize(), 10)
        objTest = NestedStruct({'a' : 1, 'b' : 1.0, 'c' : [1], 'd' : 1})
        self.assertEqual(objTest.getMinSize(), 10)
        self.assertEqual(objTest.getCurrentSize(), 10)
        self.assertIsInstance(NestedDynamicStruct.getMinSize, types.MethodType)
        self.assertIsInstance(NestedDynamicStruct.getCurrentSize,
                                                            types.FunctionType)
        objTest = NestedDynamicStruct()
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(),6)
        objTest = NestedDynamicStruct({'a' : 1})
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 6)
        objTest = NestedDynamicStruct({'b' : 1.0})
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 6)
        objTest = NestedDynamicStruct({'a' : 1, 'b' : 1.0, 'c' : [1], 'd' : 1})
        self.assertEqual(objTest.getMinSize(), 6)
        self.assertEqual(objTest.getCurrentSize(), 8)
        self.assertIsInstance(ComplexStruct.getMinSize, types.MethodType)
        self.assertIsInstance(ComplexStruct.getCurrentSize, types.FunctionType)
        objTest = ComplexStruct()
        self.assertEqual(objTest.getMinSize(), 12)
        self.assertEqual(objTest.getCurrentSize(),12)
        objTest = ComplexStruct({'a' : 1})
        self.assertEqual(objTest.getMinSize(), 12)
        self.assertEqual(objTest.getCurrentSize(), 12)
        objTest = ComplexStruct({'b' : 1.0})
        self.assertEqual(objTest.getMinSize(), 12)
        self.assertEqual(objTest.getCurrentSize(), 12)
        objTest = ComplexStruct({'a' : 1, 'b' : 1.0, 'c' : {'c' : [1], 'd' : 1},
                                                                    'd' : 1})
        self.assertEqual(objTest.getMinSize(), 12)
        self.assertEqual(objTest.getCurrentSize(), 14)
    
    def test_init_TypeError(self):
        """
        Checks that the TypeError is raised if the wrong type argument is
        passed into the initialization method of the class being tested.
        
        Test ID: TEST-T-304
        
        Covers requirement: REQ-AWM-301
        
        Version 1.0.0.0
        """
        for gValue in (1, 2.0, 'a', int, float, str, tuple, list, dict, bool,
                        True, SerNULL(), BaseArray(), SerDynamicArray(), b'a',
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
        cls.TestClass = NestedArray
    
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
    
    def test_Additional_API(self):
        """
        Checks the implementation of the required additional API.

        Test ID: TEST-T-320

        Covers requirements: REQ-FUN-320, REQ-FUN-328.

        Version 1.0.0.0
        """
        objTest = BaseArray()
        self.assertIsInstance(objTest, BaseArray)
        self.assertEqual(len(objTest), 2)
        objTest = BaseArray([1, 1])
        self.assertIsInstance(objTest, BaseArray)
        self.assertEqual(len(objTest), 2)
        objTest = BaseArray([1])
        self.assertIsInstance(objTest, BaseArray)
        self.assertEqual(len(objTest), 2)
        objTest = BaseArray([1, 1, 1])
        self.assertIsInstance(objTest, BaseArray)
        self.assertEqual(len(objTest), 2)
        objTest = NestedArray()
        self.assertIsInstance(objTest, NestedArray)
        self.assertEqual(len(objTest), 2)
        objTest = NestedArray([{'a' : 1, 'b' : 1.0}, {'a' : 1, 'b' : 1.0}])
        self.assertIsInstance(objTest, NestedArray)
        self.assertEqual(len(objTest), 2)
        objTest = NestedArray([{'a' : 1, 'b' : 1.0}])
        self.assertIsInstance(objTest, NestedArray)
        self.assertEqual(len(objTest), 2)
        objTest = NestedArray([{'a' : 1, 'b' : 1.0}, {'a' : 1, 'b' : 1.0},
                                                        {'a' : 1, 'b' : 1.0}])
        self.assertIsInstance(objTest, NestedArray)
        self.assertEqual(len(objTest), 2)
        objTest = ArrayArray()
        self.assertIsInstance(objTest, ArrayArray)
        self.assertEqual(len(objTest), 3)
        objTest = ArrayArray([[1, 1], [1, 1], [1, 1]])
        self.assertIsInstance(objTest, ArrayArray)
        self.assertEqual(len(objTest), 3)
        objTest = ArrayArray([[1, 1], [1, 1]])
        self.assertIsInstance(objTest, ArrayArray)
        self.assertEqual(len(objTest), 3)
        objTest = ArrayArray([[1, 1], [1, 1], [1, 1], [1, 1]])
        self.assertIsInstance(objTest, ArrayArray)
        self.assertEqual(len(objTest), 3)

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
        cls.TestClass = NestedDynamicArray
    
    def test_Additional_API(self):
        """
        Checks the implementation of the required additional API.

        Test ID: TEST-T-330

        Covers requirements: REQ-FUN-330, REQ-FUN-338.

        Version 1.0.0.0
        """
        self.assertIsInstance(BaseDynamicArray.getElementSize,
                                                            types.MethodType)
        objTest = BaseDynamicArray()
        self.assertIsInstance(objTest, BaseDynamicArray)
        self.assertEqual(len(objTest), 0)
        self.assertEqual(objTest.getElementSize(), 2)
        objTest = BaseDynamicArray([1, 1])
        self.assertIsInstance(objTest, BaseDynamicArray)
        self.assertEqual(len(objTest), 2)
        self.assertEqual(objTest.getElementSize(), 2)
        objTest = BaseDynamicArray([1])
        self.assertIsInstance(objTest, BaseDynamicArray)
        self.assertEqual(len(objTest), 1)
        self.assertEqual(objTest.getElementSize(), 2)
        objTest = BaseDynamicArray([1, 1, 1])
        self.assertIsInstance(objTest, BaseDynamicArray)
        self.assertEqual(len(objTest), 3)
        self.assertEqual(objTest.getElementSize(), 2)
        self.assertIsInstance(NestedDynamicArray.getElementSize,
                                                            types.MethodType)
        objTest = NestedDynamicArray()
        self.assertIsInstance(objTest, NestedDynamicArray)
        self.assertEqual(len(objTest), 0)
        self.assertEqual(objTest.getElementSize(), 6)
        objTest = NestedDynamicArray([{'a' : 1, 'b' : 1.0},
                                                        {'a' : 1, 'b' : 1.0}])
        self.assertIsInstance(objTest, NestedDynamicArray)
        self.assertEqual(len(objTest), 2)
        self.assertEqual(objTest.getElementSize(), 6)
        objTest = NestedDynamicArray([{'a' : 1, 'b' : 1.0}])
        self.assertIsInstance(objTest, NestedDynamicArray)
        self.assertEqual(len(objTest), 1)
        self.assertEqual(objTest.getElementSize(), 6)
        objTest = NestedDynamicArray([{'a' : 1, 'b' : 1.0},
                                {'a' : 1, 'b' : 1.0}, {'a' : 1, 'b' : 1.0}])
        self.assertIsInstance(objTest, NestedDynamicArray)
        self.assertEqual(len(objTest), 3)
        self.assertEqual(objTest.getElementSize(), 6)
        self.assertIsInstance(DynamicArrayArray.getElementSize,
                                                            types.MethodType)
        objTest = DynamicArrayArray()
        self.assertIsInstance(objTest, DynamicArrayArray)
        self.assertEqual(len(objTest), 0)
        self.assertEqual(objTest.getElementSize(), 4)
        objTest = DynamicArrayArray([[1, 1], [1, 1], [1, 1]])
        self.assertIsInstance(objTest, DynamicArrayArray)
        self.assertEqual(len(objTest), 3)
        self.assertEqual(objTest.getElementSize(), 4)
        objTest = DynamicArrayArray([[1, 1], [1, 1]])
        self.assertIsInstance(objTest, DynamicArrayArray)
        self.assertEqual(len(objTest), 2)
        self.assertEqual(objTest.getElementSize(), 4)
        objTest = DynamicArrayArray([[1, 1], [1, 1], [1, 1], [1, 1]])
        self.assertIsInstance(objTest, DynamicArrayArray)
        self.assertEqual(len(objTest), 4)
        self.assertEqual(objTest.getElementSize(), 4)

class Test_BadDeclarion(unittest.TestCase):
    """
    Test cases for sanity checks on the declaration of the data structure.
    
    Test id: TEST-T-305
    Covers requrements: REQ-AWM-300
    
    Version 1.0.0.0
    """
    
    def test_BadStructures(self):
        """
        Specific tests for the bad declaration of the struct data structure.
        
        Test id: TEST-T-305
        
        Covers requrements: REQ-AWM-300
        
        Version 1.0.0.0
        """
        for tTest in (BadStruct1, BadStruct2, BadStruct3, BadStruct4,
                                            BadStruct5, BadStruct6, BadStruct7):
            ClassName = tTest.__name__
            #instantiation
            with self.assertRaises(TypeError,
                                        msg = '{}.__init__'.format(ClassName)):
                tTest()
            #getSize()
            with self.assertRaises(TypeError,
                                        msg = '{}.getSize()'.format(ClassName)):
                tTest.getSize()
            #unpackBytes()
            with self.assertRaises(TypeError,
                                    msg = '{}.unpackBytes()'.format(ClassName)):
                tTest.unpackBytes(b'\x00')
            #unpackJSON()
            with self.assertRaises(TypeError,
                                    msg = '{}.unpackJSON()'.format(ClassName)):
                tTest.unpackJSON('{"a": 1}')
            #getMinSize()
            with self.assertRaises(TypeError,
                                    msg = '{}.getMinSize()'.format(ClassName)):
                tTest.getMinSize()
    
    def test_BadArrays(self):
        """
        Specific tests for the bad declaration of the fixed length array data
        structure.
        
        Test id: TEST-T-305
        
        Covers requrements: REQ-AWM-300
        
        Version 1.0.0.0
        """
        for tTest in (BadArray1, BadArray2, BadArray3, BadArray4, BadArray5,
                        BadArray6, BadArray7, BadArray8, BadArray9, BadArray10):
            ClassName = tTest.__name__
            #instantiation
            with self.assertRaises(TypeError,
                                        msg = '{}.__init__'.format(ClassName)):
                tTest()
            #getSize()
            with self.assertRaises(TypeError,
                                        msg = '{}.getSize()'.format(ClassName)):
                tTest.getSize()
            #unpackBytes()
            with self.assertRaises(TypeError,
                                    msg = '{}.unpackBytes()'.format(ClassName)):
                tTest.unpackBytes(b'\x00')
            #unpackJSON()
            with self.assertRaises(TypeError,
                                    msg = '{}.unpackJSON()'.format(ClassName)):
                tTest.unpackJSON('[1, 2]')
    
    def test_BadDynamicArrays(self):
        """
        Specific tests for the bad declaration of the dynamic length array data
        structure.
        
        Test id: TEST-T-305
        
        Covers requrements: REQ-AWM-300
        
        Version 1.0.0.0
        """
        for tTest in (BadDynamicArray1, BadDynamicArray2, BadDynamicArray3,
                                            BadDynamicArray4, BadDynamicArray5):
            ClassName = tTest.__name__
            #instantiation
            with self.assertRaises(TypeError,
                                        msg = '{}.__init__'.format(ClassName)):
                tTest()
            #getSize()
            with self.assertRaises(TypeError,
                                        msg = '{}.getSize()'.format(ClassName)):
                tTest.getSize()
            #unpackBytes()
            with self.assertRaises(TypeError,
                                    msg = '{}.unpackBytes()'.format(ClassName)):
                tTest.unpackBytes(b'\x00')
            #unpackJSON()
            with self.assertRaises(TypeError,
                                    msg = '{}.unpackJSON()'.format(ClassName)):
                tTest.unpackJSON('[1, 2]')
            #getElementSize()
            with self.assertRaises(TypeError,
                                msg = '{}.getElementSize()'.format(ClassName)):
                tTest.getElementSize()

#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_SerNULL)
TestSuite2 = unittest.TestLoader().loadTestsFromTestCase(Test_SerStruct)
TestSuite3 = unittest.TestLoader().loadTestsFromTestCase(Test_SerArray)
TestSuite4 = unittest.TestLoader().loadTestsFromTestCase(Test_SerDynamicArray)
TestSuite5 = unittest.TestLoader().loadTestsFromTestCase(Test_BadDeclarion)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, TestSuite2, TestSuite3, TestSuite4, TestSuite5])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.serialization module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)