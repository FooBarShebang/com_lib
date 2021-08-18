#usr/bin/python3
"""
Module com_lib.tests.ft001_serial_port_com

Functional tests for the function com_lib.serial_port_com.list_ports
"""

__version__ = "1.0.0.0"
__date__ = "17-08-2021"
__status__ = "Testing"

#imports

#+ standard libraries

import sys
import os

#+ my libraries

TEST_FOLDER = os.path.dirname(os.path.realpath(__file__))
LIB_FOLDER = os.path.dirname(TEST_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

#++ actual imports

from com_lib.serial_port_com import list_ports

#execution entry point

if __name__ == '__main__':
    lstPorts = list_ports()
    for Path, VID, PID in list_ports():
        print('Port path: {}, VID: {} / hex {}, PID: {} / hex {}'.format(
                                            Path, VID, hex(VID), PID, hex(PID)))