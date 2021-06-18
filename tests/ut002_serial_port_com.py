#usr/bin/python3
"""
Module com_lib.tests.ut002_serial_port_com

Unit tests for com_lib.serial_port_com.

Covered classes:
    ThreadedListener
    AbstractDevice
    AbstractDeviceSync
"""

__version__ = "1.0.0.0"
__date__ = "18-06-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import time
import unittest

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

#++ module to be tested

from com_lib.serial_port_com import AbstractDevice, AbstractDeviceSync

#classes

#+ helper classes

class MockComAsync(AbstractDevice):
    """
    Specific sub-class of the asynchronous communication abstract class
    libhps.tools.serial_port_connection.AbstractDevice designed specially for
    unit testing, thus using libhps.tools.mock_serial.MockSerial emulation
    instead of real serial port communication class.
    
    Version 0.1.0.0
    """
    
    #class fields (protected)
    
    _strDelimiter = b'\x00' #default package delimiter
    
    _dTimeOut = 0.1 #default read-out timeout in sec (100 ms default)
    
    #protected helper methods
    
    def _openConnection(self, strPortName, **kwargs):
        """
        Helper method. Connects to the libhps.tools.mock_serial.MockSerial
        serial port connection emulation instead of an actual serial port
        stream implementation.
        
        Signature:
            str/, **kwargs/ -> None
        
        Args:
            strPortName: str, name of the port to connect to, e.g. in Posix -
                '/dev/ttyACM0', in Windows - 'COM3', etc. - ignored anyway
            **kwargs: (optional) keyword arguments, such as baudrate, etc. -
                ignored anyway
        
        Version 0.1.0.0
        """
        self._objPort = MockSerial(strPortName, **kwargs)
    
    def _parseSending(self, strCommand, *args):
        """
        Helper method to prepare string for sending. Actually, simply adds the
        zero character to the end.
        
        Signature:
            str/, *args/ -> str
        
        Args:
            strCommand: str, the command to be send
            *args: placeholder for any number of other passed arguments, ignored
        
        Returns:
            str: the string for sending
        
        Version 0.1.0.0
        """
        return b'{}{}'.format(strCommand, b'\x00')
    
    def _parseResponse(self, strCommand, *args):
        """
        Helper method to parse the received string. Actually, simply removes the
        last tailing zero character if one is present.
        
        Signature:
            str/, *args/ -> str
        
        Args:
            strCommand: str, the response received
            *args: placeholder for any number of other passed arguments, ignored
        
        Returns:
            str: the parsed result / response
        
        Version 0.1.0.0
        """
        if strCommand.endswith(b'\x00'):
            strResult = strCommand[:-1]
        else:
            strResult = str(strCommand)
        return strResult

