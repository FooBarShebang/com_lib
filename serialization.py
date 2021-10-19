#usr/bin/python3
"""
Module com_lib.serialization

Functions:
    

Classes:
    Serializable
    SerNULL
    SerStruct
    SerArray
    SerDynamicArray
"""

__version__ = "1.0.0.0"
__date__ = "18-10-2021"
__status__ = "Development"

#imports

#+ standard libaries

import os
import sys
import abc
import json
import ctypes

import collections.abc

from typing import Optional, Union, List, Dict, Any, NoReturn, Sequence, Mapping
from typing import ClassVar, Tuple

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

TDict = Dict[str, Any]

TList = List[Any]

TMap = Mapping[str, Any]

TSeq = Sequence[Any]

#functions

def IsC_Scalar(gType: Any) -> bool:
    """
    Helper function to check if the passed data type is a scalar C type.
    
    Signature:
        type A -> bool
    
    Args:
        gType: type A; the data type to be checked
    
    Returns:
        bool: True if check passes, False otherwise
    
    Version 1.0.0.0
    """
    try:
        bResult = issubclass(gType, ctypes._SimpleCData)
    except TypeError:
        bResult = False
    return bResult

#classes

#+ ABC / Prototype / Interface
class Serializable(abc.ABC):
    """
    Prototype, ABC for the auto-serializable compound data types, designed
    without internal state, i.e. as an Interface.
    
    The derived classes MUST re-define the public methods getSize(), packBytes()
    and getNative(), as well as the 'private' methods _parseBuffer() and
    _checkObjectContent().
    
    It also modifies the access / attribute resolution scheme. The sub-classes
    might be required to override or walk-around the attribute resolution
    'magic' methods.
    
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
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes -> None
        
        Args:
            Data: bytes; data to be checked
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    #special methods
    
    def __getattribute__(self, name: str) -> Any:
        """
        Special method to hook into the read access to the attributes. Prohibs
        access to any attribute with the name starting with, at least, one
        underscore, except for the '__name__', which is required for the proper
        functioning of the custom exceptions.
        
        Signature:
            str -> type A
        
        Raises:
            UT_AttributeError: attribute does not exists, OR its name starts
                with, at least, one underscore, except for two special cases
                __name__ and __class__
        
        Version 1.0.0.0
        """
        if name in ('__class__'):
            return object.__getattribute__(self, name)
        elif name == '__name__':
            return self.__class__.__name__
        elif name.startswith('_'):
            raise UT_AttributeError(self, name, SkipFrames = 1)
        else:
            try:
                Result = object.__getattribute__(self, name)
                return Result
            except AttributeError:
                raise UT_AttributeError(self, name, SkipFrames = 1) from None
    
    def __setattr__(self, name: str, value: Any) -> NoReturn:
        """
        Special method to hook into the write access to the attributes. Prohibs
        assignment to any attribute.
        
        Signature:
            str, type A -> None
        
        Raises:
            UT_AttributeError: always raised
        
        Version 1.0.0.0
        """
        raise UT_AttributeError(self, name, SkipFrames = 1)
    
    #public API
    
    @classmethod
    @abc.abstractmethod
    def getSize(cls) -> TIntNone:
        """
        Prototype for the method to obtain the current size in bytes of the
        stored data.
        
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
            raise UT_ValueError(Data, 'not a valid JSON string',
                                                    SkipFrames = 1) from None
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


#++ new data type!

TElement = Union[ctypes._SimpleCData, Serializable]

