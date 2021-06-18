#usr/bin/python
"""
Module com_lib.ft002_serial_port_com

Functional testing of the module com_lib.serial_port_com, which requires a
CFR rev 1 device physically connected to an USB port. Note that the device must
be the only one connected (excluding the standard USB devices as camera, etc.),
because simply the first entry in the response of the function
com_lib.serial_port_com.list_comports() is taken.

TEST-T-20?

Covers requirements: REQ-FUN-220, REQ-FUN-221 and REQ-FUN-204

Sets the UV LED intensity to 100 (light frame) and read-outs the emission
detector with 100 samples, then repeats at the UV LED intensity 0 (dark). This
cycle is repeated 4 times.

Prints out the raw sent command + data, string to send to the device, string
respons from the device, decoded and split into command + data response and,
finally the human readable representation of the received data.

Functions:
    GetHex(strData):
        str -> str
    TranslateResponse(strData):
        str -> str

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

#+ my modules

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ COBS library

from codecs_lib.cobs import COBS_Coder

#++ module to be tested

from com_lib.serial_port_com import AbstractDeviceSync, list_comports

#constants

SET_LIGHT = (4360, b'\x00\x64') #UV LED to 100

SET_DARK = (4360, b'\x00\x00') #UV LED to 0

READ_EMISSION = (4362, b'\x00\x64\x00') #Emmision channel with 100 samples

#functions

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

def TranslateResponse(strData):
    """
    Helper function to translate the device's response, specific for this test
    module. An empty string is transformed into 'Command recieved', the 3 bytes
    string is transformed into 'Signal {}, Overflow {}' assuming packed order
    byte (uint8) as overflow followed by uint16le (low + high) as the signal.
    Other responses are translated into 'Unknown response'.
    
    Signature:
        str -> str
    
    Args:
        strData: str, byte sequence to be translated
    
    Returns:
        str: the human readable representation of the data
    
    Version 0.1.0.0
    """
    if not len(strData):
        strResult = 'Command recieved'
    elif len(strData) == 3:
        iOverflow = ord(strData[0])
        iSignal = ord(strData[1]) + 256 * ord(strData[2])
        strResult = 'Signal {}, Overflow {}'.format(iSignal, iOverflow)
    else:
        strResult = 'Unknown response'
    return strResult

#classes

class CFR_test(AbstractDeviceSync):
    """
    Minimal implementation of the communication with CFR rev 1 device based on
    the asynchronous communication abstract class
    libhps.tools.serial_port_communication.AbstractDeviceSync, specifically for
    this test.
    
    The commands to be send are to be specified by their code and the associated
    data alread packed into a byte-string. The returned results are represented
    in the human-readable form.
    
    All steps of the data transformation are printed out.
    
    Methods:
        sendCommand(iCommand, strData = None, dTimeout = None):
            int, str -> None 
    
    Version 0.1.1.0
    """
    
    #class fields (protected)
    
    _strDelimiter = b'\x00' #default package delimiter
    
    def _parseSending(self, iCommand, strData):
        """
        Creates a byte-string to be send to a device from the command code
        (assuming unsinged 16-bit integer) and the command data already packed
        into a byte string. The command code is transformed into the high and
        low bytes, which are attached to the data string in the high - low
        order. The resulting string is encoded using COBS algorithm, and the
        package delimiter '\x00' is appended.
        
        Signature:
            int, str -> str
        
        Args:
            iCommand: int, the command code, assuming uint16
            strData: str, command data already packed into a byte-string
        
        Returns:
            str: byte-string to be send
        
        Version 0.1.0.0
        """
        print('Input: Command {}, Data: {}'.format(iCommand, GetHex(strData)))
        iHigh, iLow = divmod(iCommand, 256)
        bsResult = b''.join([COBS_Coder.encode(b''.join([strData, chr(iHigh),
                                            chr(iLow)])), self._strDelimiter])
        print('Sent: {}'.format(GetHex(bsResult)))
        return bsResult
    
    def _parseResponse(self, strData, *args):
        """
        Decodes the passed byte-string using COBS algorithm, splits the
        result into the data byte-string and integer command code assuming
        uint16be (high low) byte order and a zero byte separator between the
        data and the command code. Returns the command code + data as an
        unpacked tuple.
        
        Signature:
            str/, *args/ -> tuple(int, str)
        
        Args:
            strData: str, data to be parsed
            *args: (optional), any arguments of any type, ignored
        
        Returns:
            tuple(int, str): the command code and the data
        
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
        return iCommand, bsData
    
    def _checkResponse(self, iCommand, gResponse, *args):
        """
        Checks the decoded / parsed response of the device, which is expected
        to be a 2-elements tuple of a byte-string (data) and integer command
        code. The returned command code must be the same as the sent command
        code.
        
        Signature:
            int, tuple(str, int)/, *args/ -> bool
        
        Args:
            iCommand: int, the sent command code
            gResponse: tuple(str, int), the response data and command code
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
    
    def sendCommand(self, iCommand, strData):
        """
        Sends the command and awaits the response. Prints out all steps.
        
        Signature:
            int, str -> None
        
        Args:
            iCommand: int, the command to be parsed and send
            strData: str, the data of the command to be parsed and send
        
        Raises:
            serial.serialutil.SerialException: device was not connected at the
                moment of the method's call, or got disconnected in the process
            serial.serialutil.SerialTimeoutException: the reply to a command
                does not match the expections, a.o. no response is received
                during the timeout period (e.g. connection is lost)
        
        Version 0.1.0.0
        """
        _, bsData = super(CFR_test, self).sendCommand(iCommand, strData)
        print('Result: {}'.format(TranslateResponse(bsData)))

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
    
    objPort.close()
    
    print(strPort, ', is open:', objPort.IsOpen)

# execution entry point

if __name__ == '__main__':
    main()
