#usr/bin/python3
"""
Module com_lib.serialization

Functions:
    

Classes:
    
    
"""

__version__ = "1.0.0.0"
__date__ = "14-10-2021"
__status__ = "Development"

#imports

#+ standard libaries

import os
import sys
import abc
import json

from typing import Union, List, Dict, Any

#+ custom modules

MODULE_PATH = os.path.realpath(__file__)
LIB_FOLDER = os.path.dirname(MODULE_PATH)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

from introspection_lib.base_exceptions import UT_ValueError, UT_TypeError
from introspection_lib.base_exceptions import UT_AttributeError, UT_IndexError

#types

TIntNone = Union[int, None]

#classes

class Serializable(abc.ABC):
    """
    Prototype, ABC for the auto-serializable compound data types, designed
    without internal state, i.e. as an Interface.
    
    The derived classes MUST re-define the public methods getSize(), packBytes()
    and getNative(), as well as the 'private' methods _parseBuffer() and
    _checkObjectContent().
    
    Class methods:
        getSize():
            None -> int >=0 OR None
        unpackBytes(Data):
            bytes -> 'Serializable
        unpackJSON(Data):
            str -> 'Serializable
    
    Methods:
        packBytes():
            None -> bytes
        packJSON():
            None -> str
        getNative():
            None -> type A
    
    Version 1.0.0.0
    """
    
    #private methods
    
    @classmethod
    @abc.abstractmethod
    def _checkObjectContent(cls, Data: Any) -> None:
        """
        Prototype for the private class method to check if the extracted JSON
        object matches the declared data structure of the class.
        
        Signature:
            type A -> None
        
        Args:
            Data: type A; any type data to be checked
        
        Raises:
            UT_TypeError: the type of the passed argument is not compatible with
                the class
            UT_ValueError: the internal structure of the passed object does not
                match the defined class structure
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    @abc.abstractmethod
    def _parseBuffer(cls, Data: bytes) -> None:
        """
        Prototype for the private class method to parse the content of the
        passed byte string into a native Python object using the class data
        structure definition.
        
        Signature:
            type A -> None
        
        Args:
            Data: type A; any type data to be checked
        
        Raises:
            UT_ValueError: size of the passed 
        
        Version 1.0.0.0
        """
        pass
    
    #public API
    
    @classmethod
    @abc.abstractmethod
    def getSize(cls) -> TIntNone:
        """
        Signature:
            None -> int >= 0 OR None
        
        Returns:
            * int >= 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
            * None: indication that the instance is not a fixed size object
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    def unpackBytes(cls, Data: bytes):
        """
        Class method responsible for creation of a new instance using the data
        extracted from the passed bytes packed representation.
        
        Signature:
            str -> 'Serializable
        
        Args:
            Data: bytes; bytes representation of the data
        
        Returns:
            'Serializable: an instance of a sub-class of Serializable, same as
                the current instance class
        
        Raises:
            UT_TypeError: passed argument is not a byte string
            UT_ValueError: the size of the byte string does not match the size
                of the declared class data structure
        
        Version 1.0.0.0
        """
        if not isinstance(Data, bytes):
            raise UT_TypeError(Data, bytes, SkipFrames = 1)
        funcParser = type.__getattribute__(cls, '_parseBuffer')
        funcParser(Data) #supposed to raise UT_ValueError if size is wrong
        return cls(Data)
    
    @classmethod
    def unpackJSON(cls, Data: str):
        """
        Class method responsible for creation of a new instance using the data
        extracted from the passed JSON encoded string.
        
        Signature:
            str -> 'Serializable
        
        Args:
            Data: str; JSON string data
        
        Returns:
            'Serializable: an instance of a sub-class of Serializable, same as
                the current instance class
        
        Raises:
            UT_TypeError: passed argument is not a string OR the JSON encoded
                data type is not compatible with the class
            UT_ValueError: the passed string is not a JSON object, or its
                internal structure does not match the defined class structure
        
        Version 1.0.0.0
        """
        if not isinstance(Data, str):
            raise UT_TypeError(Data, str, SkipFrames = 1)
        try:
            gNative = json.loads(Data)
        except ValueError as err:
            raise UT_ValueError(Data, 'not a valid JSON string', SkipFrames = 1)
        funcChecker = type.__getattribute__(cls, '_checkObjectContent')
        funcChecker(gNative) #supposed to raise UT_TypeError or UT_ValueError
        #+ if type / structure does not meet class definition
        return cls(gNative)
    
    @abc.abstractmethod
    def packBytes(self) -> bytes:
        """
        Prototype method for serialization of the stored data into bytes.
        
        Signature:
            None -> bytes
        
        Returns:
            bytes: bytestring representing the entire stored data
        
        Version 1.0.0.0
        """
        pass
    
    def packJSON(self) -> str:
        """
        Instance method responsible for the serialization of the stored data
        into JSON format string.
        
        Signature:
            None -> str
        
        Returns:
            str: JSON representation of the stored data
        
        Version 1.0.0.0
        """
        gNative = self.getNative()
        strData = json.dumps(gNative)
        return strData
    
    @abc.abstractmethod
    def getNative(self) -> Any:
        """
        Prototype method for convertion of the stored data into native Python
        data type.
        
        Signature:
            None -> type A
        
        Returns:
            type A: native Python type representation of the stored data
        
        Version 1.0.0.0
        """
        pass