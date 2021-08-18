#usr/bin/python3
"""
Module com_lib.serial_port_com

Functions:
    list_ports():
        None -> list(tuple(str, int, int))

Classes:
    UT_SerialException
    UT_SerialTimeoutException
    SimpleCOM_API
"""

__version__ = "1.0.0.0"
__date__ = "18-08-2021"
__status__ = "Testing"

#imports

#+ standard libaries

import os
import sys
import time

from typing import Union, List, Tuple, Any, Optional, Dict

#+ 3rd party libraries

from serial.tools.list_ports import comports
from serial import Serial, SerialException, SerialTimeoutException

#+ custom modules

MODULE_PATH = os.path.realpath(__file__)
LIB_FOLDER = os.path.dirname(MODULE_PATH)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

from introspection_lib.base_exceptions import TracebackPlugin, UT_TypeError
from introspection_lib.base_exceptions import UT_ValueError, TTracebackNone

from codecs_lib.cobs import COBS_Coder

#types

T_PORTS_LIST = List[Tuple[str, int, int]]

T_RESPONSE_SYNC = Tuple[Any, int]

T_RESPONSE = Union[None, T_RESPONSE_SYNC]

TIntNone = Optional[int]

#functions

def list_ports() -> T_PORTS_LIST:
    """
    Looks up the connected via USB device, to which the virtual serial port
    communication can be established.
    
    Signature:
        None -> list(tuple(str, int, int))
    
    Returns:
        list(tuple(str, int, int)); list of 3-element tuples, where the first
            element is the port name / path, the second - the vendor ID, and
            the last - the product ID
    
    Version 1.0.0.0
    """
    Result = []
    for Entry in comports():
        bCond1 = not (Entry.vid is None)
        bCond2 = not (Entry.pid is None)
        if bCond1 and bCond2:
            Result.append((Entry.device, Entry.vid, Entry.pid))
    return Result

#classes

#+ exceptions

class UT_SerialException(TracebackPlugin, SerialException):
    """
    Custom version of serial.SerialException with the added human-readable
    traceback analysis. Should be instantiated as:

    * UT_SerialException(message)

    Attributes:
        args: tuple(str x1); one string element tuple storing the passed message
        __traceback__: types.TracebackType; stores the actual traceback of the
            exception
    
    Properties:
        Traceback: (read-only) introspection_lib.traceback.ExceptionTraceback;
            human readable traceback analysis object, may refer to the actual or
            substituted traceback depending on the mode of instantiation
    
    Methods:
        with_traceback(Traceback):
            types.TracebackType -> UT_SerialException

    Version 1.0.0.0
    """
    
    #special methods
    
    def __init__(self, strMessage: str, *, SkipFrames: TIntNone = None,
                                FromTraceback: TTracebackNone = None) -> None:
        """
        The single mandatory argument (the error message) is stored as the only
        element of the args tuple attribute. If the FromTraceback keyword
        argument holds the proper value, the traceback analysis object is
        created immediately from the substituion object; otherwise its creation
        is delayed until the first access of the property Traceback, in wich
        case the actual traceback can be truncated is SkipFrames is provided as
        a positive integer. Note that if the method with_traceback() is called
        the truncated or substituted traceback is replaced by the actual one,
        including the chained frames.

        Signature:
            str/, int > 0 OR None, types.TracebackType OR None/ -> None
        
        Args:
            Message: str; the error message
            SkipFrames: (keyword) int > 0 OR None; number of the innermost
                frames to remove from the actual traceback, ignored if the
                keyword argument FromTraceback holds a proper traceback object
            FromTraceback: (keyword) types.TracebackType OR None; substitute
                traceback (from another exception) to use; if it is provided and
                holds a proper traceback object the SkipFrames argument is
                ignored
        
        Version 1.0.0.0
        """
        super().__init__(str(strMessage), SkipFrames = SkipFrames,
                                    FromTraceback = FromTraceback)

