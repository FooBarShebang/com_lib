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
    and getNative(), as well as the 'private' class methods _parseBuffer(),
    _checkObjectContent() and _checkDefinition().
    
    It also modifies the access / attribute resolution scheme. The sub-classes
    might be required to override or walk-around the attribute resolution
    'magic' methods.
    
    Class methods:
        getSize():
            None -> int >=0 OR None
        unpackBytes(Data, BigEndian = False):
            bytes /, bool / -> 'Serializable
        unpackJSON(Data):
            str -> 'Serializable
    
    Methods:
        packBytes(BigEndian = False):
            /bool/ -> bytes
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
    def _parseBuffer(cls, Data: bytes, BigEndian: bool = False) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        Prototype.
        
        Signature:
            bytes /, bool/ -> None
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    @abc.abstractmethod
    def _checkDefinition(cls) -> None:
        """
        Private class method to check the definition of the data structure of
        the class. Supposed to be called by all class methods, including the
        unpacking (constructors), and the initialization instance method.
        Prototype.
        
        Signature:
            None -> None
        
        Raises:
            UT_TypeError: required class private attributes are missing OR
                OR they hold wrong type vales OR elements / fields type
                declaration is incorrect
        
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
        Prototype for the method to obtain the declared size in bytes of the
        stored data.
        
        Signature:
            None -> int >= 0 OR None
        
        Returns:
            * int >= 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
            * None: indication that the instance is not a fixed size object
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    def unpackBytes(cls, Data: bytes, BigEndian: bool = False):
        """
        Class method responsible for creation of a new instance using the data
        extracted from the passed bytes packed representation.
        
        Signature:
            str /, bool/ -> 'Serializable
        
        Args:
            Data: bytes; bytes representation of the data
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
        Returns:
            'Serializable: an instance of a sub-class of Serializable, same as
                the current instance class
        
        Raises:
            UT_TypeError: passed argument is not a byte string OR the class
                data structure is wrongly defined
            UT_ValueError: the size of the byte string does not match the size
                of the declared class data structure
        
        Version 1.0.0.0
        """
        if not isinstance(Data, bytes):
            raise UT_TypeError(Data, bytes, SkipFrames = 1)
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        funcParser = type.__getattribute__(cls, '_parseBuffer')
        NativeData = funcParser(Data, BigEndian = BigEndian)
        #supposed to raise UT_ValueError if size is wrong
        return cls(NativeData)
    
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
                data type is not compatible with the class OR the class data
                structure is wrongly defined
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
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        funcChecker = type.__getattribute__(cls, '_checkObjectContent')
        funcChecker(gNative) #supposed to raise UT_TypeError or UT_ValueError
        #+ if type / structure does not meet class definition
        return cls(gNative)
    
    @abc.abstractmethod
    def packBytes(self, BigEndian: bool = False) -> bytes:
        """
        Prototype method for serialization of the stored data into bytes.
        
        Signature:
            /bool/ -> bytes
        
        Args:
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
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
        unpackBytes(Data, BigEndian = False):
            bytes /, bool/ -> SerNULL
        unpackJSON(Data):
            str -> SerNULL
    
    Methods:
        packBytes(BigEndian = False):
            /bool/ -> bytes
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
    def _parseBuffer(cls, Data: bytes, BigEndian: bool = False) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition. Only
        an empty bytestring is allowed.
        
        Signature:
            bytes /, bool/ -> None
        
        Args:
            Data: bytes; only an empty bytestring is acceptable
            BigEndian: (optional) bool; ignored
        
        Raises:
            UT_ValueError: size of the passed 
        
        Version 1.0.0.0
        """
        if len(Data):
            raise UT_ValueError(repr(Data), 'empty bytestring', SkipFrames = 2)
    
    @classmethod
    def _checkDefinition(cls) -> None:
        """
        Private class method to check the definition of the data structure of
        the class. Supposed to be called by all class methods, including the
        unpacking (constructors), and the initialization instance method.
        Does nothing.
        
        Signature:
            None -> None
        
        Version 1.0.0.0
        """
        pass
    
    #public API
    
    @classmethod
    def getSize(cls) -> int:
        """
        Method to obtain the declared size in bytes of the stored data.
        
        Signature:
            None -> int = 0
        
        Returns:
            int = 0: always zero value is returned
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
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
    
    def packBytes(self, BigEndian: bool = False) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            /bool/ -> bytes
        
        Args:
            BigEndian: (optional) bool; ignored
        
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
    
    Sub-classes must define their fields in the private class attribute
    _Fields as a tuple of 2-tuples ('name': type), where type might be either
    a ctypes primitive type or SerStruct, SerArray or SerDynamicArray. The
    dynamic length object is allowed only as the last field!
    
    Class methods:
        getSize():
            None -> int >= 0 OR None
        unpackBytes(Data, BigEndian = False):
            bytes /, bool/ -> 'SerStruct
        unpackJSON(Data):
            str -> 'SerStruct
    
    Methods:
        packBytes(BigEndian = False):
            /bool/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> dict(str -> type A)
    
    Version 1.0.0.0
    """
    
    #private class attributes - data structure definition
    
    _Fields: ClassVar[Tuple[Tuple[str, TElement], ...]] = tuple()
    #must be a tuple(tuple(str, type A)), where type A is either C primitive
    #+ or a serializable structure / array
    
    #special methods
    
    def __setattr__(self, name: str, value: Any) -> NoReturn:
        """
        Special method to hook into the write access to the attributes. Prohibs
        assignment to any attribute except the declared fields, from which only
        the C primitive type fields can be assigned to and only if the value
        is compatible with the declared type.
        
        Signature:
            str, type A -> None
        
        Raises:
            UT_AttributeError: assignment to a not declared C privite type field
            UT_TypeError: value is incompatible with the declared type of the
                field
        
        Version 1.0.0.0
        """
        Fields = object.__getattribute__(self, '_Fields')
        dictMapping = {strKey : tType for strKey, tType in Fields}
        if (name in dictMapping) and (IsC_Scalar(dictMapping[name])):
            try:
                NewValue = dictMapping[name](value).value
            except (TypeError, ValueError):
                raise UT_TypeError(value, dictMapping[name], SkipFrames = 1)
            object.__setattr__(self, name, NewValue)
        else:
            raise UT_AttributeError(self, name, SkipFrames = 1)
    
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
                of sub-class of SerStruct OR the data structure of the class
                is not defined properly
        
        Version 1.0.0.0
        """
        funChecker = object.__getattribute__(self, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        if not (Data is None):
            if not isinstance(Data, (collections.abc.Mapping, SerStruct)):
                raise UT_TypeError(Data, (collections.abc.Mapping, SerStruct),
                                                                SkipFrames = 1)
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
                        dictFields[Field] = DataType()
                    else:
                        #raise exception here!
                        pass
                except TypeError: #not a type
                    #raise exception here!
                    pass
    
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
    def _parseBuffer(cls, Data: bytes, BigEndian: bool = False) -> TDict:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes /, bool/ -> dict(str -> type A)
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    def _checkDefinition(cls) -> None:
        """
        Private class method to check the definition of the data structure of
        the class. Supposed to be called by all class methods, including the
        unpacking (constructors), and the initialization instance method.
        
        Signature:
            None -> None
        
        Raises:
            UT_TypeError: required class private attributes are missing OR
                OR they hold wrong type vales OR fields type declaration is
                incorrect
        
        Version 1.0.0.0
        """
        for strName in ('_Fields', ):
            try:
                type.__getattribute__(cls, strName)
            except AttributeError:
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = 'Wrong definition of {} - {} is missing'.format(
                                                        cls.__name__, strName)
                objError.args = (strError, )
                raise objError from None
        #check _Field attribute 
        Fields = type.__getattribute__(cls, '_Fields')
        if not isinstance(Fields, tuple):
            objError = UT_TypeError(Fields, tuple, SkipFrames = 2)
            strError = 'Wrong definition of {}._Fields - {}'.format(
                                                cls.__name__, objError.args[0])
            objError.args = (strError, )
            raise objError
        LastPosition = len(Fields) - 1
        for iIndex, tupDefinition in enumerate(Fields):
            strError = ''.join(['Wrong definition of ', cls.__name__,
                                '._Fields - {} at position {} '.format(
                                                        tupDefinition, iIndex)])
            if (not isinstance(tupDefinition, tuple)) or len(tupDefinition) !=2:
                objError = UT_TypeError(tupDefinition, tuple, SkipFrames = 2)
                strError = '{} {} of size 2'.format(strError, objError.args[0])
                objError.args = (strError, )
                raise objError
            #check field declaration
            FieldName = tupDefinition[0]
            if not isinstance(FieldName, str):
                objError = UT_TypeError(FieldName, str, SkipFrames = 2)
                strError = '{} {}'.format(strError, objError.args[0])
                objError.args = (strError, )
                raise objError
            ElementType = tupDefinition[1]
            if not IsC_Scalar(ElementType):
                try:
                    bSubClass = issubclass(ElementType, (SerArray, SerStruct))
                except TypeError: #built-in data type
                    objError = UT_TypeError(ElementType,
                                    (ctypes._SimpleCData, SerArray, SerStruct),
                                                                SkipFrames = 2)
                    strError = '{} {}'.format(strError, objError.args[0])
                    objError.args = (strError, )
                    raise objError from None
                if (bSubClass and (ElementType.getSize() is None) and 
                        iIndex != LastPosition): #dynamic not in final position
                    objError = UT_TypeError(1, int, SkipFrames = 2)
                    strError = '{} - dynamic {} not in final position'.format(
                                            strError, ElementType.__name__)
                    objError.args = (strError, )
                    raise objError
                elif not bSubClass:
                    objError = UT_TypeError(ElementType,
                                    (ctypes._SimpleCData, SerArray, SerStruct),
                                                                SkipFrames = 2)
                    strError = '{} {}'.format(strError, objError.args[0])
                    objError.args = (strError, )
                    raise objError
    
    #public API
    
    @classmethod
    def getSize(cls) -> TIntNone:
        """
        Method to obtain the full declared size in bytes of the stored data.
        
        Signature:
            None -> int >= 0 OR None
        
        Returns:
            * int >= 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
            * None: indication that the instance is not a fixed size object
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.0
        """
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        Fields = type.__getattribute__(cls, '_Fields')
        if not len(Fields):
            Size = 0
        else:
            LastType = Fields[-1][1]
            if not IsC_Scalar(LastType):
                if LastType.getSize() is None:
                    Size = None
            else:
                Size = 0
                for _, ElementType in Fields:
                    if IsC_Scalar(ElementType):
                        Size += ctypes.sizeof(ElementType)
                    else:
                        Size += ElementType.getSize()
        return Size
    
    @classmethod
    def getMinSize(cls) -> int:
        """
        Method to obtain the minimal number of bytes required to represent the
        declared size in bytes of the stored data, excluding the (optional)
        dynamic length array as the last element.
        
        Signature:
            None -> int >= 0
        
        Returns:
            int >= 0: size in bytes required to store in byte representation
                of the fixed size part
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.0
        """
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        Fields = type.__getattribute__(cls, '_Fields')
        Size = 0
        if len(Fields):
            LastType = Fields[-1][1]
            if not IsC_Scalar(LastType):
                if LastType.getSize() is None:
                    CheckFields = Fields[:-1]
                else:
                    CheckFields = Fields
            else:
                CheckFields = Fields
            for _, ElementType in CheckFields:
                if IsC_Scalar(ElementType):
                    Size += ctypes.sizeof(ElementType)
                else:
                    Size += ElementType.getSize()
        return Size
    
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
    
    def packBytes(self, BigEndian: bool = False) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            /bool/ -> bytes
        
        Args:
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
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
        unpackBytes(Data, BigEndian = False):
            bytes /, bool/ -> 'SerArray
        unpackJSON(Data):
            str -> 'SerArray
    
    Methods:
        packBytes(BigEndian = False):
            /bool/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> list(type A)
    
    Version 1.0.0.0
    """
    
    #private class attributes - data structure definition
    
    _ElementType: ClassVar[TElement] = ctypes.c_int32
    
    _Length: ClassVar[int] = 0 #number of elements
    
    #special methods
    
    def __getattribute__(self, name: str) -> Any:
        """
        Special method to hook into the read access to the attributes. Prohibs
        access to any attribute with the name starting with, at least, one
        underscore, except for the '__name__', which is required for the proper
        functioning of the custom exceptions - and '__len__' required for the
        indexing access and len() Python function.
        
        Signature:
            str -> type A
        
        Raises:
            UT_AttributeError: attribute does not exists, OR its name starts
                with, at least, one underscore, except for two special cases
                __name__ and __class__
        
        Version 1.0.0.0
        """
        if name == '__len__':
            Result = len(object.__getattribute__(self, '_Data'))
        else:
            try:
                Result = super().__getattribute__(name)
            except UT_AttributeError:
                raise UT_AttributeError(self, name, SkipFrames = 1) from None
        return Result
    
    #TODO index access!
    
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
                of sub-class of SerArray or SerDynamicArray OR the data
                structure of the class is improperly defined
        
        Version 1.0.0.0
        """
        funChecker = object.__getattribute__(self, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        if not (Data is None):
            bCond1 = not isinstance(Data, (collections.abc.Sequence, SerArray))
            bCond2 = isinstance(Data, (str, bytes))
            if bCond1 or bCond2:
                raise UT_TypeError(Data, (collections.abc.Sequence, SerArray),
                                                                SkipFrames = 1)
        ElementType = object.__getattribute__(self, '_ElementType')
        Length = object.__getattribute__(self, '_Length')
        if IsC_Scalar(ElementType):
            lstContent = []
            for _ in range(Length):
                lstContent.append(ElementType().value)
            object.__setattr__(self, '_Data', lstContent)
        else:
            try:
                if issubclass(DataType, (SerArray, SerStruct)):
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
    def _parseBuffer(cls, Data: bytes, BigEndian: bool = False) -> TList:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes -> list(type A)
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    def _checkDefinition(cls) -> None:
        """
        Private class method to check the definition of the data structure of
        the class. Supposed to be called by all class methods, including the
        unpacking (constructors), and the initialization instance method.
        
        Signature:
            None -> None
        
        Raises:
            UT_TypeError: required class private attributes are missing OR
                OR they hold wrong type vales OR elements type declaration is
                incorrect
        
        Version 1.0.0.0
        """
        #check presence of the required private class attributes
        for strName in ('_ElementType', '_Length'):
            try:
                type.__getattribute__(cls, strName)
            except AttributeError:
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = 'Wrong definition of {} - {} is missing'.format(
                                                        cls.__name__, strName)
                objError.args = (strError, )
                raise objError from None
        #check element type declaration
        ElementType = type.__getattribute__(cls, '_ElementType')
        if not IsC_Scalar(ElementType):
            try:
                bSubClass = issubclass(ElementType, (SerArray, SerStruct))
            except TypeError: #built-in data type
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = ''.join(['Wrong definition of ', cls.__name__,
                                        '._ElementType - ', str(ElementType),
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                objError.args = (strError, )
                raise objError from None
            if bSubClass and (ElementType.getSize() is None): #dynamic length
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = 'Wrong definition of {}.{} is dynamic {}'.format(
                            cls.__name__, '_ElementType', ElementType.__name__)
                objError.args = (strError, )
                raise objError
            elif not bSubClass:
                if not isinstance(ElementType, type): #instance
                    TypeValue = str(ElementType)
                else: #some class
                    TypeValue = ElementType.__name__
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = ''.join(['Wrong definition of ', cls.__name__,
                                    '._ElementType - ', TypeValue,
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                objError.args = (strError, )
                raise objError
        #check length definition
        Length = type.__getattribute__(cls, '_Length')
        strError = ''.join(['Wrong definition of ', cls.__name__,'._Length - ',
                                            str(Length), ' is not int >= 0'])
        if (not isinstance(Length, int)) or (Length < 0):
            objError = UT_TypeError(1, int, SkipFrames = 2)
            objError.args = (strError, )
            raise objError
    
    #public API
    
    @classmethod
    def getSize(cls) -> int:
        """
        Method to obtain the declared size in bytes of the stored data.
        
        Signature:
            None -> int > 0
        
        Returns:
            int >= 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.0
        """
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        ElementType = type.__getattribute__(cls, '_ElementType')
        if hasattr(ElementType, 'getSize'):
            ElementSize = ElementType.getSize()
        else:
            ElementSize = ctypes.sizeof(ElementType)
        Length = type.__getattribute__(cls, '_Length')
        return Length * ElementSize
    
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
    
    def packBytes(self, BigEndian: bool = False) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            None -> bytes
        
        Args:
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
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
        unpackBytes(Data, BigEndian = False):
            bytes /, bool/ -> 'SerDynamicArray
        unpackJSON(Data):
            str -> 'SerDynamicArray
    
    Methods:
        packBytes(BigEndian = False):
            /bool/ -> bytes
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
                of sub-class of SerArray or SerDynamicArray OR the class data
                structure is defined improperly
        
        Version 1.0.0.0
        """
        funChecker = object.__getattribute__(self, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        ElementType = object.__getattribute__(self, '_ElementType')
        if not (Data is None):
            bCond1 = not isinstance(Data, (collections.abc.Sequence, SerArray))
            bCond2 = isinstance(Data, (str, bytes))
            if bCond1 or bCond2:
                raise UT_TypeError(Data, (collections.abc.Sequence, SerArray),
                                                                SkipFrames = 1)
        if not IsC_Scalar(ElementType):
            try:
                if issubclass(DataType, (SerArray, SerStruct)):
                    pass
                else:
                    #raise exception here!
                    pass
            except TypeError: #not a type
                #raise exception here!
                pass
        object.__setattr__(self, '_Data', [])
    
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
    def _parseBuffer(cls, Data: bytes, BigEndian = False) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            /bool/ -> None
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool; flag if to use big endian bytes order,
                defaults to False (little endian)
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        pass
    
    @classmethod
    def _checkDefinition(cls) -> None:
        """
        Private class method to check the definition of the data structure of
        the class. Supposed to be called by all class methods, including the
        unpacking (constructors), and the initialization instance method.
        
        Signature:
            None -> None
        
        Raises:
            UT_TypeError: required class private attributes are missing OR
                OR they hold wrong type vales OR elements type declaration is
                incorrect
        
        Version 1.0.0.0
        """
        #check presence of the required private class attributes
        for strName in ('_ElementType', ):
            try:
                type.__getattribute__(cls, strName)
            except AttributeError:
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = 'Wrong definition of {} - {} is missing'.format(
                                                        cls.__name__, strName)
                objError.args = (strError, )
                raise objError from None
        #check element type declaration
        ElementType = type.__getattribute__(cls, '_ElementType')
        if not IsC_Scalar(ElementType):
            try:
                bSubClass = issubclass(ElementType, (SerArray, SerStruct))
            except TypeError: #built-in data type
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = ''.join(['Wrong definition of ', cls.__name__,
                                        '._ElementType - ', str(ElementType),
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                objError.args = (strError, )
                raise objError from None
            if bSubClass and (ElementType.getSize() is None): #dynamic length
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = 'Wrong definition of {}.{} is dynamic {}'.format(
                            cls.__name__, '_ElementType', ElementType.__name__)
                objError.args = (strError, )
                raise objError
            elif not bSubClass:
                if not isinstance(ElementType, type): #instance
                    TypeValue = str(ElementType)
                else: #some class
                    TypeValue = ElementType.__name__
                objError = UT_TypeError(1, int, SkipFrames = 2)
                strError = ''.join(['Wrong definition of ', cls.__name__,
                                    '._ElementType - ', TypeValue,
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                objError.args = (strError, )
                raise objError
    
    #public API
    
    @classmethod
    def getSize(cls) -> None:
        """
        Method to obtain the declared size in bytes of the stored data.
        
        Signature:
            None -> None
        
        Returns:
            None: indication that the instance is not a fixed size object
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.0
        """
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        return None
    
    @classmethod
    def getElementSize(cls) -> int:
        """
        Class method to get the byte size of a single element, which can be
        stored in a dynamic array.
        
        Signature:
            None -> int >= 0
        
        Returns:
            int >= 0: size in bytes required to present a single element
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.0
        """
        funChecker = type.__getattribute__(cls, '_checkDefinition')
        funChecker() #UT_TypeError may be raised
        ElementType = type.__getattribute__(cls, '_ElementType')
        if IsC_Scalar(ElementType):
            Size = ctypes.sizeof(ElementType)
        else:
            Size = ElementType.getSize()
        return Size
