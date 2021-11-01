#usr/bin/python3
"""
Module com_lib.tests.ut002_serial_port_com

Unit tests for com_lib.serial_port_com.

Covered classes:
    SimpleCOM_API
"""

__version__ = "1.1.0.0"
__date__ = "01-11-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import unittest
import time

#+ 3rd party libraries

from serial import SerialException, SerialTimeoutException

#+ my libraries

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ helper modules

from com_lib.mock_serial import MockSerial

from com_lib.serialization import SerNULL

from com_lib.tests.ut003_serialization import ComplexStruct, NestedArray
from com_lib.tests.ut003_serialization import DynamicArrayArray

#++ module to be tested

from com_lib.serial_port_com import SimpleCOM_API

#classes

#+ helper classes

class MockCom(SimpleCOM_API):
    """
    Sub-classes the class to be tested and replaces the actual serial.Serial
    class by the mock serial class for the testing.
    
    Version 1.0.0.0
    """
    
    #class attributes
    
    _BaseAPI = MockSerial

#+ test cases

class Test_SimpleCOM_API(unittest.TestCase):
    """
    Test cases for the SimpleCOM_API class.
    
    Test ids: TEST-T-210, TEST-T-220, TEST-T-221, TEST-T-222, TEST-T-223,
    TEST-T-224, TEST-T-225, TEST-T-226, TEST-T-227, TEST-T-228
    Covers requrements: REQ-FUN-210, REQ-FUN-220, REQ-FUN-221, REQ-FUN-222,
    REQ-FUN-223, REQ-FUN-224, REQ-FUN-225, REQ-FUN-226, REQ-FUN-227,
    REQ-FUN-228, REQ-AWM-220, REQ-AWM-221, REQ-AWM-222, REQ-AWM-223, REQ-AWM-224
    
    Version 1.1.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        cls.TestClass = MockCom
    
    def test_Reopening(self):
        """
        Checks the proper assignment and preservation of the settings upon
        re-opening.
        
        Test id: TEST-T-221
        Requirement ids: REQ-FUN-221, REQ-FUN-222, REQ-FUN-223
        
        Version 1.0.0.0
        """
        objTest = self.TestClass('mock', port = 'whatever', timeout = None,
                                    write_timeout = None, baudrate = 115200,
                                    xonxoff = True, something = 1)
        dictRef = {'port' : 'mock', 'timeout' : 0, 'write_timeout' : 0,
                    'baudrate' : 115200, 'xonxoff' : True, 'something' : 1}
        self.assertTrue(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        objTest.close()
        self.assertFalse(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        objTest.open()
        self.assertTrue(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        del objTest
        objTest = self.TestClass('mock2')
        dictRef = {'port' : 'mock2', 'timeout' : 0, 'write_timeout' : 0,
                    'baudrate' : 9600}
        self.assertTrue(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        for Index in range(10):
            objTest.send('test_{}'.format(Index))
        with self.assertRaises(SerialTimeoutException):
            objTest.sendSync('test', ReturnType = str, Timeout = 0.1)
        self.assertFalse(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        Response, Index = objTest.sendSync('test', ReturnType = str, Timeout= 1)
        self.assertTrue(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        self.assertEqual(Response, 'test')
        self.assertEqual(Index, 1)
        objTest.send('test')
        time.sleep(1)
        with self.assertRaises(TypeError):
            objTest.send(1)
        self.assertFalse(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        time.sleep(1)
        Result = objTest.getResponse()
        self.assertIsNone(Result)
        self.assertTrue(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        objTest.send('test')
        time.sleep(1)
        with self.assertRaises(TypeError):
            objTest.getResponse(ReturnType = int)
        self.assertFalse(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        Response, Index = objTest.sendSync('final', ReturnType = str)
        self.assertEqual(Response, 'final')
        self.assertEqual(Index, 1)
        self.assertTrue(objTest.IsOpen)
        self.assertDictEqual(objTest.Settings, dictRef)
        del objTest
    
    def test_Asynchronous(self):
        """
        Checks the sending and receiving the data in the asynchronous mode.
        
        Test id: TEST-T-222
        Requirement ids: REQ-FUN-224, REQ-FUN-225
        
        Version 1.0.0.0
        """
        for Baudrate in [50, 2400, None, 115200]:
            if not (Baudrate is None):
                objTest = self.TestClass('mock', baudrate = Baudrate)
            else:
                objTest = self.TestClass('mock')
            Sent = []
            for Index in range(3):
                Message = 'test_{}'.format(Index)
                SentIndex = objTest.send(Message)
                Sent.append((Message, SentIndex))
            for Message, Index in Sent:
                Result = None
                while Result is None:
                    Result = objTest.getResponse(str)
                self.assertEqual(Result[0], Message)
                self.assertEqual(Result[1], Index)
            for _ in range(100):
                Result = objTest.getResponse(str)
                self.assertIsNone(Result)
            del objTest
    
    def test_SynchronousBlocking(self):
        """
        Checks the sending and receiving the data in the synchronous blocking
        mode.
        
        Test id: TEST-T-223
        Requirement ids: REQ-FUN-226
        
        Version 1.0.0.0
        """
        for Baudrate in [50, 2400, None, 115200]:
            if not (Baudrate is None):
                objTest = self.TestClass('mock', baudrate = Baudrate)
            else:
                objTest = self.TestClass('mock')
            for Index in range(2):
                Message = 'test_{}'.format(Index)
                objTest.send(Message)
            Message = 'test_2'
            Result, Index = objTest.sendSync(Message, str)
            self.assertEqual(Result, Message)
            self.assertEqual(Index, 3)
            for _ in range(100):
                Result = objTest.getResponse(str)
                self.assertIsNone(Result)
            del objTest
    
    def test_SynchronousTimeout(self):
        """
        Checks the sending and receiving the data in the synchronous timeout
        mode and re-opening of the port after timeout exception.
        
        Test id: TEST-T-223
        Requirement ids: REQ-FUN-222, REQ-FUN-226, REQ-AMW-222
        
        Version 1.0.0.0
        """
        Message = 'test_x'
        objTest = self.TestClass('mock', baudrate = 115200)
        Result, Index = objTest.sendSync(Message, str, 0.1) #100 ms - timeout
        self.assertEqual(Result, Message)
        self.assertEqual(Index, 1)
        del objTest
        objTest = self.TestClass('mock', baudrate = 2400)
        with self.assertRaises(SerialTimeoutException):
            Result, Index = objTest.sendSync(Message, str, 0.1)
        #should be able to gracefully recover
        objTest.open()
        Result, Index = objTest.sendSync(Message, str, 0) #blocking!
        self.assertEqual(Result, Message)
        self.assertEqual(Index, 1)
        Message = 'test_y'
        Result, Index = objTest.sendSync(Message, str) #blocking!
        self.assertEqual(Result, Message)
        self.assertEqual(Index, 2)
        Message = 'test_z'
        Result, Index = objTest.sendSync(Message, str, 0.2) #200 ms - timeout
        self.assertEqual(Result, Message)
        self.assertEqual(Index, 3)
        del objTest
    
    def test_SupportedTypes(self):
        """
        Checks the support for the input and output types.
        
        Test id: TEST-T-224
        Requirement ids: REQ-FUN-228
        
        Version 2.0.0.0
        """
        objTest = self.TestClass('mock', baudrate = 115200)
        strMessage = 'codec\u0000test'
        self.assertIsInstance(strMessage, str)
        objTest.send(strMessage)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(str)
        self.assertIsInstance(Response, str)
        self.assertEqual(Response, strMessage)
        self.assertEqual(Index, 1)
        Response, Index = objTest.sendSync(strMessage, str)
        self.assertIsInstance(Response, str)
        self.assertEqual(Response, strMessage)
        self.assertEqual(Index, 2)
        bsMessage = strMessage.encode('utf_8')
        self.assertIsInstance(bsMessage, bytes)
        objTest.send(bsMessage)
        time.sleep(0.5)
        Response, Index = objTest.getResponse()
        self.assertIsInstance(Response, bytes)
        self.assertEqual(Response, bsMessage)
        self.assertEqual(Index, 3)
        Response, Index = objTest.sendSync(bsMessage)
        self.assertIsInstance(Response, bytes)
        self.assertEqual(Response, bsMessage)
        self.assertEqual(Index, 4)
        objTest.send(bsMessage)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(bytes)
        self.assertIsInstance(Response, bytes)
        self.assertEqual(Response, bsMessage)
        self.assertEqual(Index, 5)
        Response, Index = objTest.sendSync(bsMessage, bytes)
        self.assertIsInstance(Response, bytes)
        self.assertEqual(Response, bsMessage)
        self.assertEqual(Index, 6)
        baMessage = bytearray(bsMessage)
        self.assertIsInstance(baMessage, bytearray)
        objTest.send(bsMessage)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(bytearray)
        self.assertIsInstance(Response, bytearray)
        self.assertEqual(Response, baMessage)
        self.assertEqual(Index, 7)
        Response, Index = objTest.sendSync(baMessage, bytearray)
        self.assertIsInstance(Response, bytearray)
        self.assertEqual(Response, baMessage)
        self.assertEqual(Index, 8)
        Data = SerNULL()
        objTest.send(Data)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(SerNULL)
        self.assertIsInstance(Response, SerNULL)
        self.assertIsNone(Response.getNative())
        self.assertEqual(Index, 9)
        del Response
        Response, Index = objTest.sendSync(Data, SerNULL)
        self.assertIsInstance(Response, SerNULL)
        self.assertIsNone(Response.getNative())
        self.assertEqual(Index, 10)
        del Data
        del Response
        gNative = {'a' : 1, 'b' : 1.0, 'c' : {'a' : 2, 'b' : 1.0, 'c' : [3, 4]}}
        Data = ComplexStruct(gNative)
        objTest.send(Data)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(ComplexStruct)
        self.assertIsInstance(Response, ComplexStruct)
        self.assertEqual(Response.getNative(), gNative)
        self.assertEqual(Index, 11)
        del Response
        Response, Index = objTest.sendSync(Data, ComplexStruct)
        self.assertIsInstance(Response, ComplexStruct)
        self.assertEqual(Response.getNative(), gNative)
        self.assertEqual(Index, 12)
        del Data
        del Response
        gNative = [{'a' : 1, 'b' : 1.0}, {'a' : 2, 'b' : 1.0}]
        Data = NestedArray(gNative)
        objTest.send(Data)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(NestedArray)
        self.assertIsInstance(Response, NestedArray)
        self.assertEqual(Response.getNative(), gNative)
        self.assertEqual(Index, 13)
        del Response
        Response, Index = objTest.sendSync(Data, NestedArray)
        self.assertIsInstance(Response, NestedArray)
        self.assertEqual(Response.getNative(), gNative)
        self.assertEqual(Index, 14)
        del Data
        del Response
        gNative = [[1, 2], [3, 4], [5, 6]]
        Data = DynamicArrayArray(gNative)
        objTest.send(Data)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(DynamicArrayArray)
        self.assertIsInstance(Response, DynamicArrayArray)
        self.assertEqual(Response.getNative(), gNative)
        self.assertEqual(Index, 15)
        del Response
        Response, Index = objTest.sendSync(Data, DynamicArrayArray)
        self.assertIsInstance(Response, DynamicArrayArray)
        self.assertEqual(Response.getNative(), gNative)
        self.assertEqual(Index, 16)
        del Data
        del Response
        del objTest
    
    def test_NoExceptions(self):
        """
        Checks the unnecessary exceptions are not raised - the action is ignored
        or the port is automatically re-opened
        
        Test id: TEST-T-225
        Requirement ids: REQ-AWM-220
        
        Version 1.0.0.0
        """
        objTest = self.TestClass('mock', baudrate = 115200)
        self.assertTrue(objTest.IsOpen)
        objTest.send('test')
        self.assertTrue(objTest.IsOpen)
        objTest.open()
        self.assertTrue(objTest.IsOpen)
        time.sleep(0.5)
        Response, Index = objTest.getResponse(str)
        self.assertTrue(objTest.IsOpen)
        self.assertEqual(Response, 'test')
        self.assertEqual(Index, 1)
        objTest.close()
        self.assertFalse(objTest.IsOpen)
        objTest.close()
        self.assertFalse(objTest.IsOpen)
        objTest.send('test')
        self.assertTrue(objTest.IsOpen)
        objTest.close()
        self.assertFalse(objTest.IsOpen)
        time.sleep(0.5)
        Result = objTest.getResponse()
        self.assertIsNone(Result)
        self.assertTrue(objTest.IsOpen)
        objTest.close()
        self.assertFalse(objTest.IsOpen)
        Response, Index = objTest.sendSync('test', str)
        self.assertTrue(objTest.IsOpen)
        self.assertEqual(Response, 'test')
        self.assertEqual(Index, 1)
        del objTest
    
    def test_SerialExceptions(self):
        """
        Checks the SerialException is raised than the port cannot be (re-)
        opened.
        
        Test id: TEST-T-226
        Requirement ids: REQ-AWM-221
        
        Version 1.0.0.0
        """
        with self.assertRaises(SerialException):
            objTest = self.TestClass('unmock')
        objTest = self.TestClass('mock')
        objTest.close()
        objTest._Settings['port'] = 'unmock'
        objTest._Connection = None
        with self.assertRaises(SerialException):
            objTest.open()
        with self.assertRaises(SerialException):
            objTest.send('test')
        with self.assertRaises(SerialException):
            objTest.getResponse()
        with self.assertRaises(SerialException):
            objTest.sendSync('test')
    
    def test_TypeError(self):
        """
        Checks the TypeError is raised or propagated than expected.
        
        Test id: TEST-T-227
        Requirement ids: REQ-AWM-223
        
        Version 1.0.0.0
        """
        for Item in [1, 1.0, b'test', bytearray(b'test'), str, ('a', ), ['a'],
                            int, float, list, tuple, bytes, bytearray, bool]:
            with self.assertRaises(TypeError):
                self.TestClass(Item)
        for Item in ['1', 1.0, b'test', bytearray(b'test'), str, ('a', ), ['a'],
                            int, float, list, tuple, bytes, bytearray, bool]:
            with self.assertRaises(TypeError):
                self.TestClass('mock', baudrate = Item)
        objTest = self.TestClass('mock')
        for Item in [1, 1.0, str, ('a', ), ['a'], int, float, list, tuple,
                                                        bytes, bytearray, bool]:
            with self.assertRaises(TypeError):
                objTest.send(Item)
            with self.assertRaises(TypeError):
                objTest.sendSync(Item)
        for Item in [1, 1.0, b'test', bytearray(b'test'), ('a', ), ['a'], int,
                                                    float, list, tuple, bool]:
            with self.assertRaises(TypeError):
                objTest.send('a')
                time.sleep(0.5)
                objTest.getResponse(Item)
            with self.assertRaises(TypeError):
                objTest.sendSync('test', Item)
    
    def test_ValueError(self):
        """
        Checks the ValueError is raised or propagated than expected.
        
        Test id: TEST-T-228
        Requirement ids: REQ-AWM-224
        
        Version 1.0.0.0
        """
        with self.assertRaises(ValueError):
            self.TestClass('mock', baudrate = 25)

#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_SimpleCOM_API)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, ])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.serial_port_com module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)