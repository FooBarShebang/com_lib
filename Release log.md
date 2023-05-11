# Release log of library com_lib

## 2023-05-11 v1.1.0

* Cleaned up code
* Added prototype / meta-class for the serializable proxies for C scalar types
* Improved little- and big-endian (de-) serialization, now compatible with **ctypes.c_bool** type

## 2021-11-11

Added dedicated test cases for the implementation of *getSize*() method of all serializable classes.

## 2021-11-10 v1.0.1

Found and fixed bug in *serialization.SerStruct.getSize*() method.

## 2021-11-09 v1.0.0

Fully documented. The first official release.

## 2021-11-01

* Implemented and tested auto-serializable classes
* Finished testing of the communication wrapper
* Built and uploaded PyPI distibutable
* Documenation is pending

## 2021-08-18

* Implemented and mostly tested the serial communication wrapper

## 2021-08-13

* Implemented and tested the mock serial port API and a mock device
