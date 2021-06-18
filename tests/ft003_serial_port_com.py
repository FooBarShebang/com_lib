#usr/bin/python
"""
Module com_lib.ft003_serial_port_com

Functional testing of the module com_lib.serial_port_com, which requires a
CFR rev 1 device physically connected to an USB port. Note that the device must
be the only one connected (excluding the standard USB devices as camera, etc.),
because simply the first entry in the response of the function
com_lib.serial_port_com.list_comports() is taken.

TEST-T-20?

Covers requirements: REQ-FUN-220, REQ-FUN-221 and REQ-FUN-204

Sets the UV LED intensity to 100 (light frame) and read-outs the emission
detector with 100 samples, then repeats at the UV LED intensity 0 (dark). This
cycle is repeated 4 times. Finally, the device information is retrieved, i.e.
the hardware type, serial number, etc.

Prints out the raw sent command + data, string to send to the device, string
respons from the device, decoded and split into command + data response and,
finally the human readable representation of the received data.

Functions:
    GetHex(strData):
        str -> str

Classes:
    SourceSetting
    SensorSetting
    SensorValue
    SoftVersion
    Revision
    DeviceSerial
    TimeStamp
    DeviceInfo
    CFR_test
"""

__version__ = "1.0.0.0" #TODO - redefine!
__date__ = "18-06-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import time
import ctypes

#+ my modules

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ COBS library and serialization objects

from codecs_lib.cobs import COBS_Coder
from libhps.tools.serialization import NullStruct, NestedStruct #REPLACE!


#++ module to be tested

from com_lib.serial_port_com import AbstractDeviceSync, list_comports

#helper functions

def GetHex(strData):
    """
    Helper function to represent a byte string as '\xaa' hex codes instead of
    the mixture of hex code and printable characters.
    
    Signature:
        str -> str
    
    Args:
        strData: str, byte sequence to be represented in hex code
    
    Returns:
        str: the hex representation of the data
    
    Version 0.1.0.0
    """
    return ''.join(['\{}'.format(hex(ord(strItem))[1:]) for strItem in strData])

#classes

#+ main class

class CFR_test(AbstractDeviceSync):
    """
    Minimal implementation of the communication with CFR rev 1 device based on
    the asynchronous communication abstract class
    libhps.tools.serial_port_communication.AbstractDeviceSync, specifically for
    this test.
    
    The commands to be send are to be specified by their code, the associated
    data stored as a (nested) structure and the class (data type) onto witch the
    device's response should be mapped. The returned results are represented
    in the human-readable form.
    
    All steps of the data transformation are printed out.
    
    Methods:
        sendCommand(iCommand, gData, tReturn):
            int, NestedStruct OR NullStruct,
                type NestedStruct OR type NullStruct -> None 
    
    Version 0.2.0.0
    """
    
    #class fields (protected)
    
    _strDelimiter = b'\x00' #default package delimiter
    
    def _parseSending(self, iCommand, gData, tResult):
        """
        Creates a byte-string to be send to a device from the command code
        (assuming unsinged 16-bit integer) and the command data already packed
        into a byte string. The command code is transformed into the high and
        low bytes, which are attached to the data string in the high - low
        order. The resulting string is encoded using COBS algorithm, and the
        package delimiter '\x00' is appended.
        
        Signature:
            str, NestedStruct OR NullStruct,
                type NestedStruct OR type NullStruct -> str
        
        Args:
            iCommand: int, the command code, assuming uint16
            gData: NestedStruct OR NullStruct, the command data to send
            tResult: type NestedStruct OR type NullStruct, the expected type of
                the response, ignored
        
        Returns:
            str: byte-string to be send
        
        Version 0.1.0.0
        """
        print('Input: Command {}, Data: {}:{}'.format(iCommand,
                                gData.__class__.__name__, gData.packToJSON()))
        iHigh, iLow = divmod(iCommand, 256)
        bsData = gData.packToString()
        if not len(bsData):
            bsData = b'\x00\x00'
        bsResult = b''.join(
                            [COBS_Coder.encode(b''.join([bsData, chr(iHigh),
                                            chr(iLow)])), self._strDelimiter])
        print('Sent: {}'.format(GetHex(bsResult)))
        return bsResult
    
    def _parseResponse(self, strData, gData, tResult):
        """
        Decodes the passed byte-string using COBS algorithm, splits the
        result into the data byte-string and integer command code assuming
        uint16be (high low) byte order and a zero byte separator between the
        data and the command code. Returns the command code + data as an
        unpacked tuple.
        
        Signature:
            str, NestedStruct OR NullStruct,
                type NestedStruct OR type NullStruct
                    -> tuple(int, NestedStruct OR NullStruct)
        
        Args:
            strData: str, data to be parsed
            gData: NestedStruct OR NullStruct, the intial command data, ignored
            tResult: type NestedStruct OR type NullStruct, the expected type of
                the response, to be cast upon
        
        Returns:
            tuple(int, NestedStruct OR NullStruct): the command code and the
                data; the type of the data is define by the value of tResult
        
        Version 0.1.0.0
        """
        print('Received: {}'.format(GetHex(strData)))
        bsTemp = COBS_Coder.decode(strData)
        iCommand = ord(bsTemp[-2]) * 256 + ord(bsTemp[-1])
        if len(bsTemp) > 3:
            bsData = bsTemp[:-3]
        else:
            bsData = ''
        print('Processed: Command {}, Data: {}'.format(iCommand,GetHex(bsData)))
        objData = tResult.createFromString(bsData)
        return iCommand, objData
    
    def _checkResponse(self, iCommand, gResponse, *args):
        """
        Checks the decoded / parsed response of the device, which is expected
        to be a 2-elements tuple of a byte-string (data) and integer command
        code. The returned command code must be the same as the sent command
        code.
        
        Signature:
            int, tuple(NestedStruct OR NullStruct, int)/, *args/ -> bool
        
        Args:
            iCommand: int, the sent command code
            gResponse: tuple(NestedStruct OR NullStruct, int), the response data
                and command code
            *args: (optional), any arguments of any type, ignored
        
        Returns:
            bool: True if the response is a 2-element tuple with the second
                element being integer equal to the sent command code, False
                otherwise
        
        Version 0.1.1.0
        """
        bResult = False
        if isinstance(gResponse, tuple) and len(gResponse) == 2:
            iResponse, _ = gResponse
            if iResponse == iCommand:
                bResult = True
        return bResult
    
    def sendCommand(self, iCommand, gData, tReturn):
        """
        Sends the command and awaits the response. Prints out all steps.
        
        Signature:
            int, NestedStruct OR NullStruct,
                type NestedStruct OR type NullStruct -> None 
        
        Args:
            iCommand: int, the command to be parsed and send
            gData: NestedStruct OR NullStruct, instance of; the data of the
                command to be parsed and send
            tReturn: type NestedStruct OR type NullStruct, the expected type of
                the response, to be cast upon
        
        Raises:
            serial.serialutil.SerialException: device was not connected at the
                moment of the method's call, or got disconnected in the process
            serial.serialutil.SerialTimeoutException: the reply to a command
                does not match the expections, a.o. no response is received
                during the timeout period (e.g. connection is lost)
        
        Version 0.1.0.0
        """
        _, objData = super(CFR_test, self).sendCommand(iCommand, gData, tReturn)
        print('Translated result {}:{}'.format(objData.__class__.__name__,
                                                        objData.packToJSON()))

