#usr/bin/python
"""
Module com_lib.tests.ft001_mock_serial

Functional testing of the module com_lib.mock_serial, which itself implements a
mock serial port connection designed for the unit testing of the communication
layer related modules.

TEST-T-100, covers the requirements REQ-FUN-100, REQ-FUN-101, REQ-FUN-102,
REQ-FUN-103, REQ-AWM-101 and REQ-AWM-102

Sends and receives assynchronously and tests the fast, slow and very slow
response of the mock serial port device as well as the situation of an
emulated disconnect.

Classes:
    Listener
    Monitor

Functions:
    main():
        None -> None
"""

__version__ = "1.0.0.0" #TODO - redefine!
__date__ = "18-06-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os
import time
import threading
import Queue #check!!

#+ module to be tested

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

from com_lib.mock_serial import MockSerial

#classes

class Listener(threading.Thread):
    """
    Serial port (or other stream-like objects) listener designed to be used in a
    separate execution thread. Sub-classes threading.Thread and inherites the
    API, but must be instantiated with 3 arguments: a stream-like object, a
    queue object and a signaling event object.
    
    Reads the input from a stream / port one character at the time, until the
    delimiter character '\x00' is encountered, then places the accumulated
    string into the exchange buffer (queue) without the delimiter.
    
    Version 0.1.0.0
    """
    def __init__(self, Port, ExchangeQueue, StopEvent):
        """
        Initialization
        
        Signature:
            'io.RawIOBase, Queue.Queue, threading.Event -> None
        
        Args:
            Port: io.RawIOBase, instance of, or any API compatible class
                instance; 'serial' port to communicate with
            ExchangeQueue: Queue.Queue, instance of; the exchange buffer, into
                which the receieved messages are placed
            StopEvent: threading.Event, instance of; when it is set, the thread
                is terminated
        
        Version 0.1.0.0
        """
        super(Listener, self).__init__()
        self._StopEvent = StopEvent
        self._ExchangeQueue = ExchangeQueue
        self._Port = Port
    
    def run(self):
        """
        Internal implementation of the start() method expected from a Thread
        instance. Runs in a loop - read-out from the 'serial' port byte-by-byte
        (whean available)- until the stop event is triggered. When the delimiter
        '\x00' character is encountered the accumulated string (except the
        delimiter itself) is placed into the exchange buffer (queue).
        
        Signature:
            None -> None
        
        Version 0.1.0.0
        """
        bsBuffer = b''
        while not self._StopEvent.isSet():
            while self._Port.in_waiting:
                bsChar = self._Port.read()
                if bsChar != b'\x00':
                    bsBuffer = b''.join([bsBuffer, bsChar])
                else:
                    self._ExchangeQueue.put(bsBuffer)
                    bsBuffer = b''

class Monitor(threading.Thread):
    """
    Listener designed to be used in a separate execution thread. Sub-classes
    threading.Thread and inherites the API, but must be instantiated with 2
    arguments: a stream-like object and a signaling event object.
    
    Listens to the output of the Listener class object (via the shared exchange
    buffer / queue) and prints out (to the console) each received string.
    
    Version 0.1.0.0
    """
    def __init__(self, Port, StopEvent):
        """
        Initialization. Creates the internal exchange buffer (queue).
        
        Signature:
            'io.RawIOBase, threading.Event -> None
        
        Args:
            Port: io.RawIOBase, instance of, or any API compatible class
                instance; 'serial' port to communicate with
            StopEvent: threading.Event, instance of; when it is set, the thread
                is terminated
        
        Version 0.1.0.0
        """
        super(Monitor, self).__init__()
        self._StopEvent = StopEvent
        self._ExchangeQueue = Queue.Queue()
        self._Port = Port
    
    def run(self):
        """
        Internal implementation of the start() method expected from a Thread
        instance. Starts a separate thread (Listener class instance) and runs in
        a loop - consumes the exchange buffer (queue) - until the stop event is
        triggered, in which case is closes and deletes the secondary Listener
        thread.
        
        Signature:
            None -> None
        
        Version 0.1.0.0
        """
        objListener = Listener(self._Port, self._ExchangeQueue, self._StopEvent)
        objListener.start()
        while not self._StopEvent.isSet():
            if not self._ExchangeQueue.empty():
                print('Acquired...')
                while not self._ExchangeQueue.empty():
                    gItem = self._ExchangeQueue.get()
                    print(repr(gItem))
        objListener.join()
        del objListener

#functions

def main():
    """
    Test functionality for the libhps.tools.mock_serial.MockSerial class. The
    4 commands must be sent: 'fast', 'slow', 'unknown' and 'very_slow' - with
    3 responses received - 'fast', 'slow' and 'very_slow'. After that the 'quit'
    command must be sent and 2 exceptions are to be raised.
    
    Signature:
        None -> None
    
    Raises:
        serial.serialutil.SerialException: - the intended outcome (sub-class
            of the exceptions.IOError exception)
    
    Version 0.1.0.0
    """
    StopEvent = threading.Event()
    objPortDescription = 'MockSerial'
    objPort = MockSerial()
    print(objPortDescription, ', is open:', objPort.isOpen())
    objMonitor = Monitor(objPort, StopEvent)
    objMonitor.start()
    for strCommand in ['fast', 'slow', 'unknown', 'very_slow']:
        print("Sent:", strCommand)
        objPort.write(strCommand)
    time.sleep(20) #allow all responses to be generated and sent
    print("Sent: quit")
    objPort.write('quit')
    time.sleep(1) #just precaution to ensure that the 'cold disconnect' event
    #+ is processed before the listener + monitor are terminated
    #+ An exception must be raised from the thread, where the Listener instance
    #+ is communicating with the serial port emulation
    StopEvent.set()
    objMonitor.join()
    del objMonitor
    objPort.close()
    # An exception must be raised from the main thread - attempting to close a
    #+ disconenected device

#execution entry point

if __name__ == '__main__':
    main()
