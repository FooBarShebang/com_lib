#usr/bin/python3
"""
Module com_lib.mock_serial

Implements a mock device, echoing the input into the output, and a mock serial
port connection, to wich that device is bound. This module is designed for the
test purposes.

Functions:
    MockDevice(Input, Output, StopEvent, Baudrate):
        queue.Queue, queue,Queue, threading.Event, int > 0 -> None

Classes:
    MockSerial
"""

__version__ = "1.0.0.1"
__date__ = "18-08-2021"
__status__ = "Production"

#imports

#+ standard libraries

from threading import Thread, Event
from queue import Queue, Empty
from time import sleep, time
from typing import Union

#+ 3rd party libraries

from serial import SerialException, SerialTimeoutException

#globals

#+ types

T_REAL = Union[int, float]
T_REAL_OR_NONE = Union[T_REAL, None]
T_STR_OR_NONE = Union[str, None]

#functions

#+ emulation of a device connected to a port

def MockDevice(Input: Queue, Output: Queue,
                StopEvent: Event, Baudrate: int) -> None:
    """
    Emulation of a simple device, which repeats back every command send, until
    the stop event is not set externally or b'quit' command is received. Note
    that b'\x00' is used as the terminator between the commands, and it is also
    send back. The response to the b'quit' command is not sent.

    This function is designed to be executed in a separate thread.

    Signature:
        queue.Queue, queue,Queue, threading.Event, int > 0 -> None
    
    Args:
        Input: Queue; input buffer (from the device's perspective), from which
            the commands are to be read
        Output: Queue; output buffer (from the device's perspective), into which
            the response to a command is to be written
        StopEvent: Event; an object signaling the function to terminate if set
        Baudrate: int > 0; emulation of the different data transfer rates, i.e.
            introduces a delay of 8.0 / Baudrate between each byte read from the
            input and send to the output
    
    Version 1.0.0.0
    """
    Delay = 8.0 / Baudrate
    Command = bytearray()
    while not StopEvent.is_set():
        try:
            Character = Input.get(False)
            Command.append(Character)
            sleep(Delay)
            Input.task_done()
            if Character == 0:
                if Command != b'quit\x00':
                    for SendCharacter in Command:
                        Output.put(SendCharacter)
                        sleep(Delay)
                    Command = bytearray()
                else:
                    StopEvent.set()
        except Empty:
            pass

#classes

