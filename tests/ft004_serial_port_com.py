#usr/bin/python
"""
Module com_lib.ft004_serial_port_com

Functional testing of the module com_lib.serial_port_com, which requires a
CFR rev 1 device physically connected to an USB port. Note that the device must
be the only one connected (excluding the standard USB devices as camera, etc.),
because simply the first entry in the response of the function
com_lib.serial_port_com.list_comports() is taken.

TEST-T-220 -> REQ-FUN-222

Sets the UV LED intensity to 100 (light frame) and read-outs the emission
detector with the specified number of samples, then switches of the UV LED
(intensity to 0). The time required to obtain that number of samples from a
single detector channel is measured and reported.

Classes:
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
import time

#+ my modules

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ COBS library and serialization objects

from codecs_lib.cobs import COBS_Coder
from libhps.tools.serialization import NullStruct #REPLACE! and below!
from com_lib.ft003_tools_serial_port_com import SensorSetting
from com_lib.ft003_tools_serial_port_com import SensorValue
from com_lib.ft003_tools_serial_port_com import SourceSetting

#++ module to be tested

from com_lib.serial_port_com import AbstractDeviceSync
from com_lib.serial_port_com import list_comports

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
    
    Inherits the API of the base class but re-defines the actual worker helper
    'protected' methods. Thus the main method must be evoked as:
        sendCommand(iCommand, objData, tResult):
            int, 'NestedStruct OR 'NullStuct,
                class 'NestedStruct OR class 'NullStuct
                    -> int, 'NestedStruct OR 'NullStuct
    with
    
        Args:
            iCommand: int, the command code
            objData: 'NestedStruct OR 'NullStuct, instance of, the command data
                stored in any sub-class of these classes
            tResult: class 'NestedStruct or class 'NullStuct, the data type
                (class) to cast the response onto
    
        Returns: int, tuple(int, 'NestedStruct OR 'NullStuct), the response
            command code and data cast onto the type (class) specified by the
            tResult argument
    
    Version 0.3.0.0
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
        iHigh, iLow = divmod(iCommand, 256)
        bsData = gData.packToString()
        if not len(bsData):
            bsData = b'\x00\x00'
        bsResult = b''.join(
                            [COBS_Coder.encode(b''.join([bsData, chr(iHigh),
                                            chr(iLow)])), self._strDelimiter])
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
        bsTemp = COBS_Coder.decode(strData)
        iCommand = ord(bsTemp[-2]) * 256 + ord(bsTemp[-1])
        if len(bsTemp) > 3:
            bsData = bsTemp[:-3]
        else:
            bsData = ''
        objData = tResult.createFromString(bsData)
        return iCommand, objData
    
    def _checkResponse(self, iCommand, gResponse, *args):
        """
        Checks the decoded / parsed response of the device, which is expected
        to be a 2-elements tuple of a byte-string (data) and integer command
        code. The returned command code must be the same as the sent command
        code.
        
        Signature:
            int, tuple(int, NestedStruct OR NullStruct)/, *args/ -> bool
        
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

#constants

N_SAMPLES = 75

#+ structure: command code, structured data, return type

SET_LIGHT = (4360, SourceSetting(Channel = 0, Value = 100), NullStruct)
#UV LED to 100

SET_DARK = (4360, SourceSetting(Channel = 0, Value = 0), NullStruct)
#UV LED to 0

READ_EMISSION = (4362, SensorSetting(Channel = 0, Samples = N_SAMPLES),
                                                                SensorValue)
#Emmision channel with N samples

#test function

def main():
    strPort = list_comports()[0]
    
    objPort = CFR_test(strPort)
    
    print(strPort, ', is open:', objPort.IsOpen)
    
    objPort.sendCommand(*SET_LIGHT)
    
    dStartTime = time.time()
    
    objPort.sendCommand(*READ_EMISSION)
    
    dEndTime = time.time()
    
    objPort.sendCommand(*SET_DARK)
    
    objPort.close()
    
    print(strPort, ', is open:', objPort.IsOpen)
    
    print('Time to read {} samples is {} ms'.format(N_SAMPLES,
                                                1000 * (dEndTime - dStartTime)))

# execution entry point

if __name__ == '__main__':
    main()