class UT_SerialTimeoutException(TracebackPlugin, SerialTimeoutException):
    """
    Custom version of serial.SerialTimeoutException with the added
    human-readable traceback analysis. Should be instantiated as:

    * UT_SerialExceotionException(message)

    Attributes:
        args: tuple(str x1); one string element tuple storing the passed message
        __traceback__: types.TracebackType; stores the actual traceback of the
            exception
    
    Properties:
        Traceback: (read-only) introspection_lib.traceback.ExceptionTraceback;
            human readable traceback analysis object, may refer to the actual or
            substituted traceback depending on the mode of instantiation
    
    Methods:
        with_traceback(Traceback):
            types.TracebackType -> UT_SerialTimeoutException

    Version 1.0.0.0
    """
    
    #special methods
    
    def __init__(self, strMessage: str, *, SkipFrames: TIntNone = None,
                                FromTraceback: TTracebackNone = None) -> None:
        """
        The single mandatory argument (the error message) is stored as the only
        element of the args tuple attribute. If the FromTraceback keyword
        argument holds the proper value, the traceback analysis object is
        created immediately from the substituion object; otherwise its creation
        is delayed until the first access of the property Traceback, in wich
        case the actual traceback can be truncated is SkipFrames is provided as
        a positive integer. Note that if the method with_traceback() is called
        the truncated or substituted traceback is replaced by the actual one,
        including the chained frames.

        Signature:
            str/, int > 0 OR None, types.TracebackType OR None/ -> None
        
        Args:
            Message: str; the error message
            SkipFrames: (keyword) int > 0 OR None; number of the innermost
                frames to remove from the actual traceback, ignored if the
                keyword argument FromTraceback holds a proper traceback object
            FromTraceback: (keyword) types.TracebackType OR None; substitute
                traceback (from another exception) to use; if it is provided and
                holds a proper traceback object the SkipFrames argument is
                ignored
        
        Version 1.0.0.0
        """
        super().__init__(str(strMessage), SkipFrames = SkipFrames,
                                    FromTraceback = FromTraceback)

#+ work classes