class MockSerial:
    """
    Emulation of the minimal API compatible with the serial.Serial class, see
    PyPI library PySerial. Executes the function MockDevice in a separate thread
    upon calling the method open(); one should assign port = 'mock' first. This
    approach simulates a real serial port connection to a device, which echoes
    back the send data. Thus the blocking and non-blocking reading and writing
    at the different baudrates can be safely tested.

    Methods:
        open()
        close()
        read(size = 1):
            /int >= 1/ -> bytes
        write(data):
            bytes -> int >= 0

    Properties:
        is_open: (read-only) bool
        in_waiting: (read-only) int >= 0
        out_waiting: (read-only) int >= 0
        port: str OR None
        baudrate: int > 0
        timeout: int >= 0 OR float >= 0 OR None
        write_timeout: int >=0 OR float OR None
    
    Version 1.0.1.0
    """

    #private class attributes

    _KnownPorts = {'mock' : MockDevice,
                    'mock2' : MockDevice}

    _KnownBaudrates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400,
                                        4800, 9600, 19200, 38400, 57600, 115200]

    #special methods

    def __init__(self, **kwargs):
        """
        Initialization. Creates instance attributes and sets the connection
        settings according to the passed keyword arguments values:
            * port - None or str
            * baudrate - integer, any standard baudrate, e.g. 50, 9600, 115200
            * timeout and write_timeout - None or non-negative integer or float
        
        If the known value is assigned to the port (e.g. 'mock') the connection
        to the mock device is openned automatically.

        Signature:
            \**kwargs\ -> None
        
        Raises:
            TypeError: inappropriate data type of a recognised keyword argument
            ValueError: inappropriate value of a proper data type of a
                recognized keyword argument
            serial.SerialExeption: unknown port value (string)

        Version 1.0.0.0
        """
        self._objIncoming = Queue()
        self._objOutgoing = Queue()
        self._objSignal = Event()
        self._objDevice = None
        self.timeout = kwargs.get('timeout', None)
        self.write_timeout = kwargs.get('write_timeout', None)
        self.baudrate = kwargs.get('baudrate', 9600)
        self.port = kwargs.get('port', None)


    def __del__(self):
        """
        Destructor. Ensures proper closing of the additional threads and
        clean-up activities.

        Signature:
            None -> None
        
        Version 1.0.0.0
        """
        self._closeClean()
        del self._objOutgoing
        del self._objIncoming
        del self._objSignal
        self._objSignal = None
        self._objIncoming = None
        self._objOutgoing = None


    #private helper methods

    def _closeClean(self):
        """
        Helper method to ensure clean shutting down of the 'device' thread and
        empting of the both buffer queues.

        Signature:
            None -> None
        
        Version 1.0.0.0
        """
        if self.is_open:
            if not self._objSignal.is_set():
                self._objSignal.set()
            if not (self._objDevice is None) and self._objDevice.is_alive():
                self._objDevice.join()
            del self._objDevice
            self._objDevice = None
            while not self._objIncoming.empty():
                try:
                    self._objIncoming.get(False)
                    self._objIncoming.task_done()
                except Empty:
                    break
            while not self._objOutgoing.empty():
                try:
                    self._objOutgoing.get(False)
                    self._objOutgoing.task_done()
                except Empty:
                    break

    #public API

    #+properties

    @property
    def is_open(self) -> bool:
        """
        Getter (read-only) property to check the status of the connection.

        Signature:
            None -> bool
        
        Version 1.1.0.0
        """
        if self._objDevice is None or (not (self._objDevice.is_alive())):
            Result = False
        else:
            Result = True
        return Result

    @property
    def in_waiting(self) -> int:
        """
        Getter (read-only) property for the number of bytes waiting to be
        read from the 'read' input buffer

        Signature:
            None -> int >= 0
        
        Version 1.0.0.0
        """
        if not self.is_open:
            raise SerialException('Connection is inactive')
        return self._objIncoming.qsize()

    @property
    def out_waiting(self) -> int:
        """
        Getter (read-only) property for the number of bytes waiting in the
        'write' output buffer

        Signature:
            None -> int >= 0
        
        Version 1.0.0.0
        """
        if not self.is_open:
            raise SerialException('Connection is inactive')
        return self._objOutgoing.qsize()
    
    @property
    def port(self) -> T_STR_OR_NONE:
        """
        Getter property for the name of the 'connected' port - should always be
        'mock'.

        Signature:
            None -> str OR None
        
        Version 1.0.0.0
        """
        return self._Port

    @port.setter
    def port(self, Name: T_STR_OR_NONE) -> None:
        """
        Setter property for the port to 'connect' to. Accepts only a single
        value 'mock' or 'mock2' - all other strings result in
        serial.SerialException.

        Signature:
            str OR None-> None
        
        Raises:
            TypeError: the argument is not a string
            serial.SerialException: the argument is a string, but not known
                value

        Version 1.0.0.0
        """
        if not (isinstance(Name, str) or (Name is None)):
            self._closeClean()
            raise TypeError('port {} is not a string or None'.format(Name))
        elif isinstance(Name, str) and (not (Name in self._KnownPorts)):
            self._closeClean()
            raise SerialException('unknown port {}'.format(Name))
        if hasattr(self, '_Port'): #repetitive call
            if Name is None:
                self._closeClean()
                self._Port = None
            else: #name is string
                if not self.is_open: #connection is closed
                    self._Port = Name
                    self.open()
                else: #connection if open
                    if self._Port != Name: #another port is requested
                        self._closeClean()
                        self._Port = Name
                        self.open()
        else: #first call
            self._Port = Name
            if not (Name is None):
                self.open()

    @property
    def baudrate(self) -> int:
        """
        Getter property for the current baudrate of the communication.

        Signature:
            None -> int > 0
        
        Version 1.0.0.0
        """
        return self._Baudrate

    @baudrate.setter
    def baudrate(self, Rate: int) -> None:
        """
        Setter property for the communication baudrate. Must be one of the
        standard values.

        Signature:
            int > 0 -> None
        
        Raises:
            TypeError: the argument is not an integer
            ValueError: the argument is not one of the recognized values

        Version 1.0.0.0
        """
        if not isinstance(Rate, int):
            self._closeClean()
            raise TypeError('baudrate {} is not an integer'.format(Rate))
        elif not (Rate in self._KnownBaudrates):
            self._closeClean()
            raise ValueError('unknown baudrate {}'.format(Rate))
        if hasattr(self, '_Baudrate') and (Rate != self._Baudrate):
            self._Baudrate = Rate
            if self.is_open:
                self._closeClean()
                self.open()
        else:
            self._Baudrate = Rate

    @property
    def timeout(self) -> T_REAL_OR_NONE:
        """
        Getter property for the current timeout for reading.

        Signature:
            None -> int >= 0 OR float >=0 OR None
        
        Version 1.0.0.0
        """
        return self._Timeout

    @timeout.setter
    def timeout(self, Value: T_REAL_OR_NONE) -> None:
        """
        Setter property for the reading timeout.

        Signature:
            int >= 0 OR float >=0 OR None -> None
        
        Raises:
            TypeError: the argument is not an integer, nor a float, nor None
            ValueError: the argument is a negative integer or float

        Version 1.0.0.0
        """
        if not (isinstance(Value, (int, float)) or (Value is None)):
            self._closeClean()
            raise TypeError('timeout {} is not a float or None'.format(Value))
        elif isinstance(Value, (int, float)) and (Value < 0):
            self._closeClean()
            raise ValueError('negative timeout {}'.format(Value))
        self._Timeout = Value

    @property
    def write_timeout(self) -> T_REAL_OR_NONE:
        """
        Getter property for the current timeout for writing.

        Signature:
            None -> int >= 0 OR float >=0 OR None
        
        Version 1.0.0.0
        """
        return self._WriteTimeout

    @write_timeout.setter
    def write_timeout(self, Value: T_REAL_OR_NONE) -> None:
        """
        Setter property for the writing timeout.

        Signature:
            int >= 0 OR float >=0 OR None -> None
        
        Raises:
            TypeError: the argument is not an integer, nor a float, nor None
            ValueError: the argument is a negative integer or float

        Version 1.0.0.0
        """
        if not (isinstance(Value, (int, float)) or (Value is None)):
            self._closeClean()
            raise TypeError('write_timeout {} is not a float or None'.format(
                                                                        Value))
        elif isinstance(Value, (int, float)) and (Value < 0):
            self._closeClean()
            raise ValueError('negative write_timeout {}'.format(Value))
        self._WriteTimeout = Value

    #+ methods

    def open(self) -> None:
        """
        Method to (re-) open a connection to the assigned port. It is called
        automatically if the port = 'mock' is passed into the initialization
        method, or the same value is assigned to the property port directly.

        Signature:
            None -> None
        
        Raises:
            serial.SerialException: the port is already opened
        
        Version 1.1.0.0
        """
        if self.port is None:
            raise SerialException('Port is not assigned')
        else:
            if self.is_open:
                self._closeClean()
                raise SerialException('Port was already opened')
            self._objSignal.clear()
            self._objDevice = Thread(target = self._KnownPorts[self.port],
                                        args = (self._objOutgoing,
                                                self._objIncoming,
                                                self._objSignal, self.baudrate))
            self._objDevice.start()

    def close(self) -> None:
        """
        Closes the currently active connection.

        Signature:
            None -> None
        
        Raises:
            serial.SerialException: the port is already closed
        
        Version 1.0.0.0
        """
        if not self.is_open:
            raise SerialException('Connection is inactive - cannot be closed.')
        self._closeClean()

    def read(self, size: int = 1) -> bytes:
        """
        Pulls the incoming buffer for available data and returns the result as
        a bytestring. The requested number of bytes to obtain is passed via the
        optional argument. However, the number of bytes actually returned
        depends on the status of the incoming buffer and the value of the
        property timeout:
            * timeout = None; blocking call, the buffer is pulled indefinitely
                until exactly 'size' bytes are acquired
            * timeout = 0; non-blocking call - if there are more than or equal
                to 'size' bytes in the buffer, exactly 'size' bytes are pulled
                and returned, otherwise all available (< 'size') are returned;
                in any case - exits almost immediately
            * timeout > 0; tries to pull exactly 'size' bytes from the incoming
                buffer and return them, but if less bytes are obtained during
                the 'timeout' period, only the already pulled bytes are returned

        Signature:
            int > 0 -> bytes

        Args:
            size: (optional) int > 0; maximum number of bytes to read from the
                incoming buffer, defaults to 1

        Returns:
            bytes: the read-out data

        Raises:
            TypeError: passed argument is not an integer
            ValueError: passed argument is an integer but not positive
            serial.SerialException: the port is not open
        
        Version 1.0.0.0
        """
        if not isinstance(size, int):
            self._closeClean()
            raise TypeError('{} is not an integer'.format(size))
        elif size <=0:
            self._closeClean()
            raise ValueError('{} is not positive'.format(size))
        if not self.is_open:
            raise SerialException('Connection is inactive')
        Timeout = self.timeout
        Result = []
        if isinstance(Timeout, int) and (not Timeout):
            InWaiting = self.in_waiting
            for _ in range(min(InWaiting, size)):
                Result.append(self._objIncoming.get())
                self._objIncoming.task_done()
        else:
            t0 = time()
            while True:
                try:
                    Result.append(self._objIncoming.get(False))
                    self._objIncoming.task_done()
                    if len(Result) == size:
                        break
                    dt = time() - t0
                    if (not(Timeout is None)) and dt >= Timeout:
                        break
                except Empty:
                    pass
        if not len(Result):
            Result = b''
        else:
            Result = bytes(Result)
        return Result

    def write(self, Data: bytes) -> int:
        """
        Puts all bytes from the passed bytestring into the outgoing buffer. The
        further behavior is defined by the set baudrate and write_timeout:
            * write_timeout = None; blocking call, waits indefinetely until the
                outgoing buffer is emptied
            * write_timeout = 0; non-blocking call returns immediately
            * write_timeout > 0; waits until the outgoing buffer is emptied, but
                no longer than 'write_timeout' - if the timeout is reached,
                raises an exception

        Signature:
            bytes -> int >= 0
        
        Args:
            Data: bytes; bytestring to be sent
        
        Returns:
            int >= 0; number of bytes written into the outgoing buffer, i.e. the
                length of bytestring argument

        Raises:
            TypeError: passed argument is not a bytestring
            serial.SerialException: the port is not open
            serial.SerialTimeoutException: timeout is reached while sending

        Version 1.0.0.0
        """
        if not isinstance(Data, (bytes, bytearray)):
            self._closeClean()
            raise TypeError('{} is not a bytestring'.format(Data))
        if not self.is_open:
            raise SerialException('Connection is inactive')
        for outByte in Data:
            self._objOutgoing.put(outByte)
        WriteTimeout = self.write_timeout
        if (WriteTimeout is None) or (WriteTimeout > 0):
            t0 = time()
            while self.out_waiting > 0:
                dt = time() - t0
                if (not (WriteTimeout is None)) and (dt >= WriteTimeout):
                    self._closeClean()
                    raise SerialTimeoutException('Timeout is reached')
        return len(Data)