#+ main classes
class SerNULL(Serializable):
    """
    Implements auto-serilizable and de-serializable object representing NULL /
    None empty response or data load. Can be instantiate without an argument or
    with a single optional argument, which is simply ignored.
    
    Class methods:
        getSize():
            None -> int = 0
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
            None -> None
    
    Version 1.0.0.0
    """
    
    #special methods
    
    def __init__(self, Data: Any = None) -> None:
        """
        Initialization method. Does nothing. Added for the consistent signature.
        
        Signature:
            /type A/ -> None
        
        Args:
            Data: (optional) type A; simply ignored even if provided
        
        Version 1.0.0.0
        """
        pass
    
    #private methods
    
    @classmethod
    def _checkObjectContent(cls, Data: None) -> None:
        """
        Private class method to check if the extracted JSON object matches the
        declared data structure of the class. Only None value is acceptable.
        
        Signature:
            None-> None
        
        Args:
            Data: None; any other value is an error
        
        Raises:
            UT_TypeError: any value but None is recieved
        
        Version 1.0.0.0
        """
        if not (Data is None):
            raise UT_TypeError(Data, type(None), SkipFrames = 2)
    
    @classmethod
    def _parseBuffer(cls, Data: bytes) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition. Only
        an empty bytestring is allowed.
        
        Signature:
            bytes -> None
        
        Args:
            Data: bytes; only an empty bytestring is acceptable
        
        Raises:
            UT_ValueError: size of the passed 
        
        Version 1.0.0.0
        """
        if len(Data):
            raise UT_ValueError(repr(Data), 'empty bytestring', SkipFrames = 2)
    
    #public API
    
    @classmethod
    def getSize(cls) -> int:
        """
        Method to obtain the current size in bytes of the stored data.
        
        Signature:
            None -> int = 0
        
        Returns:
            int = 0: always zero value is returned
        
        Version 1.0.0.0
        """
        return 0
    
    def getNative(self) -> None:
        """
        Method for convertion of the stored data into native Python data type.
        
        Signature:
            None -> None
        
        Returns:
            None: native Python type representation of the stored data
        
        Version 1.0.0.0
        """
        return None
    
    def packBytes(self) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            None -> bytes
        
        Returns:
            bytes: an empty bytestring
        
        Version 1.0.0.0
        """
        return b''

