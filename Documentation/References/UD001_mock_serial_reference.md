# UD001 User and API Reference for the Module mock_serial

## Scope

This document provides user reference on the module *com_lib.mock_serial*, including design, functionality, implementation details and API reference.

Functional components:

* Class **MockSerial**
* Function **MockDevice**

Note that this module is intended only for unit testing of the library. End users (not developers) should not use this module.

## Design and Functionality

This module provides a mock serial connection handler class **MockSerial**, which emulates the basic functionality of the **serial.Serial** class from the *pySerial* library, and it is designed for use in the unit testing. It can 'connect' to a mock device, which simply repeats back the bytestring zero-terminated packages sent into it.

The emulated functionality includes:

* Opening a connection by a string identifier of a port. The already open connection cannot be openned again - **SerialException** is raised. However, if the port was explicitely closed by the user request, or implicitely closed due to emulated disconnection, it can be safely re-openned.
* Closing the open connection. The already closed connection (or it never was open) cannot be closed - **SerialException** is raised.
* Blocking and non-blocking acquision of specific number of bytes from the incoming buffer with a specific *read* timeout
* Blocking and non-blocking sending of a bytestring with a specific *write* timeout
* Emulation of the slower or faster connections using the standard baudrates (same as recognized by *pySerial*)
* The port name, baudrate and both read and write timeouts can be passed as keyword arguments of the initializer method or defined later via the respective properties, but before openning the connection

The blocking / non-blocking reading and writing functions in the same way as in the *pySerial* library:

* Reading
  * Timeout is None - blocking call until exactly the requested number of bytes is acquired
  * Timeout is 0 - non-blocking call; as many as possible (present in the incoming buffer) but no more than the requested number of bytes is acquired and returned immediately
  * Time is a positive number - blocking call; the method will not return until the requested number of bytes is acquired or timeout is reached, at which point all acquired bytes are returned
* Writing
  * Timeout is None - blocking call; the passed bytestring is placed into the outgoing buffer, and the method doesn't return control until the outgoing buffer is empty (consumed by the mock device)
  * Timeout is 0 - non-blocking call; the passed bytestring is placed into the outgoing buffer, and the method returns control immediately
  * Timeout is a positive number - blocking call; the passed bytestring is placed into the outgoing buffer, and the method doesn't return control until the outgoing buffer is empty (consumed by the mock device) or timeout is reached - in the second case **SerialTimeoutException** is raised

In addition, a special command b'quit\x00' can be sent via the mock serial connection into the mock device in order emulate disconnection.

The mock device simply repeats back each zero-terminated package (bytestring), except for the 'kill command' (see above).

This functionality allows unit testing of the higher level *pySerial* wrapper objects at the different speed of the connection, and even a simulation of a disconnection event.

## Implementation Details

The components and class diagrams of the module are shown below

![Components diagram](../UML/mock_serial/mock_serial_components.png)

![Class diagram](../UML/mock_serial/mock_serial_classes.png)

## API

### Functions

**MockDevice**(Input, Output, StopEvent, Baudrate)

_**Signature**_:

queue.Queue, queue,Queue, threading.Event, int > 0 -> None

_**Args**_:

