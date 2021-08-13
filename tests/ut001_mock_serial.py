#usr/bin/python3
"""
Module com_lib.tests.ut001_mock_serial

Unit tests for com_lib.mock_serial module. See the requirements RE001 and
test reports TE001 documents.
"""

__version__ = "1.0.0.0"
__date__ = "13-08-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import unittest
import time
from threading import Thread, Event
from queue import Queue, Empty

#+ 3rd party libraries

from serial import SerialException, SerialTimeoutException

#+ modules to be tested

#+ my libraries

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ module to be tested

from com_lib.mock_serial import MockDevice, MockSerial

#+ test cases

class Test_MockDevice(unittest.TestCase):
    """
    Test cases for the com_lib.mock_serial.MockDevice function. The function
    is tested in the main thread as well as in a separate thread!

    The test is time consuming. Be patient.

    Test id: TEST-T-110.
    Covers requirement: REQ-FUN-110
    """

    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 0.1.0.0
        """
        cls.TestFunction = staticmethod(MockDevice)
        cls.BaudRates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400,
                                        4800, 9600, 19200, 38400, 57600, 115200]
        cls.Commands = ['a', 'ab', '1234567890', 'what_ever',
                                                            'anton\u2600антон']
        cls.SendBuffer = Queue()
        cls.ReceiveBuffer = Queue()
        cls.StopSignal = Event()

    @classmethod
    def tearDownClass(cls):
        """
        Global clean-up after all tests are run. Called only once.

        Version 1.0.0.0
        """
        cls.SendBuffer.join()
        cls.ReceiveBuffer.join()
        del cls.SendBuffer
        del cls.ReceiveBuffer
        del cls.StopSignal
    
    def setUp(self):
        """
        Initialization and preparation performed before each test.

        Version 1.0.0.0
        """
        while not self.SendBuffer.empty():
            try:
                self.SendBuffer.get(False)
                self.SendBuffer.task_done()
            except Empty:
                break
        while not self.ReceiveBuffer.empty():
            try:
                self.ReceiveBuffer.get(False)
                self.ReceiveBuffer.task_done()
            except Empty:
                break
        if self.StopSignal.is_set():
            self.StopSignal.clear()
    
    def tearDown(self):
        """
        Cleaning-ip performed after each test.

        Version 1.0.0.0
        """
        while not self.SendBuffer.empty():
            try:
                self.SendBuffer.get(False)
                self.SendBuffer.task_done()
            except Empty:
                break
        while not self.ReceiveBuffer.empty():
            try:
                self.ReceiveBuffer.get(False)
                self.ReceiveBuffer.task_done()
            except Empty:
                break
        if self.StopSignal.is_set():
            self.StopSignal.clear()
    
    def test_NotStarting(self):
        """
        Checks that the tested function exits almost immediately if the
        StopSignal is set regardless of the content of the SendBuffer and the
        set baudrate. The contents of the both buffers shouldn't be modified.

        Version 1.0.0.0
        """
        self.StopSignal.set()
        for Rate in self.BaudRates:
            Delay = 8.0 / Rate
            for Command in self.Commands:
                OutData = Command.encode('utf_8') + b'\x00'
                for Char in OutData:
                    self.SendBuffer.put(Char)
                StartTime = time.time()
                self.TestFunction(self.SendBuffer, self.ReceiveBuffer,
                                                        self.StopSignal, Rate)
                SpentTime = time.time() - StartTime
                self.assertLess(SpentTime, 2 * Delay)
                self.assertTrue(self.ReceiveBuffer.empty())
                Count = 0
                while not self.SendBuffer.empty():
                    try:
                        self.SendBuffer.get(False)
                        Count += 1
                        self.SendBuffer.task_done()
                    except Empty:
                        break
                self.assertEqual(Count, len(OutData))
    
    @unittest.skip
    def test_NotThreaded(self):
        """
        Checks the functionality of the tested function in the not threaded
        manner. Different 'commands' are placed into the SendBuffer encoded
        into UTF-8 bytestring, followed by b'\x00quit\x00'. The function is
        called with the different commands and baudrates. After that the content
        of the ReceiveBuffer is pulled, stripped of the tailing b'\x00', decoded
        using UTF-8 and compared with the initial command. The call is also
        timed; the timing should be comparable to (2 * N + 7) * 8.0 / baudrate,
        where N is the length of the encoded command in bytes, i.e. the time
        required to receive and send back the original command with the tailing
        zero and to receve b'quit\x00'. However, some call overhead may be
        introduced, thus the expected timing interval is between the expected
        value and that value times 1.1 plus 0.01 (10 ms extras!).

        Version 1.0.0.0
        """
        for Rate in self.BaudRates:
            for Command in self.Commands:
                OutData = Command.encode('utf_8')
                N = len(OutData)
                OutData += b'\x00quit\x00'
                ExpectedTime = 8.0 * (2 * N + 7) / Rate
                for Char in OutData:
                    self.SendBuffer.put(Char)
                StartTime = time.time()
                self.TestFunction(self.SendBuffer, self.ReceiveBuffer,
                                                        self.StopSignal, Rate)
                SpentTime = time.time() - StartTime
                self.assertTrue(self.StopSignal.is_set())
                self.assertGreaterEqual(SpentTime, ExpectedTime)
                self.assertLess(SpentTime, 1.1 * ExpectedTime + 0.01)
                self.assertTrue(self.SendBuffer.empty())
                Response = bytearray()
                while not self.ReceiveBuffer.empty():
                    try:
                        Char = self.ReceiveBuffer.get(False)
                        Response.append(Char)
                        self.ReceiveBuffer.task_done()
                    except Empty:
                        break
                StringResponse = Response[:-1].decode(encoding = 'utf_8')
                self.assertEqual(StringResponse, Command)
                self.StopSignal.clear()

    @unittest.skip
    def test_Threaded(self):
        """
        Checks the functionality of the tested function in the threaded manner.
        
        The function to be tested is executed in a separate thread with the
        different values of the baudrate passed.

        Different 'commands' are placed into the SendBuffer encoded into UTF-8
        bytestring, followed by b'\x00'. The ReceiveBuffer is continuously
        checked, pulled and accumulated, untill b'\x00' is received. After that
        the accumulated content is stripped of the tailing b'\x00', decoded
        using UTF-8 and compared with the initial command.
        
        The entire process is timed; the timing should be comparable to
        (N + 1) * 16.0 / baudrate, where N is the length of the encoded command
        in bytes, i.e. the time required to receive and send back the original
        command with the tailing zero. However, some overhead may be introduced
        due to threads switching, on the other hand, the SendBuffer may be
        partially emptied before the full command is sent, thus the expected
        timing interval is between the expected values times 0.75 and that value
        times 1.1 plus 0.02 * N (i.e. 20 ms extra per byte).

        Version 1.0.0.0
        """
        for Rate in self.BaudRates:
            objTest = Thread(target = self.TestFunction,
                                args = (self.SendBuffer, self.ReceiveBuffer,
                                            self.StopSignal, Rate))
            objTest.start()
            for Command in self.Commands:
                OutData = Command.encode('utf_8') + b'\x00'
                N = len(OutData)
                ExpectedTime = 16.0 * N / Rate
                Response = bytearray()
                StartTime = time.time()
                for Char in OutData:
                    self.SendBuffer.put(Char)
                while True:
                    try:
                        Char = self.ReceiveBuffer.get(False)
                        self.ReceiveBuffer.task_done()
                        if Char == 0:
                            break
                        else:
                            Response.append(Char)
                    except Empty:
                        pass
                SpentTime = time.time() - StartTime
                StringResponse = Response.decode(encoding = 'utf_8')
                self.assertEqual(StringResponse, Command)
                self.assertGreaterEqual(SpentTime, 0.75 * ExpectedTime)
                self.assertLess(SpentTime, 1.1 * ExpectedTime + 0.02 * N)
                self.assertTrue(self.SendBuffer.empty())
            for Char in b'quit\x00':
                    self.SendBuffer.put(Char)
            objTest.join()
            self.assertTrue(self.StopSignal.is_set())
            self.assertTrue(self.SendBuffer.empty())
            self.assertTrue(self.ReceiveBuffer.empty())
            self.StopSignal.clear()
    
    def test_Stops(self):
        """
        Checks that the threaded execution of the funtion being tested stops
        when the 'stop' signal is set by the client / consumer thread.

        Version 1.0.0.0
        """
        for Rate in self.BaudRates:
            Delay = 8.0 / Rate
            objTest = Thread(target = self.TestFunction,
                                args = (self.SendBuffer, self.ReceiveBuffer,
                                            self.StopSignal, Rate))
            objTest.start()
            self.SendBuffer.put(33)
            time.sleep(Delay)
            self.StopSignal.set()
            objTest.join()
            self.assertTrue(self.StopSignal.is_set())
            self.assertTrue(self.SendBuffer.empty())
            self.assertTrue(self.ReceiveBuffer.empty())
            self.StopSignal.clear()

class Test_MockSerial(unittest.TestCase):
    """
    Test cases for the com_lib.mock_serial.MockSerial class.
    
    Test ids: TEST-T-120, TEST-T-121, TEST-T-122, TEST-T-123, TEST-T-124,
        TEST-T-125, TEST-T-126, TEST-T-127, TEST-T-128, TEST-T-129, TEST-T-12A
    Covers the requirements: REQ-FUN-120, REQ-FUN-121, REQ-FUN-122, REQ-FUN-123,
        REQ-FUN-124, REQ-FUN-125, REQ-AWM-120, REQ-AWM-121, REQ-AWM-122,
        REQ-AWM-123, REQ-AWM-124, REQ-AWM-125, REQ-AWM-126, REQ-AWM-127 and
        REQ-AWM-128
    
    Version 1.0.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 1.0.0.0
        """
        cls.TestClass = MockSerial
        cls.BadValues = [int, float, str, bytes, bytearray, list, tuple, dict,
                            (1, ), [1], {1 : 1}]
        cls.NotOptionalReal = list(cls.BadValues)
        cls.NotOptionalReal.extend(['whatever', b'whatever'])
        cls.NotOptionalString = list(cls.BadValues)
        cls.NotOptionalString.extend([1, 1.0, b'whatever'])
        cls.NotInteger = list(cls.BadValues)
        cls.NotInteger.extend(['whatever', b'whatever', 1.0, None])
        cls.NotBytes = list(cls.BadValues)
        cls.NotBytes.extend([1, 1.0, 'whatever', None])
    
    def test_HasAttributes(self):
        """
        Checks that an instance of the class being tested has all expected
        attributes required for the minimum API compatibility with the PySerial
        class Serial.

        Test id: TEST-T-120
        Covers requirements: REQ-FUN-120

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock')
        for Attr in ['open', 'close', 'read', 'write', 'port', 'is_open',
                        'in_waiting', 'out_waiting', 'timeout', 'write_timeout',
                                                                    'baudrate']:
            self.assertTrue(hasattr(objTest, Attr),
                                    msg = 'Missing attribute "{}"'.format(Attr))
        del objTest
    
    def test_initOk(self):
        """
        Checks the instantiation with and without keyword arguments.

        Test id: TEST-T-121
        Covers requirements: REQ-FUN-121
        """
        objTest = self.TestClass()
        self.assertIsNone(objTest.port, msg = 'port')
        self.assertIsNone(objTest.timeout, msg = 'timeout')
        self.assertIsNone(objTest.write_timeout, msg = 'write_timeout')
        self.assertEqual(objTest.baudrate, 9600, msg = 'baudrate')
        del objTest
        objTest = self.TestClass(port = 'mock', timeout = 0.5,
                                        write_timeout = 0, baudrate = 115200)
        self.assertEqual(objTest.port, 'mock', msg = 'port')
        self.assertEqual(objTest.timeout, 0.5 , msg = 'timeout')
        self.assertEqual(objTest.write_timeout, 0, msg = 'write_timeout')
        self.assertEqual(objTest.baudrate, 115200, msg = 'baudrate')
        self.assertTrue(objTest.is_open, msg ='is_open')
        del objTest

    def test_init_TypeError(self):
        """
        Checks that TypeError or its sub-class is raised if, at least, one
        recognized keyword argument receives improper type value.

        Test id: TEST-T-122
        Covers requirement: REQ-AWM-120

        Version 1.0.0.0
        """
        for Item in self.NotOptionalString:
            with self.assertRaises(TypeError):
                self.TestClass(port = Item)
        for Item in self.NotInteger:
            with self.assertRaises(TypeError):
                self.TestClass(baudrate = Item)
        for Item in self.NotOptionalReal:
            with self.assertRaises(TypeError):
                self.TestClass(timeout = Item)
        for Item in self.NotOptionalReal:
            with self.assertRaises(TypeError):
                self.TestClass(write_timeout = Item)
    
    def test_init_ValueError(self):
        """
        Checks that ValueError or its sub-class is raised if, at least, one
        recognized keyword argument receives improper value of a proper data
        type.

        Test id: TEST-T-123
        Covers requirement: REQ-AWM-121

        Version 1.0.0.0
        """
        for Item in ['whatever', 'whoever', 'test']:
            with self.assertRaises(SerialException):
                self.TestClass(port = Item)
        for Item in [-50, 0, 60]:
            with self.assertRaises(ValueError):
                self.TestClass(baudrate = Item)
        for Item in [-1, -1.0]:
            with self.assertRaises(ValueError):
                self.TestClass(timeout = Item)
        for Item in [-1, -1.0]:
            with self.assertRaises(ValueError):
                self.TestClass(write_timeout = Item)
    
    def test_port_TypeError(self):
        """
        Checks assignment of improper type to port property.

        Test id: TEST-T-122
        Covers requirement: REQ-AWM-120

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in self.NotOptionalString:
            with self.assertRaises(TypeError):
                objTest.port = Item
        del objTest
    
    def test_baudrate_TypeError(self):
        """
        Checks assignment of improper type to baudrate property.

        Test id: TEST-T-122
        Covers requirement: REQ-AWM-120

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in self.NotInteger:
            with self.assertRaises(TypeError):
                objTest.baudrate = Item
        del objTest
    
    def test_timeout_TypeError(self):
        """
        Checks assignment of improper type to timeout property.

        Test id: TEST-T-122
        Covers requirement: REQ-AWM-120

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in self.NotOptionalReal:
            with self.assertRaises(TypeError):
                objTest.timeout = Item
        del objTest
    
    def test_write_timeout_TypeError(self):
        """
        Checks assignment of improper type to write_timeout property.

        Test id: TEST-T-122
        Covers requirement: REQ-AWM-120

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in self.NotOptionalReal:
            with self.assertRaises(TypeError):
                objTest.write_timeout = Item
        del objTest
    
    def test_port_SerialException(self):
        """
        Checks assignment of improper value to port property.

        Test id: TEST-T-123
        Covers requirement: REQ-AWM-121

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in ['whatever', 'whoever', 'test']:
            with self.assertRaises(SerialException):
                objTest.port = Item
        del objTest
    
    def test_baudrate_ValueError(self):
        """
        Checks assignment of improper value to baudrate property.

        Test id: TEST-T-123
        Covers requirement: REQ-AWM-121

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in [-50, 0, 60]:
            with self.assertRaises(ValueError):
                objTest.baudrate = Item
        del objTest
    
    def test_timeout_ValueError(self):
        """
        Checks assignment of improper value to timeout property.

        Test id: TEST-T-123
        Covers requirement: REQ-AWM-121

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in [-1, -1.0]:
            with self.assertRaises(ValueError):
                objTest.timeout = Item
        del objTest
    
    def test_write_timeout_ValueError(self):
        """
        Checks assignment of improper value to write_timeout property.

        Test id: TEST-T-123
        Covers requirement: REQ-AWM-121

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        for Item in [-1, -1.0]:
            with self.assertRaises(ValueError):
                objTest.write_timeout = Item
        del objTest
    
    def test_SerialException_No_Port(self):
        """
        Checks the open() method without assigned port.

        Test id: TEST-T-124
        Covers requirement: REQ-AWM-122

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.open()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        del objTest
    
    def test_SerialException_AlreadyOpen(self):
        """
        Checks the open() method - re-opening of the already active connection.

        Test id: TEST-T-125
        Covers requirement: REQ-AWM-123

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock')
        self.assertEqual(objTest.port, 'mock')
        self.assertTrue(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.open()
        self.assertEqual(objTest.port, 'mock')
        self.assertFalse(objTest.is_open)
        del objTest
    
    def test_SerialException_AlreadyClosed(self):
        """
        Checks the close() method - closing of the already inactive connection.

        Test id: TEST-T-126
        Covers requirement: REQ-AWM-124

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.close()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        del objTest
    
    def test_SerialException_Inactive(self):
        """
        Checks the inactive connection access limitations.

        Test id: TEST-T-127
        Covers requirement: REQ-AWM-125

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.read()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.read()
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.in_waiting
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        with self.assertRaises(SerialException):
            objTest.out_waiting
        self.assertIsNone(objTest.port)
        self.assertFalse(objTest.is_open)
        del objTest
    
    def test_read_TypeError(self):
        """
        Checks that read() raises TypeError-type exception with non-integer
        argument being passed.

        Test id: TEST-T-128
        Covers requirement: REQ-AWM-126

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock')
        for Item in self.NotInteger:
            self.assertTrue(objTest.is_open)
            with self.assertRaises(TypeError):
                objTest.read(Item)
            self.assertFalse(objTest.is_open)
            self.assertEqual(objTest.port, 'mock')
            objTest.open()
        del objTest
    
    def test_write_TypeError(self):
        """
        Checks that write() raises TypeError-type exception with not bytestring
        (or compatible, e.g. bytearray) argument being passed.

        Test id: TEST-T-128
        Covers requirement: REQ-AWM-126

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock')
        for Item in self.NotBytes:
            self.assertTrue(objTest.is_open)
            with self.assertRaises(TypeError):
                objTest.write(Item)
            self.assertFalse(objTest.is_open)
            self.assertEqual(objTest.port, 'mock')
            objTest.open()
        del objTest
    
    def test_read_ValueError(self):
        """
        Checks that read() raises ValueError-type exception with an integer but
        not positive argument being passed.

        Test id: TEST-T-129
        Covers requirement: REQ-AWM-127

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock')
        for Item in [-1, -5, 0]:
            self.assertTrue(objTest.is_open)
            with self.assertRaises(ValueError):
                objTest.read(Item)
            self.assertFalse(objTest.is_open)
            self.assertEqual(objTest.port, 'mock')
            objTest.open()
        del objTest
    
    def test_Blocking(self):
        """
        Tests the sending and receiving both in the blocking mode.

        Test id: TEST-T-12A
        Covers requirements: REQ-FUN-122, REQ-FUN-123, REQ-FUN-124, REQ-FUN-125
        and REQ-AWM-128

        Version 1.0.0.0
        """
        objTest = self.TestClass()
        self.assertFalse(objTest.is_open)
        self.assertEqual(objTest.baudrate, 9600)
        self.assertIsNone(objTest.port)
        self.assertIsNone(objTest.timeout)
        self.assertIsNone(objTest.write_timeout)
        objTest.baudrate = 2400
        objTest.port = 'mock'
        self.assertTrue(objTest.is_open)
        self.assertEqual(objTest.baudrate, 2400)
        self.assertEqual(objTest.port, 'mock')
        self.assertEqual(objTest.in_waiting, 0)
        self.assertEqual(objTest.out_waiting, 0)
        bsTest = b'test_case\x00'
        t0 = time.time()
        objTest.write(bsTest)
        t1 = time.time()
        out = objTest.out_waiting
        in1 = objTest.in_waiting
        result = objTest.read(10)
        t2 = time.time()
        in2 = objTest.in_waiting
        self.assertEqual(result, bsTest)
        self.assertEqual(out, 0)
        self.assertGreaterEqual(in1, 0)
        self.assertLess(in1, 10)
        self.assertEqual(in2, 0)
        dt1 = t1 - t0
        dt2 = t2 - t1
        self.assertGreater(dt1, 0.003)
        self.assertLess(dt1, 0.1)
        self.assertGreater(dt2, 0.003)
        self.assertLess(dt2, 0.1)
        result = b''
        objTest.write(bsTest)
        t3 = time.time()
        for _ in range(10):
            result += objTest.read()
        dt3 = time.time() - t3
        self.assertEqual(objTest.in_waiting, 0)
        self.assertEqual(objTest.out_waiting, 0)
        self.assertEqual(result, bsTest)
        self.assertGreater(dt3, 0.003)
        self.assertLess(dt3, 0.1)
        self.assertEqual(objTest.port, 'mock')
        self.assertTrue(objTest.is_open)
        objTest.port = 'mock' #re-assign same port
        self.assertEqual(objTest.port, 'mock')
        self.assertTrue(objTest.is_open)
        objTest.port = 'mock2' #assign another port
        self.assertEqual(objTest.port, 'mock2')
        self.assertTrue(objTest.is_open)
        objTest.close()
        self.assertFalse(objTest.is_open)
        self.assertEqual(objTest.port, 'mock2')
        objTest.open()
        self.assertTrue(objTest.is_open)
        self.assertEqual(objTest.port, 'mock2')
        objTest.port = None
        self.assertFalse(objTest.is_open)
        self.assertIsNone(objTest.port)
        del objTest
    
    def test_NonBlocking(self):
        """
        Tests the sending and receiving both in the non-blocking mode.

        Test id: TEST-T-12A
        Covers requirements: REQ-FUN-122, REQ-FUN-123, REQ-FUN-124, REQ-FUN-125
        and REQ-AWM-128

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock', baudrate = 2400, timeout = 0,
                                                            write_timeout = 0)
        self.assertTrue(objTest.is_open)
        self.assertEqual(objTest.baudrate, 2400)
        self.assertEqual(objTest.port, 'mock')
        self.assertEqual(objTest.timeout, 0)
        self.assertEqual(objTest.write_timeout, 0)
        self.assertEqual(objTest.in_waiting, 0)
        self.assertEqual(objTest.out_waiting, 0)
        bsTest = b'test_case\x00'
        t0 = time.time()
        objTest.write(bsTest)
        t1 = time.time()
        time.sleep(0.01)
        out = objTest.out_waiting
        in1 = objTest.in_waiting
        while objTest.out_waiting:
            pass
        time.sleep(0.01)
        in2 = objTest.in_waiting
        t2 = time.time()
        result = objTest.read(10)
        t3 = time.time()
        time.sleep(0.1)
        in3 = objTest.in_waiting
        self.assertLess(t1-t0, 0.01)
        self.assertLess(t3-t2, 0.01)
        self.assertEqual(in1, 0)
        self.assertLess(out, 10)
        self.assertGreater(out, 0)
        self.assertLess(in2, 10)
        self.assertGreater(in2, 0)
        self.assertLess(in3, 10)
        self.assertGreater(in3, 0)
        self.assertGreater(len(result), 0)
        self.assertLess(len(result), 10)
        self.assertTrue(bsTest.startswith(result))
        self.assertTrue(bsTest.endswith(objTest.read(20)))
        objTest.write(bsTest)
        while objTest.in_waiting < 10:
            pass
        result = objTest.read(20)
        self.assertEqual(result, bsTest)
        objTest.close()
        del objTest

    def test_Timed(self):
        """
        Tests the sending and receiving both in the time-out mode.

        Test id: TEST-T-12A
        Covers requirements: REQ-FUN-122, REQ-FUN-123, REQ-FUN-124, REQ-FUN-125
        and REQ-AWM-128

        Version 1.0.0.0
        """
        objTest = self.TestClass(port = 'mock', baudrate = 2400, timeout = 0.01)
        self.assertTrue(objTest.is_open)
        self.assertEqual(objTest.baudrate, 2400)
        self.assertEqual(objTest.port, 'mock')
        self.assertEqual(objTest.timeout, 0.01)
        self.assertIsNone(objTest.write_timeout)
        self.assertEqual(objTest.in_waiting, 0)
        self.assertEqual(objTest.out_waiting, 0)
        bsTest = b'test_case\x00'
        objTest.write(bsTest)
        t0 = time.time()
        result = objTest.read(10)
        t1 = time.time() - t0
        t0 = time.time()
        result2 = objTest.read()
        t2 = time.time() - t0
        self.assertEqual(len(result2), 1)
        self.assertLess(len(result), 10)
        self.assertGreater(len(result), 0)
        self.assertTrue(bsTest.startswith(result))
        self.assertLess(t2, 0.01)
        self.assertLess(t1, 0.02)
        self.assertGreater(t1, 0.01)
        objTest.write_timeout = 0.01
        self.assertEqual(objTest.write_timeout, 0.01)
        self.assertTrue(objTest.is_open)
        with self.assertRaises(SerialTimeoutException):
            objTest.write(bsTest)
        self.assertFalse(objTest.is_open)
        del objTest

#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_MockDevice)
TestSuite2 = unittest.TestLoader().loadTestsFromTestCase(Test_MockSerial)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, TestSuite2])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.mock_serial module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)