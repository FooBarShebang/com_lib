#!/usr/bin/python3
"""
Library com_lib

Abstraction layer for USB COM-port bi-directional communication. Provides
automated byte packing and unpacking for structured and container-like data
storage classes, automated COBS encoding / decoding of the data, data sending
and receiving as 0-terminated packages in the synchronous and asynchronous modes
using a queue.

Modules:
    serialization: NULL / None, C-struct, fixed and dynamic length C-array
        objects with the built-in JSON and byte-string (de-) serialization,
        consistent data structure between instances of the same class and
        data sanity checks
    serial_port_com: wrapper, abstraction layer implementing package-oriented,
        COBS encoded, synchronous and asynchronous bi-directional communication
        via (virtual) serial ports

"""

__project__ ='Serial port communication wrapper'
__version_info__= (1, 0, 1)
__version_suffix__= '-release'
__version__= ''.join(['.'.join(map(str, __version_info__)), __version_suffix__])
__date__ = '10-11-2021'
__status__ = 'Production'
__author__ = 'Anton Azarov'
__maintainer__ = 'a.azarov@diagnoptics.com'
__license__ = 'Public Domain'
__copyright__ = 'Diagnoptics Technologies B.V.'

__all__ = ['serial_port_com', 'serialization']