* *Input*: **queue.Queue**; input buffer (from the device's perspective), from which the commands are to be read

* *Output*: **queue.Queue**; output buffer (from the device's perspective), into which the response to a command is to be written

* *StopEvent*: **threading.Event**; an object signaling the function to terminate if set

* *Baudrate*: **int** > 0; emulation of the different data transfer rates, i.e. introduces a delay of 8.0 / Baudrate between each byte read from the input and send to the output

_**Description**_:

Emulation of a simple device, which repeats back every command send, until the stop event is not set externally or b'quit' command is received. Note that b'\x00' is used as the terminator between the commands, and it is also send back. The response to the b'quit' command is not sent.

This function is designed to be executed in a separate thread.

### Classes

#### Class MockSerial

_**Description**_:

Emulation of the minimal API compatible with the **serial.Serial** class, see PyPI library *pySerial*. Executes the function *MockDevice*() in a separate thread upon calling the method *open*(); one should assign *port* = 'mock' first. This approach simulates a real serial port connection to a device, which echoes back the send data. Thus the blocking and non-blocking reading and writing at the different baudrates can be safely tested.

_**Properties**_:

* *is_open*: (read-only) **bool**
* *in_waiting*: (read-only) **int** >= 0
* *out_waiting*: (read-only) **int** >= 0
* *port*: **str** OR **None**
* *baudrate*: **int** > 0
* *timeout*: **int** >= 0 OR **float** >= 0 OR **None**
* *write_timeout*: **int** >=0 OR **float** >= 0 OR **None**

_**Instantiation**_:

**\_\_init\_\_**(* *kwargs)

Signature:

/* *kwargs/ -> None

_**Raises**_:

* **TypeError**: inappropriate data type of a recognised keyword argument
* **ValueError**: inappropriate value of a proper data type of a recognized keyword argument
* **serial.SerialExeption**: unknown port value (string)

_**Description**_:

Initialization. Creates instance attributes and sets the connection settings according to the passed keyword arguments values, which can include:

* *port* - None or str
* *baudrate* - integer, any standard baudrate, e.g. 50, 9600, 115200
* *timeout* and *write_timeout* - None or non-negative integer or float

If the known value is assigned to the port (e.g. 'mock') the connection to the mock device is openned automatically.

_**Methods**_:

**open**()

_**Signature**_:

None -> None

_**Raises**_:

**serial.SerialException**: the port is already opened

_**Description**_:

Method to (re-) open a connection to the assigned port. It is called automatically if the *port* = 'mock' is passed into the initialization method, or the same value is assigned to the property port directly.

**close**()

_**Signature**_:

None -> None

_**Raises**_:

**serial.SerialException**: the port is already closed

_**Description**_:

Closes the currently active connection.

**read**(size = 1)

_**Signature**_:

/int >= 1/ -> bytes

_**Args**_:

*size*: (optional) **int** > 0; maximum number of bytes to read from the incoming buffer, defaults to 1

_**Returns**_:

**bytes**: the read-out data

_**Raises**_:

* **TypeError**: passed argument is not an integer
* **ValueError**: passed argument is an integer but not positive
* **serial.SerialException**: the port is not open

_**Description**_:

Pulls the incoming buffer for available data and returns the result as a bytestring. The requested number of bytes to obtain is passed via the optional argument. However, the number of bytes actually returned depends on the status of the incoming buffer and the value of the property timeout:

* *timeout* = None; blocking call, the buffer is pulled indefinitely until exactly 'size' bytes are acquired
* *timeout* = 0; non-blocking call - if there are more than or equal to 'size' bytes in the buffer, exactly 'size' bytes are pulled and returned, otherwise all available (< 'size') are returned; in any case - exits almost immediately
* *timeout* > 0; tries to pull exactly 'size' bytes from the incoming buffer and return them, but if less bytes are obtained during the 'timeout' period, only the already pulled bytes are returned

**write**(Data)

_**Signature**_:

bytes -> int >= 0

_**Args**_:

*Data*: **bytes**; bytestring to be sent

_**Returns**_:

**int** >= 0: number of bytes written into the outgoing buffer, i.e. the length of bytestring argument

_**Raises**_:

* **TypeError**: passed argument is not a bytestring
* **serial.SerialException**: the port is not open
* **serial.SerialTimeoutException**: timeout is reached while sending

_**Description**_:

Puts all bytes from the passed bytestring into the outgoing buffer. The further behavior is defined by the set baudrate and write_timeout:

* *write_timeout* = None; blocking call, waits indefinetely until the outgoing buffer is emptied
* *write_timeout* = 0; non-blocking call returns immediately
* *write_timeout* > 0; waits until the outgoing buffer is emptied, but no longer than 'write_timeout' - if the timeout is reached, raises an exception