class SimpleCOM_API:
    """
    Wrapper class for the serial.Serial class - serial port connection API from
    the library PySerial. Implements simple API for asynchronous and synchronous
    data exchange using zero terminated bytestrings. Keeps track of the number
    of the sent and received packages. As long as the connected device sends
    a response to each received package, the both asynchronous and synchronous
    modes can be mixed.
    
    Requires the path to the port during instantiation. Other connection
    settings except for the port path, read and write timeouts can be passed
    as the keyword arguments. The connection settings cannot be changed after-
    wards, but the port can be closed and re-opened multiple times upon
    request.
    
    Properties:
        IsOpen: (read-only) bool
        Settings: (read-only) dict(str -> type A)
    
    Methods:
        open():
            None -> None
        close():
            None -> None
        send(Data, **kwargs):
            type A/, **kwargs/ -> int > 0
        getResponse(ReturnType = bytes, **kwargs):
            /type type A, **kwargs/ -> None OR tuple(type A, int > 0)
        sendSync(Data, ReturnType = bytes, Timeout = 0, **kwargs):
            type A/, type type B, int > = 0 OR float >= 0, **kwargs/
                -> tuple(type B, int > 0)
    
    Version 1.0.0.0
    """
    
    #class attributes
    
    _BaseAPI = Serial
    
    #special methods
    
    def __init__(self, strPort, **kwargs) -> None:
        """
        Initializer. Additional connection settings, like baudrate, etc. can be
        passed as keyword arguments, however the values of the keyword arguments
        port, timeout and write_timeout are replaced by the value of the
        positional argument, 0 and 0 respectively even if they are present among
        the keyword arguments. The connection is opened automatically.
        
        If sub-class overrides this method, it must call this 'super' version.
        
        Signature:
            str/, **kwargs/ -> None
        
        Args:
            strPort: str; path to the port to be opened
            kwargs: (keyword) type A; any number of the keyword arguments
                acceptable by the serial.Serial class' initializator
        
        Raises:
            UT_SerialException: the connection cannot be opened, e.g. a device
                cannot be found or configured
            UT_TypeError: port path is not a string, OR any of the keyword
                arguments is of the improper type
            UT_ValueError: any of the keyword arguments is of a proper type, but
                of an unacceptable value
        
        Version 1.0.0.0
        """
        if not isinstance(strPort, str):
            raise UT_TypeError(strPort, str, SkipFrames = 1)
        self._Connection = None
        self._Settings = dict(kwargs)
        self._Settings['port'] = strPort
        self._Settings['timeout'] = 0
        self._Settings['write_timeout'] = 0
        self._ReceivedCommands = []
        self._CommandBuffer = bytearray()
        self._SentIndex = 0
        self._ReceivedIndex = 0
        try:
            self.open()
        except SerialException as err:
            raise UT_SerialException(''.join(map(str, err.args)),
                                                    SkipFrames = 1) from None
        except TypeError as err1:
            objError = UT_TypeError(1, int, SkipFrames = 1)
            objError.args = (''.join(map(str, err1.args)), 1)
            raise objError from None
        except ValueError as err2:
            objError = UT_ValueError(1, '1', SkipFrames = 1)
            objError.args = (''.join(map(str, err2.args)), 1)
            raise objError from None
        self._Settings['baudrate'] = self._Connection.baudrate
    
    def __del__(self) -> None:
        """
        Cleaning-up. Ensures that the connection is closed and the cached data
        is discarded.
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            None -> None
        
        Version 1.0.0.0
        """
        self.close()
        if hasattr(self, '_Connection'):
            del self._Connection
            self._Connection = None
    
    #private methods
    
    def _checkIncoming(self) -> None:
        """
        Helper 'private' method, which pulls all available data from the
        incoming buffer of the serial port connection, splits it into the
        complete packages by b'\x00' package terminator and caches the not yet
        complete packages. Note that the package terminator is automatically
        stripped.
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            None -> None
        
        Version 1.0.0.0
        """
        N_Waiting = self._Connection.in_waiting
        while N_Waiting:
            bsData = self._Connection.read(N_Waiting)
            for Char in bsData:
                if Char == 0:
                    self._ReceivedIndex += 1
                    self._ReceivedCommands.append((bytes(self._CommandBuffer),
                                                        self._ReceivedIndex))
                    self._CommandBuffer = bytearray()
                else:
                    self._CommandBuffer.append(Char)
            N_Waiting = self._Connection.in_waiting
    
    def _parseSending(self, Data: Any, **kwargs) -> bytes:
        """
        Helper 'private' method to convert the input data of the supported
        type into a bytestring. The currently supported data types are: Unicode
        strings, bytestring, byte-arrays and instances of class providing own
        bytestring packing method packToBytes(). The generated bytestring is
        COBS encoded and b'\x00' terminator is added
        
        The sub-classes can re-define this method.
        
        Signature:
            type A/, **kwargs/ -> bytes
        
        Args:
            Data: type A; the data to be converted into a bytestring
            kwargs: (keyword) type B; any additional arguments, ignored
        
        Raises:
            UT_TypeError: the passed data is of the unsupported type
        
        Version 1.0.0.0
        """
        if isinstance(Data, str):
            Result = Data.encode('utf_8')
        elif isinstance(Data, bytes):
            Result = Data
        elif isinstance(Data, bytearray):
            Result = bytes(Data)
        elif hasattr(Data, 'packToBytes'):
            Result = Data.packToBytes()
        else:
            self.close()
            raise UT_TypeError(Data, (str, bytes, bytearray), SkipFrames = 2)
        if len(Result):
            bsData = COBS_Coder.encode(Result) + b'\x00'
        else:
            bsData = b'\x00'
        return bsData
    
    def _parseResponse(self, Data: bytes, ReturnType: Any, **kwargs) -> Any:
        """
        Helper 'private' method to convert the received bytestring into a
        supported data type. The currently supported data types are: Unicode
        strings, bytestring, byte-arrays and classes providing own bytestring
        unpacking class method unpackFromBytes().
        
        The sub-classes can re-define this method but to ensure that it accepts
        a bytestring and a data type / class (not instance!) as its arguments.
        
        Signature:
            bytes, type type A/, **kwargs/ -> type A
        
        Args:
            Data: bytes; the data to be converted
            ReturnType: type type A; the data type / class of the returned value
            kwargs: (keyword) type B; any additional arguments, ignored
        
        Returns:
            type A; instance of the passed ReturnType data type / class, into
                which the received bytestring is converted
        
        Raises:
            UT_TypeError: the ReturnType is unsupported data type
        
        Version 1.0.0.0
        """
        try:
            issubclass(ReturnType, str)
        except TypeError:
            raise UT_TypeError(ReturnType, (type(str)),
                                                    SkipFrames = 2) from None
        if len(Data):
            bsData = COBS_Coder.decode(Data)
        else:
            bsData = b''
        if issubclass(ReturnType, str):
            Result = bsData.decode('utf_8')
        elif issubclass(ReturnType, bytes):
            Result = bsData
        elif issubclass(ReturnType, bytearray):
            Result = bytearray(bsData)
        elif hasattr(ReturnType, 'unpackFromBytes'):
            Result = ReturnType.unpackFromBytes(bsData)
        else:
            self.close()
            raise UT_TypeError(bsData, (str, bytes, bytearray), SkipFrames = 2)
        return Result
    
    #public API
    
    #+ properties
    
    @property
    def IsOpen(self) -> bool:
        """
        Getter (read-only) property to check the status of the connection, if
        it is open or not.
        
        Signature:
            None -> bool
        
        Version 1.0.0.0
        """
        if ((not hasattr(self, '_Connection')) or (self._Connection is None) or 
                    (not hasattr(self._Connection, 'is_open')) or
                                                (not self._Connection.is_open)):
            Result = False
        else:
            Result = True
        return Result
    
    @property
    def Settings(self) -> Dict[str, Any]:
        """
        Getter (read-only) property to check the connection settings.
        
        Signature:
            None -> dict(str -> type A)
        
        Version 1.0.0.0
        """
        return {Key : Value for Key, Value in self._Settings.items()}
    
    #+ methods
    
    def open(self) -> None:
        """
        Attempts to open a connection using the stored settings if it is not
        open at the moment.
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            None -> None
        
        Raises:
            UT_SerialException: the connection cannot be opened, e.g. a device
                cannot be found or configured
        
        Version 1.0.0.0
        """
        try:
            if self._Connection is None:
                self._Connection = self._BaseAPI(**self._Settings)
            elif not self._Connection.is_open:
                self._Connection.open()
        except SerialException as err:
            raise UT_SerialException(''.join(map(str, err.args)),
                                                    SkipFrames = 1) from None
    
    def close(self) -> None:
        """
        Closes the connection if it is open. however, the cached data is cleared
        in any case.
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            None -> None
        
        Version 1.0.0.0
        """
        if self.IsOpen:
            if hasattr(self._Connection, 'reset_input_buffer'):
                self._Connection.reset_input_buffer()
            if hasattr(self._Connection, 'reset_output_buffer'):
                self._Connection.reset_output_buffer()
            self._Connection.close()
        self._ReceivedCommands = []
        self._CommandBuffer = bytearray()
        self._SentIndex = 0
        self._ReceivedIndex = 0
    
    def send(self, Data: Any, **kwargs) -> int:
        """
        Converts the passed data into a COBS encode bytesting, adds b'\x00'
        terminator and sends it into the port. The currently supported data
        types are: Unicode strings, bytestring, byte-arrays and instances of
        class providing own bytestring packing method packToBytes().
        
        The method is non-blocking. It exists immediately and returns the sent
        package index. There is no guarantee that the sending is already
        finished or even succeeded at this point.
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            type A/, **kwargs/ -> int > 0
        
        Args:
            Data: type A; data to be processed and send
            kwargs: (keyword) type B; any additional arguments
        
        Returns:
            int > 0; the sent package index
        
        Raises:
            UT_TypeError: the passed data is of the unsupported type
            UT_SerialException: the connection cannot be opened, e.g. a device
                cannot be found or configured, OR it has been disconnected in
                the process
        
        Version 1.0.0.0
        """
        try:
            if not self.IsOpen:
                self.open()
            bsData = self._parseSending(Data, **kwargs)
            self._Connection.write(bsData)
            self._SentIndex += 1
            return self._SentIndex
        except SerialException as err:
            self.close()
            raise UT_SerialException(''.join(map(str, err.args)),
                                                    SkipFrames = 1) from None
    
    def getResponse(self, ReturnType: Any = bytes, **kwargs) -> T_RESPONSE:
        """
        Checks the received and unclaimed responces and returns the earliest
        received response. The bytestring is converted into the requested
        data type / class instance. The method is not blocking. The currently
        supported data types are: Unicode strings, bytestring, byte-arrays and
        classes providing own bytestring unpacking class method
        unpackFromBytes().
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            /type type A, **kwargs/ -> None OR tuple(type A, int > 0)
        
        Args:
            ReturnType: (optional) type type A; the data type, into which the
                the response should be converted; defaults to bytes
            kwargs: (keyword) type B; any additional arguments
        
        Returns:
            None: there is no complete package waiting at the moment
            tuple(type A, int > 0); the 2-element tuple consisting of the
                received data converted into the required data type and
                the received data package index
        
        Raises:
            UT_TypeError: the ReturnType is unsupported data type
            UT_SerialException: the connection cannot be opened, e.g. a device
                cannot be found or configured, OR it has been disconnected in
                the process
        
        Version 1.0.0.0
        """
        try:
            if not self.IsOpen:
                self.open()
            self._checkIncoming()
            if len(self._ReceivedCommands):
                Result = self._ReceivedCommands.pop(0)
                Parsed = self._parseResponse(Result[0], ReturnType, **kwargs)
                return (Parsed, Result[1])
            else:
                return None
        except SerialException as err:
            self.close()
            raise UT_SerialException(''.join(map(str, err.args)),
                                                    SkipFrames = 1) from None
    
    def sendSync(self, Data: Any, ReturnType: Any = bytes,
                Timeout: Union[int, float] = 0, **kwargs) -> T_RESPONSE_SYNC:
        """
        Converts the passed data into a COBS encode bytesting, adds b'\x00'
        terminator and sends it into the port. When it waits until the reply to
        this sending is received. Unclaimed responses to the previous sendings
        are discarded in the process. By default (zero timeout) the call is
        blocking. If a positive timeout is specified, an exception is raised if
        the response is not received during this time interval. The received
        bytesting is converted into an instance of the requested data type /
        class.
        
        The currently supported input data types are: Unicode strings,
        bytestring, byte-arrays and instances of class providing own bytestring
        packing method packToBytes().
        
        The currently supported return data types are: Unicode strings,
        bytestring, byte-arrays and classes providing own bytestring unpacking
        class method unpackFromBytes().
        
        The sub-classes should not re-define this particular method.
        
        Signature:
            type A/, type type B, int > = 0 OR float >= 0, **kwargs/
                -> tuple(type B, int > 0)
        
        Args:
            Data: type A; data to be processed and send
            ReturnType: (optional) type type B; the data type, into which the
                the response should be converted; deafults to bytes
            Timeout: (optional) int >= 0 OR float >= 0; the timeout period;
                defaults to 0, i.e. blocking call
            kwargs: (keyword) type C; any additional arguments
        
        Returns:
            tuple(type B, int > 0); the 2-element tuple consisting of the
                received data converted into the required data type and
                the send and received data package index
        
        Raises:
            UT_TypeError: the passed data is of the unsupported type, OR the
                ReturnType is unsupported data type, OR timeout arguments is
                not an int or float number
            UT_ValueError: the passed timeout value is negative
            UT_SerialException: the connection cannot be opened, e.g. a device
                cannot be found or configured, OR it has been disconnected in
                the process
        
        Version 1.0.0.0
        """
        if not isinstance(Timeout, (int, float)):
            self.close()
            raise UT_TypeError(Timeout, (int, float), SkipFrames = 1)
        elif Timeout < 0:
            raise UT_ValueError(Timeout, 'non-negative', SkipFrames = 1)
        try:
            if not self.IsOpen:
                self.open()
            bsData = self._parseSending(Data, **kwargs)
            self._Connection.write(bsData)
            self._SentIndex += 1
            StartTimer = time.time()
            while True:
                Result = None
                self._checkIncoming()
                if len(self._ReceivedCommands):
                    Result = self._ReceivedCommands.pop(0)
                    if Result[1] == self._SentIndex:
                        break
                CurrentTimer = time.time() - StartTimer
                if Timeout and CurrentTimer > Timeout:
                    break
        except SerialException as err:
            self.close()
            raise UT_SerialException(''.join(map(str, err.args)),
                                                    SkipFrames = 1) from None
        if Result is None:
            self.close()
            raise UT_SerialTimeoutException('Timeout is reached')
        Parsed = self._parseResponse(Result[0], ReturnType, **kwargs)
        return (Parsed, Result[1])