class SerStruct(Serializable):
    """
    Implements auto-serilizable and de-serializable object representing C-struct
    like structured data storage. Can be instantiate without an argument or
    with a single optional argument of a mapping type or another structure.
    
    Class methods:
        getSize():
            None -> int >= 0 OR None
        unpackBytes(Data):
            bytes -> 'SerStruct
        unpackJSON(Data):
            str -> 'SerStruct
    
    Methods:
        packBytes():
            None -> bytes
        packJSON():
            None -> str
        getNative():
            None -> dict(str -> type A)
    
    Version 1.0.0.0
    """
    
    #private class attributes - data structure definition
    
    _Fields: ClassVar[Tuple[Tuple[str, TElement], ...]] = tuple()
    #must be a tuple(tuple(str, type A))
    
    #special methods
    
    def __init__(self, Data: Optional[Union[TMap, Serializable]]=None) -> None:
        """
        Initialization method - copies the data from the same named keys /
        fields of the passed object into the respective fields of the created
        instance.
        
        Signature:
            /dict(str -> type A) OR SerStruct/ -> None
        
        Args:
            Data: (optional) dict(str -> type A) OR SerStruct; dictionary or
                another instance of SerStruct class
        
        Raises:
            UT_TypeError: passed argument is not a mapping type or an instance
                of sub-class of SerStruct
        
        Version 1.0.0.0
        """
        Fields = object.__getattribute__(self, '_Fields')
        dictFields = object.__getattribute__(self, '__dict__')
        for Field, DataType in Fields:
            if IsC_Scalar(DataType):
                gTemp = DataType()
                dictFields[Field] = gTemp.value
                del gTemp
            else:
                try:
                    if issubclass(DataType, (SerArray, SerStruct)):
                        #TODO check dynamic length not in final position
                        dictFields[Field] = DataType()
                    else:
                        #raise exception here!
                        pass
                except TypeError: #not a type
                    #raise exception here!
                    pass
        if not (Data is None):
            if not isinstance(Data, (collections.abc.Mapping, SerStruct)):
                raise UT_TypeError(Data, (collections.abc.Mapping, SerStruct),
                                                                SkipFrames = 1)
    
    #private methods
    
    @classmethod
    def _checkObjectContent(cls, Data: TDict) -> None:
        """
        Private class method to check if the extracted JSON object matches the
        declared data structure of the class.
        
        Signature:
            dict(str -> type A) -> None
        
        Args:
            Data: dict(str -> type A); data to be checked
        
        Raises:
            UT_TypeError: the type of the passed argument is not compatible with
                the class
            UT_ValueError: the internal structure of the passed object does not
                match the defined class structure
        
        Version 1.0.0.0
        """
        if not isinstance(Data, dict):
            raise UT_TypeError(Data, dict, SkipFrames = 2)
    
    @classmethod
    def _parseBuffer(cls, Data: bytes) -> TDict:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes -> dict(str -> type A)
        
        Args:
            Data: bytes; data to be checked
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    #public API
    
    @classmethod
    def getSize(cls) -> TIntNone:
        """
        Method to obtain the current size in bytes of the stored data.
        
        Signature:
            None -> int >= 0 OR None
        
        Returns:
            * int >= 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
            * None: indication that the instance is not a fixed size object
        
        Version 1.0.0.0
        """
        pass
    
    def getNative(self) -> TDict:
        """
        Method for convertion of the stored data into native Python data type.
        
        Signature:
            None -> dict(str -> type A)
        
        Returns:
            dict(str -> type A): native Python type representation of the stored
                data
        
        Version 1.0.0.0
        """
        pass
    
    def packBytes(self) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            None -> bytes
        
        Returns:
            bytes: bytestring representing the entire stored data
        
        Version 1.0.0.0
        """
        pass

class SerArray(Serializable):
    """
    Implements auto-serilizable and de-serializable object representing C-array
    like structured data storage. Can be instantiate without an argument or
    with a single optional argument of a sequence type or another array.
    
    Class methods:
        getSize():
            None -> int >= 0 OR None
        unpackBytes(Data):
            bytes -> 'SerArray
        unpackJSON(Data):
            str -> 'SerArray
    
    Methods:
        packBytes():
            None -> bytes
        packJSON():
            None -> str
        getNative():
            None -> list(type A)
    
    Version 1.0.0.0
    """
    
    #private class attributes - data structure definition
    
    _ElementType: ClassVar[TElement] = ctypes.c_int32
    
    _Length: ClassVar[int] = 0
    
    #special methods
    
    def __init__(self, Data: Optional[Union[TSeq, Serializable]]=None) -> None:
        """
        Initialization method - copies the data from the same named keys /
        fields of the passed object into the respective fields of the created
        instance.
        
        Signature:
            /seq(str -> type A) OR 'SerArray/ -> None
        
        Args:
            Data: (optional) seq(str -> type A) OR 'SerArray; sequence or an
                instance of SerArray (sub-) class
        
        Raises:
            UT_TypeError: passed argument is not a sequence type or an instance
                of sub-class of SerArray or SerDynamicArray
        
        Version 1.0.0.0
        """
        ElementType = object.__getattribute__(self, '_ElementType')
        Length = object.__getattribute__(self, '_Length')
        #structure check
        if isinstance(Length, int):
            if Length > 0:
                if IsC_Scalar(ElementType):
                    lstContent = []
                    for _ in range(Length):
                        lstContent.append(ElementType().value)
                    object.__setattr__(self, '_Data', lstContent)
                else:
                    try:
                        if issubclass(DataType, (SerArray, SerStruct)):
                            #TODO check dynamic length element
                            lstContent = []
                            for _ in range(Length):
                                lstContent.append(ElementType())
                            object.__setattr__(self, '_Data', lstContent)
                        else:
                            #raise exception here!
                            pass
                    except TypeError: #not a type
                        #raise exception here!
                        pass
            else:
                #raise error
                pass
        else:
            #raise error
            pass
        if not (Data is None):
            bCond1 = not isinstance(Data, (collections.abc.Sequence, SerArray))
            bCond2 = isinstance(Data, (str, bytes))
            if bCond1 or bCond2:
                raise UT_TypeError(Data, (collections.abc.Sequence, SerArray),
                                                                SkipFrames = 1)
    
    #private methods
    
    @classmethod
    def _checkObjectContent(cls, Data: TList) -> None:
        """
        Private class method to check if the extracted JSON object matches the
        declared data structure of the class.
        
        Signature:
            list(type A) -> None
        
        Args:
            Data: list(type A); data to be checked
        
        Raises:
            UT_TypeError: the type of the passed argument is not compatible with
                the class
            UT_ValueError: the internal structure of the passed object does not
                match the defined class structure
        
        Version 1.0.0.0
        """
        if not isinstance(Data, list):
            raise UT_TypeError(Data, list, SkipFrames = 2)
    
    @classmethod
    def _parseBuffer(cls, Data: bytes) -> TList:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes -> list(type A)
        
        Args:
            Data: bytes; data to be checked
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    #public API
    
    @classmethod
    def getSize(cls) -> int:
        """
        Method to obtain the current size in bytes of the stored data.
        
        Signature:
            None -> int > 0
        
        Returns:
            int >= 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
        
        Version 1.0.0.0
        """
        pass
    
    def getNative(self) -> TList:
        """
        Method for convertion of the stored data into native Python data type.
        
        Signature:
            None -> list(type A)
        
        Returns:
            list(type A): native Python type representation of the stored data
        
        Version 1.0.0.0
        """
        pass
    
    def packBytes(self) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            None -> bytes
        
        Returns:
            bytes: bytestring representing the entire stored data
        
        Version 1.0.0.0
        """
        pass