class MockComSync(AbstractDeviceSync):
    """
    Specific sub-class of the synchronous communication abstract class
    libhps.tools.serial_port_connection.AbstractDeviceSync designed specially
    for unit testing, thus using libhps.tools.mock_serial.MockSerial emulation
    instead of real serial port communication class.
    
    Version 0.1.0.0
    """
    
    #class fields (protected)
    
    _strDelimiter = b'\x00' #default package delimiter
    
    _dTimeOut = 10 #default read-out timeout in sec (10 s default)
    
    def _openConnection(self, strPortName, **kwargs):
        """
        Helper method. Connects to the libhps.tools.mock_serial.MockSerial
        serial port connection emulation instead of an actual serial port
        stream implementation.
        
        Signature:
            str/, **kwargs/ -> None
        
        Args:
            strPortName: str, name of the port to connect to, e.g. in Posix -
                '/dev/ttyACM0', in Windows - 'COM3', etc. - ignored anyway
            **kwargs: (optional) keyword arguments, such as baudrate, etc. -
                ignored anyway
        
        Version 0.1.0.0
        """
        self._objPort = MockSerial(strPortName, **kwargs)
    
    def _parseSending(self, strCommand, *args):
        """
        Helper method to prepare string for sending. Actually, simply adds the
        zero character to the end.
        
        Signature:
            str/, *args/ -> str
        
        Args:
            strCommand: str, the command to be send
            *args: placeholder for any number of other passed arguments, ignored
        
        Returns:
            str: the string for sending
        
        Version 0.1.0.0
        """
        return b'{}{}'.format(strCommand, b'\x00')
    
    def _parseResponse(self, strCommand, *args):
        """
        Helper method to parse the received string. Actually, simply removes the
        last tailing zero character if one is present.
        
        Signature:
            str/, *args/ -> str
        
        Args:
            strCommand: str, the response received
            *args: placeholder for any number of other passed arguments, ignored
        
        Returns:
            str: the parsed result / response
        
        Version 0.1.0.0
        """
        if strCommand.endswith(b'\x00'):
            strResult = strCommand[:-1]
        else:
            strResult = str(strCommand)
        return strResult
    
    def _checkResponse(self, strCommand, strResponse, *args):
        """
        Helper method to check that the response is indeed to the last sent
        command. Simply compares the strings: initial command and the parsed
        response.
        
        Signature:
            str, type A, str -> bool
        
        Args:
            strCommand: str, the initial command (to be send)
            gData: type A, the sent command data, ignored, since it is None
            strResponse: str, the parsed response
        
        Returns:
            bool: True if the response equals to the initial command, False
                otherwise
        
        Version 0.1.0.0
        """
        bResult = False
        if strCommand == strResponse:
            bResult = True
        return bResult

#+ test cases