#+ helper classes

class SourceSetting(NestedStruct):
    
    _fields = [ ('Channel', ctypes.c_uint8),
                ('Value', ctypes.c_uint8)]

class SensorSetting(NestedStruct):
    
    _fields = [ ('Channel', ctypes.c_uint8),
                ('Samples', ctypes.c_uint16)]

class SensorValue(NestedStruct):
    
    _fields = [ ('Overflow', ctypes.c_uint8),
                ('Value', ctypes.c_uint16)]

class SoftVersion(NestedStruct):
    
    _fields = [ ('Major', ctypes.c_uint8),
                ('Minor', ctypes.c_uint8),
                ('Build', ctypes.c_uint8),
                ('Revision', ctypes.c_uint8)]

class Revision(NestedStruct):
    
    _fields = [ ('Number', ctypes.c_uint8),
                ('Letter', ctypes.c_char)]

class DeviceSerial(NestedStruct):
    
    _fields = [ ('Type', ctypes.c_uint8),
                ('Serial', ctypes.c_uint32)]

class TimeStamp(NestedStruct):
    
    _fields = [ ('Second', ctypes.c_uint8),
                ('Minute', ctypes.c_uint8),
                ('Hour', ctypes.c_uint8),
                ('Day', ctypes.c_uint8),
                ('Month', ctypes.c_uint8),
                ('Year', ctypes.c_uint8)]

class DeviceInfo(NestedStruct):
    
    _fields = [('DeviceType', ctypes.c_uint8),
                ('API_Version', SoftVersion),
                ('FirmwareVersion', SoftVersion),
                ('IsProgrammed', ctypes.c_uint8),
                ('HardwareRevision', Revision),
                ('SoftwareRevision', Revision),
                ('BaseTypeSerial', DeviceSerial),
                ('EndTypeSerial', DeviceSerial),
                ('BuildTime', TimeStamp),
                ('BootloaderVersion', SoftVersion)
                ]

#constants

#+ structure: command code, structured data, return type

SET_LIGHT = (4360, SourceSetting(Channel = 0, Value = 100), NullStruct)
#UV LED to 100

SET_DARK = (4360, SourceSetting(Channel = 0, Value = 0), NullStruct)
#UV LED to 0

READ_EMISSION = (4362, SensorSetting(Channel = 0, Samples = 100), SensorValue)
#Emmision channel with 100 samples

DEVICE_INFO = (4097, NullStruct(), DeviceInfo)

#test function

def main():
    strPort = list_comports()[0]
    
    objPort = CFR_test(strPort)
    
    print(strPort, ', is open:', objPort.IsOpen)
    
    for _ in range(4):
        objPort.sendCommand(*SET_LIGHT)
        objPort.sendCommand(*READ_EMISSION)
        time.sleep(1)
        objPort.sendCommand(*SET_DARK)
        objPort.sendCommand(*READ_EMISSION)
        time.sleep(1)
    
    objPort.sendCommand(*DEVICE_INFO)
    
    objPort.close()
    
    print(strPort, ', is open:', objPort.IsOpen)

# execution entry point

if __name__ == '__main__':
    main()