class SerDynamicArray(SerArray):
    """
    Implements auto-serilizable and de-serializable object representing C-array
    like structured data storage. Can be instantiate without an argument or
    with a single optional argument of a sequence type or another array.
    
    Class methods:
        getSize():
            None -> int >= 0 OR None
        unpackBytes(Data):
            bytes -> 'SerDynamicArray
        unpackJSON(Data):
            str -> 'SerDynamicArray
    
    Methods:
        packBytes():
            None -> bytes
        packJSON():
            None -> str
        getNative():
            None -> list(type A)
    
    Version 1.0.0.0
    """
    
    #special methods
    
    def __init__(self, Data: Optional[Union[TSeq, Serializable]]=None) -> None:
        """
        Initialization method - copies the data from the same named keys /
        fields of the passed object into the respective fields of the created
        instance.
        
        Signature:
            /seq(str -> type A) OR 'SerArray/ -> None
        
        Args:
            Data: (optional) seq(str -> type A) OR 'SerArray; sequence or an
                instance of SerArray (sub-) class
        
        Raises:
            UT_TypeError: passed argument is not a sequence type or an instance
                of sub-class of SerArray or SerDynamicArray
        
        Version 1.0.0.0
        """
        ElementType = object.__getattribute__(self, '_ElementType')
        #structure check
        if not IsC_Scalar(ElementType):
            try:
                if issubclass(DataType, (SerArray, SerStruct)):
                    #TODO check dynamic length element
                    pass
                else:
                    #raise exception here!
                    pass
            except TypeError: #not a type
                #raise exception here!
                pass
        object.__setattr__(self, '_Data', [])
        if not (Data is None):
            bCond1 = not isinstance(Data, (collections.abc.Sequence, SerArray))
            bCond2 = isinstance(Data, (str, bytes))
            if bCond1 or bCond2:
                raise UT_TypeError(Data, (collections.abc.Sequence, SerArray),
                                                                SkipFrames = 1)
    
    #private methods
    
    @classmethod
    def _checkObjectContent(cls, Data: Any) -> None:
        """
        Private class method to check if the extracted JSON object matches the
        declared data structure of the class.
        
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
        if not isinstance(Data, list):
            raise UT_TypeError(Data, list, SkipFrames = 2)
    
    @classmethod
    def _parseBuffer(cls, Data: bytes) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes -> None
        
        Args:
            Data: bytes; data to be checked
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    #public API
    
    @classmethod
    def getSize(cls) -> None:
        """
        Method to obtain the current size in bytes of the stored data.
        
        Signature:
            None -> None
        
        Returns:
            None: indication that the instance is not a fixed size object
        
        Version 1.0.0.0
        """
        return None