class Test_MockComAsync(unittest.TestCase):
    """
    Test cases for the AbstractDevice class (asynchronous) using mock serial
    port.
    
    TEST-T-200 and TEST-T-201 (via inheritance).
    
    Covers requrements: REQ-FUN-201, REQ-FUN-202, REQ-FUN-203, REQ-FUN-210,
    REQ-FUN-211, REQ-AWM-200, REQ-AWM-201, REQ-AWM-202
    
    Version 0.1.0.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 0.1.0.0
        """
        cls.TestClass = MockComAsync
    
    def test_MockCom_ConnectDisconnect(self):
        """
        Tests that the class can be instantiated, connection established and
        properly closed.
        
        TEST-T-200 and TEST-T-201
        
        Covers requirements: REQ-FUN-201 and REQ-FUN-202
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        self.assertTrue(objTest.IsOpen)
        objTest.close()
        self.assertFalse(objTest.IsOpen)
        del objTest
    
    def test_MockCom_ConnectTwiceRaises(self):
        """
        Tests that the already open connection cannot be opened again - must
        raise serial.SerialException.
        
        TEST-T-200 and TEST-T-201
        
        Covers requirements: REQ-FUN-201 and REQ-AWM-200
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        with self.assertRaises(SerialException):
            objTest.open('Whatever')
        objTest.close()
        del objTest
    
    def test_MockCom_DisonnectTwiceRaises(self):
        """
        Tests that the already closed connection cannot be closed again - must
        raise serial.SerialException.
        
        TEST-T-200 and TEST-T-201
        
        Covers requirements: REQ-FUN-202 and REQ-AWM-201
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        objTest.close()
        with self.assertRaises(SerialException):
            objTest.close()
        del objTest
    
    def test_MockCom_NoSendingToClosed(self):
        """
        Tests that the message cannot be send to a closed port - must raise
        serial.SerialException.
        
        TEST-T-200 and TEST-T-201
        
        Covers requirements: REQ-AWM-202
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        objTest.close()
        with self.assertRaises(SerialException):
            objTest.sendCommand('fast')
        del objTest
    
    def test_MockCom_NoReadingFromClosed(self):
        """
        Tests that the data cannot be read-out from a closed port - must raise
        serial.SerialException.
        
        TEST-T-200 and TEST-T-201
        
        Covers requirements: REQ-AWM-202
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        objTest.close()
        with self.assertRaises(SerialException):
            strResult = objTest.getResponse()
        del objTest
    
    def test_MockCom_CommunicateNormal(self):
        """
        Tests the normal way of communications. Sends several messages and
        fetches response some time later.
        
        TEST-T-200
        
        Covers requiements: REQ-FUN-201, REQ-FUN-202, REQ-FUN-210, REQ-FUN-211
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        for strCommand in ['fast', 'slow', 'very_slow']:
            objTest.sendCommand(strCommand)
        #allow enought time for processing
        for strCommand in ['fast', 'slow', 'very_slow']:
            strResponse = objTest.getResponse(dTimeout = 20)
            self.assertEqual(strResponse, strCommand)
        objTest.close()
        del objTest
    
    def test_MockCom_Timeout(self):
        """
        Tests that it communicates normally if the response is received within
        the timeout period but simply returns None if time-out occurs, whereas
        the device remains being connected.
        
        TEST-T-200
        
        Covers requirements: REQ-FUN-211
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        strCommand = 'fast'
        objTest.sendCommand(strCommand)
        strResponse = objTest.getResponse()
        self.assertEqual(strResponse, strCommand)
        objTest.sendCommand('very_slow')
        strResponse = objTest.getResponse()
        self.assertIsNone(strResponse)
        self.assertTrue(objTest.IsOpen)
        objTest.close()
        del objTest

class Test_MockComSync(Test_MockComAsync):
    """
    Test cases for the AbstractDevice class (synchronous) using mock serial
    port.
    
    TEST-T-301
    
    Covers requrements: REQ-FUN-201, REQ-FUN-202, REQ-FUN-203, REQ-FUN-220,
    REQ-FUN-221, REQ-AWM-200, REQ-AWM-201, REQ-AWM-202
    
    Version 0.1.1.0
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Preparation for the test cases, done only once.
        
        Version: 0.1.0.0
        """
        cls.TestClass = MockComSync
    
    def test_MockCom_CommunicateNormal(self):
        """
        Tests the normal way of communications. Sends a message and fetches
        response with the long enough timeout (20 sec). Loops through fast to
        very slow responses.
        
        TEST-T-201
        
        Covers requiements: REQ-FUN-201, REQ-FUN-202, REQ-FUN-220, REQ-FUN-221
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        #allow enought time for processing
        for strCommand in ['fast', 'slow', 'very_slow']:
            strResult = objTest.sendCommand(strCommand, dTimeout = 20)
            self.assertEqual(strCommand, strResult)
        objTest.close()
        del objTest
    
    def test_MockCom_Timeout(self):
        """
        Tests that it communicates normally if the response is received within
        the timeout period but throws an exception and disconnect the device
        if time-out occurs.
        
        TEST-T-201
        
        Covers requirments: REQ-FUN-210
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        strCommand = 'fast'
        strResponse = objTest.sendCommand(strCommand)
        self.assertEqual(strResponse, strCommand)
        with self.assertRaises(SerialTimeoutException):
            objTest.sendCommand('very_slow')
        self.assertFalse(objTest.IsOpen)
        del objTest
    
    def test_MockCom_getResponseReturnsNone(self):
        """
        Tests that the getResponse() method returns None.
        
        TEST-T-201
        
        Covers requirements: REQ-FUN-221
        
        Version 0.1.0.0
        """
        objTest = self.TestClass('MockSerial')
        strCommand = 'fast'
        strResponse = objTest.sendCommand(strCommand)
        strResponse = objTest.getResponse()
        self.assertIsNone(strResponse)
        objTest.close()
        del objTest

#+ test suites

TestSuite1 = unittest.TestLoader().loadTestsFromTestCase(Test_MockComAsync)

TestSuite2 = unittest.TestLoader().loadTestsFromTestCase(Test_MockComSync)

TestSuite = unittest.TestSuite()
TestSuite.addTests([TestSuite1, TestSuite2])

if __name__ == "__main__":
    sys.stdout.write(
            "Testing com_lib.tools.serial_port_com module...\n")
    sys.stdout.flush()
    unittest.TextTestRunner(verbosity = 2).run(TestSuite)