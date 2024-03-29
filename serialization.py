#usr/bin/python3fun
"""
Module com_lib.serialization

Functions:
    IsC_Scalar(Type):
        type A -> bool
    Scalar2BytesNE(Value, CType):
        type A, class ctypes._SimpleCData -> bytes
    Scalar2BytesBE(Value, CType):
        type A, class ctypes._SimpleCData -> bytes
    Scalar2BytesLE(Value, CType):
        type A, class ctypes._SimpleCData -> bytes
    Scalar2Bytes(Value, CType, BigEndian = None):
        type A, class ctypes._SimpleCData/, bool OR None/ -> bytes
    Bytes2ScalarNE(Data, CType):
        bytes, class ctypes._SimpleCData -> type A
    Bytes2ScalarBE(Data, CType):
        bytes, class ctypes._SimpleCData -> type A
    Bytes2ScalarLE(Data, CType):
        bytes, class ctypes._SimpleCData -> type A
    Bytes2Scalar(Data, CType, BigEndian = None):
        bytes, class ctypes._SimpleCData/, bool OR None/ -> type A

Classes:
    Serializable
    SerNULL
    SerStruct
    SerArray
    SerDynamicArray
    SerNumber
"""

__version__ = "1.2.0.0"
__date__ = "11-05-2023"
__status__ = "Production"

#imports

#+ standard libaries

import os
import sys
import abc
import json
import ctypes

import collections.abc

from typing import Iterator, Optional, Union, List, Dict, Any, NoReturn
from typing import ClassVar, Tuple, Sequence, Mapping, Type

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

TSimpleC = Type[ctypes._SimpleCData]

#helper functions

def IsC_Scalar(Type: Any) -> bool:
    """
    Helper function to check if the passed data type is a scalar C type.
    
    Signature:
        type A -> bool
    
    Args:
        Type: type A; the data type to be checked
    
    Returns:
        bool: True if check passes, False otherwise
    
    Version 1.0.0.1
    """
    try:
        Result = issubclass(Type, ctypes._SimpleCData)
    except TypeError:
        Result = False
    return Result

def Scalar2BytesNE(Value: Any, CType: TSimpleC) -> bytes:
    """
    Helper function to get a byte representation of a native Python scalar value
    compatible with a specific C data type using the native platform endianness.
    
    Signature:
        type A, class ctypes._SimpleCData -> bytes
    
    Args:
        Value: type A; native Python scalar value to be converted into bytes
            representation
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
    
    Returns:
        bytes: bytes representation of the passed value as if stored in a
            variable of the respective C data type
    
    Version 1.0.0.0
    """
    CValue = CType(Value)
    Length = ctypes.sizeof(CType)
    Pointer = ctypes.addressof(CValue)
    Result = ctypes.string_at(Pointer, Length)
    del CValue
    return Result

def Scalar2BytesLE(Value: Any, CType: TSimpleC) -> bytes:
    """
    Helper function to get a byte representation of a native Python scalar value
    compatible with a specific C data type using the forced little endianness.
    
    Signature:
        type A, class ctypes._SimpleCData -> bytes
    
    Args:
        Value: type A; native Python scalar value to be converted into bytes
            representation
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
    
    Returns:
        bytes: bytes representation of the passed value as if stored in a
            variable of the respective C data type
    
    Version 1.1.0.0
    """
    if hasattr(CType, '__ctype_le__'):
        CastType = CType.__ctype_le__
    else:
        CastType = CType
    CValue = CastType(Value)
    Length = ctypes.sizeof(CType)
    Pointer = ctypes.addressof(CValue)
    Result = ctypes.string_at(Pointer, Length)
    del CValue
    return Result

def Scalar2BytesBE(Value: Any, CType: TSimpleC) -> bytes:
    """
    Helper function to get a byte representation of a native Python scalar value
    compatible with a specific C data type using the forced big endianness.
    
    Signature:
        type A, class ctypes._SimpleCData -> bytes
    
    Args:
        Value: type A; native Python scalar value to be converted into bytes
            representation
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
    
    Returns:
        bytes: bytes representation of the passed value as if stored in a
            variable of the respective C data type
    
    Version 1.1.0.0
    """
    if hasattr(CType, '__ctype_be__'):
        CastType = CType.__ctype_be__
    else:
        CastType = CType
    CValue = CastType(Value)
    Length = ctypes.sizeof(CType)
    Pointer = ctypes.addressof(CValue)
    Result = ctypes.string_at(Pointer, Length)
    del CValue
    return Result

def Scalar2Bytes(Value: Any, CType: TSimpleC,
                            BigEndian: Optional[bool] = None) -> bytes:
    """
    Helper function to get a byte representation of a native Python scalar value
    compatible with a specific C data type using the specified endianness. The
    optional argument BigEndian is interpreted either as None or as boolean
    value regardless of its actual data type.
    
    Signature:
        type A, class ctypes._SimpleCData/, bool OR None/ -> bytes
    
    Args:
        Value: type A; native Python scalar value to be converted into bytes
            representation
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
        BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
    
    Returns:
        bytes: bytes representation of the passed value as if stored in a
            variable of the respective C data type
    
    Version 1.0.0.0
    """
    if BigEndian is None:
        Result = Scalar2BytesNE(Value, CType)
    elif BigEndian:
        Result = Scalar2BytesBE(Value, CType)
    else:
        Result = Scalar2BytesLE(Value, CType)
    return Result

def Bytes2ScalarNE(Data: bytes, CType: TSimpleC) -> Any:
    """
    Helper function to get a native Python scalar value from a byte string,
    assuming that the passed data is byte representation of the specific C
    primitive data type. Uses the platform native endianness.
    
    Signature:
        bytes, class ctypes._SimpleCData -> type A
    
    Args:
        Data: bytes; byte representation of a value
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
    
    Returns:
        type A: native Python scalar type, e.g. int or float
    
    Version 1.0.0.0
    """
    CValue = CType.from_buffer_copy(Data)
    Result = CValue.value
    del CValue
    return Result

def Bytes2ScalarLE(Data: bytes, CType: TSimpleC) -> Any:
    """
    Helper function to get a native Python scalar value from a byte string,
    assuming that the passed data is byte representation of the specific C
    primitive data type. Uses the forced little endianness.
    
    Signature:
        bytes, class ctypes._SimpleCData -> type A
    
    Args:
        Data: bytes; byte representation of a value
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
    
    Returns:
        type A: native Python scalar type, e.g. int or float
    
    Version 1.1.0.0
    """
    if hasattr(CType, '__ctype_le__'):
        CastType = CType.__ctype_le__
    else:
        CastType = CType
    CValue = CastType.from_buffer_copy(Data)
    Result = CValue.value
    del CValue
    return Result

def Bytes2ScalarBE(Data: bytes, CType: TSimpleC) -> Any:
    """
    Helper function to get a native Python scalar value from a byte string,
    assuming that the passed data is byte representation of the specific C
    primitive data type. Uses the forced big endianness.
    
    Signature:
        bytes, class ctypes._SimpleCData -> type A
    
    Args:
        Data: bytes; byte representation of a value
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
    
    Returns:
        type A: native Python scalar type, e.g. int or float
    
    Version 1.1.0.0
    """
    if hasattr(CType, '__ctype_be__'):
        CastType = CType.__ctype_be__
    else:
        CastType = CType
    CValue = CastType.from_buffer_copy(Data)
    Result = CValue.value
    del CValue
    return Result

def Bytes2Scalar(Data: bytes, CType: TSimpleC,
                            BigEndian: Optional[bool] = None) -> Any:
    """
    Helper function to get a native Python scalar value from a byte string,
    assuming that the passed data is byte representation of the specific C
    primitive data typeusing the specified endianness. The optional argument
    BigEndian is interpreted either as None or as boolean value regardless of
    its actual data type.
    
    Signature:
        bytes, class ctypes._SimpleCData/, bool OR None/ -> type A
    
    Args:
        Data: bytes; byte representation of a value
        CType: class ctypes._SimpleCData; class, Python implementation of C
            primitive data type
        BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
    
    Returns:
        type A: native Python scalar type, e.g. int or float
    
    Version 1.0.0.0
    """
    if BigEndian is None:
        Result = Bytes2ScalarNE(Data, CType)
    elif BigEndian:
        Result = Bytes2ScalarBE(Data, CType)
    else:
        Result = Bytes2ScalarLE(Data, CType)
    return Result

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
        unpackBytes(Data, BigEndian = None):
            bytes /, bool OR None / -> 'Serializable
        unpackJSON(Data):
            str -> 'Serializable
    
    Methods:
        packBytes(BigEndian = None):
            /bool OR None/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> type A
    
    Version 1.0.0.1
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
    def _parseBuffer(cls, Data: bytes, BigEndian: Optional[bool] =None) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        Prototype.
        
        Signature:
            bytes /, bool OR None/ -> None
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
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
        underscore, except for the '__class__' and '__name__', which are
        required for the proper functioning of the custom exceptions.
        
        Signature:
            str -> type A
        
        Raises:
            UT_AttributeError: attribute does not exists, OR its name starts
                with, at least, one underscore, except for two special cases
                __name__ and __class__
        
        Version 1.0.0.1
        """
        if name in ('__class__', ):
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
    def unpackBytes(cls, Data: bytes, BigEndian: Optional[bool] = None):
        """
        Class method responsible for creation of a new instance using the data
        extracted from the passed bytes packed representation. The optional
        argument BigEndian is interpreted either as None or as boolean value
        regardless of its actual data type.
        
        Signature:
            bytes /, bool OR None/ -> 'Serializable
        
        Args:
            Data: bytes; bytes representation of the data
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Returns:
            'Serializable: an instance of a sub-class of Serializable, same as
                the current instance class
        
        Raises:
            UT_TypeError: passed argument is not a byte string OR the class
                data structure is wrongly defined
            UT_ValueError: the size of the byte string does not match the size
                of the declared class data structure
        
        Version 1.0.0.1
        """
        if not isinstance(Data, bytes):
            raise UT_TypeError(Data, bytes, SkipFrames = 1)
        TypeChecker = type.__getattribute__(cls, '_checkDefinition')
        TypeChecker() #UT_TypeError may be raised
        Parser = type.__getattribute__(cls, '_parseBuffer')
        NativeData = Parser(Data, BigEndian = BigEndian)
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
        
        Version 1.0.0.1
        """
        if not isinstance(Data, str):
            raise UT_TypeError(Data, str, SkipFrames = 1)
        try:
            NativeData = json.loads(Data)
        except ValueError as err:
            raise UT_ValueError(Data, 'not a valid JSON string',
                                                    SkipFrames = 1) from None
        TypeChecker = type.__getattribute__(cls, '_checkDefinition')
        TypeChecker() #UT_TypeError may be raised
        ContentChecker = type.__getattribute__(cls, '_checkObjectContent')
        ContentChecker(NativeData)
        #supposed to raise UT_TypeError or UT_ValueError
        #+ if type / structure does not meet class definition
        return cls(NativeData)
    
    @abc.abstractmethod
    def packBytes(self, BigEndian: Optional[bool] = None) -> bytes:
        """
        Prototype method for serialization of the stored data into bytes. The
        optional argument BigEndian is interpreted either as None or as boolean
        value regardless of its actual data type.
        
        Signature:
            /bool OR None/ -> bytes
        
        Args:
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
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
        
        Version 1.0.0.1
        """
        NativeData = self.getNative()
        JSON_Data = json.dumps(NativeData)
        return JSON_Data
    
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

TElement = Union[TSimpleC, Serializable]

#+ main classes
class SerNULL(Serializable):
    """
    Implements auto-serilizable and de-serializable object representing NULL /
    None empty response or data load. Can be instantiated without an argument or
    with a single optional argument, which is simply ignored.
    
    Class methods:
        getSize():
            None -> int = 0
        unpackBytes(Data, BigEndian = None):
            bytes /, bool OR None/ -> SerNULL
        unpackJSON(Data):
            str -> SerNULL
    
    Methods:
        packBytes(BigEndian = None):
            /bool OR None/ -> bytes
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
    def _parseBuffer(cls, Data: bytes, BigEndian: Optional[bool] =None) -> None:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition. Only
        an empty bytestring is allowed.
        
        Signature:
            bytes /, bool OR None/ -> None
        
        Args:
            Data: bytes; only an empty bytestring is acceptable
            BigEndian: (optional) bool OR None; ignored
        
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
    
    def packBytes(self, BigEndian: Optional[bool] = None) -> bytes:
        """
        Method for serialization of the stored data into bytes.
        
        Signature:
            /bool OR None/ -> bytes
        
        Args:
            BigEndian: (optional) bool OR None; ignored
        
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
        unpackBytes(Data, BigEndian = None):
            bytes /, bool OR None/ -> 'SerStruct
        unpackJSON(Data):
            str -> 'SerStruct
        getMinSize():
            None -> int >= 0
    
    Methods:
        packBytes(BigEndian = None):
            /bool OR None/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> dict(str -> type A)
        getCurrentSize():
            None -> int >= 0
    
    Version 1.0.1.1
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
        
        Version 1.0.0.1
        """
        Fields = object.__getattribute__(self, '_Fields')
        FiledsTypes = {Key : Type_ for Key, Type_ in Fields}
        if (name in FiledsTypes) and (IsC_Scalar(FiledsTypes[name])):
            try:
                NewValue = FiledsTypes[name](value)
            except (TypeError, ValueError):
                Error = UT_TypeError(value, FiledsTypes[name], SkipFrames = 1)
                Error.appendMessage('type compatible')
                raise Error from None
            object.__setattr__(self, name, NewValue.value)
            del NewValue
        elif not (name in FiledsTypes):
            raise UT_AttributeError(self, name, SkipFrames = 1)
        else:
            Error = UT_TypeError(FiledsTypes[name], ctypes._SimpleCData,
                                                                 SkipFrames = 1)
            Error.appendMessage('- immutable field')
            raise Error
        del FiledsTypes
    
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
            UT_ValueError: not matching data type in one of the key:value pairs,
                concerning the declared data type for this field
        
        Version 1.0.0.1
        """
        TypeChecker = object.__getattribute__(self, '_checkDefinition')
        TypeChecker() #UT_TypeError may be raised
        if not (Data is None):
            if not isinstance(Data, (collections.abc.Mapping, SerStruct)):
                raise UT_TypeError(Data, (collections.abc.Mapping, SerStruct),
                                                                SkipFrames = 1)
            Source = Data
        else:
            Source = dict()
        Fields = object.__getattribute__(self, '_Fields')
        FieldsContent = dict()
        for Field, DataType in Fields:
            IsFound = False
            if (isinstance(Source, collections.abc.Mapping)
                                                        and (Field in Source)):
                PassedValue = Source[Field]
                IsFound = True
            elif isinstance(Source, SerStruct) and hasattr(Source, Field):
                PassedValue = getattr(Source, Field)
                IsFound = True
            if IsFound:
                try:
                    FieldValue = DataType(PassedValue)
                except (ValueError, TypeError):
                    ErrorMessage='being compatible with {} for field {}'.format(
                                                    DataType.__name__, Field)

                    raise UT_ValueError(PassedValue, ErrorMessage,
                                                    SkipFrames = 1) from None
            else:
                FieldValue = DataType()
            if IsC_Scalar(DataType):
                FieldsContent[Field] = FieldValue.value
                del FieldValue
            else:
                FieldsContent[Field] = FieldValue
            for Field, Value in FieldsContent.items():
                object.__setattr__(self, Field, Value)
    
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
        
        Version 1.0.0.1
        """
        if not isinstance(Data, dict):
            raise UT_TypeError(Data, dict, SkipFrames = 2)
        Fields = type.__getattribute__(cls, '_Fields')
        DeclaredFields = []
        for Field, FieldType in Fields:
            DeclaredFields.append(Field)
            if not (Field in Data):
                raise UT_ValueError(Field, 'key being present in data',
                                                                SkipFrames= 2)
            Value = Data[Field]
            IsScalar = IsC_Scalar(FieldType)
            try:
                if IsScalar:
                    Temp = FieldType(Value)
                    del Temp
                else:
                    Checker = type.__getattribute__(FieldType,
                                                        '_checkObjectContent')
                    Checker(Value)
            except (TypeError, ValueError):
                raise UT_ValueError(Value,
                    f'compatible with {FieldType.__name__} type at key {Field}',
                        SkipFrames= 2) from None
        for Key in Data:
            if not (Key in DeclaredFields):
                raise UT_ValueError(Key, 'being declared field', SkipFrames= 2)
    
    @classmethod
    def _parseBuffer(cls, Data: bytes,
                                    BigEndian: Optional[bool] = None) -> TDict:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes /, bool OR None/ -> dict(str -> type A)
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.1
        """
        Size = cls.getSize()
        DataSize = len(Data)
        if Size is None:
            MinSize = cls.getMinSize()
            if DataSize < MinSize:
                raise UT_ValueError(DataSize, f'> {MinSize} - string length',
                                                                SkipFrames = 2)
        elif DataSize != Size:
            raise UT_ValueError(DataSize, f'= {Size} - string length',
                                                                SkipFrames = 2)
        Fields = type.__getattribute__(cls, '_Fields')
        NewValues = dict()
        ProcessedBytes = 0
        for Field, FieldType in Fields[:-1]:
            if IsC_Scalar(FieldType):
                ElementSize = ctypes.sizeof(FieldType)
                DataSlice = Data[ProcessedBytes : ProcessedBytes + ElementSize]
                NewValues[Field] = Bytes2Scalar(DataSlice, FieldType,
                                                        BigEndian = BigEndian)
            else:
                ElementSize = FieldType.getSize()
                DataSlice = Data[ProcessedBytes : ProcessedBytes + ElementSize]
                Temp = FieldType.unpackBytes(DataSlice, BigEndian= BigEndian)
                NewValues[Field] = Temp.getNative()
                del Temp
            ProcessedBytes += ElementSize
        DataSlice = Data[ProcessedBytes : ]
        LastField, LastType = Fields[-1]
        if IsC_Scalar(LastType):
            NewValues[LastField] = Bytes2Scalar(DataSlice, LastType,
                                                        BigEndian = BigEndian)
        else:
            try:
                Temp = LastType.unpackBytes(DataSlice, BigEndian= BigEndian)
                NewValues[LastField] = Temp.getNative()
                del Temp
            except UT_ValueError as err:
                BytesRemain = DataSize - ProcessedBytes
                Message = 'byte size for type {} of field {} - {}'.format(
                                LastType.__name__, LastField, err.getMessage())
                Error = UT_ValueError(BytesRemain, Message, SkipFrames = 1)
                raise Error from None
        return NewValues
    
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
        
        Version 1.0.0.1
        """
        for Name in ('_Fields', ):
            try:
                type.__getattribute__(cls, Name)
            except AttributeError:
                Error = UT_TypeError(1, int, SkipFrames = 2)
                ErrorMessage = 'Wrong definition of {} - {} is missing'.format(
                                                        cls.__name__, Name)
                Error.setMessage(ErrorMessage)
                raise Error from None
        #check _Field attribute 
        Fields = type.__getattribute__(cls, '_Fields')
        if not isinstance(Fields, tuple):
            Error = UT_TypeError(Fields, tuple, SkipFrames = 2)
            ErrorMessage = 'Wrong definition of {}._Fields - {}'.format(
                                            cls.__name__, Error.getMessage())
            Error.setMessage(ErrorMessage)
            raise Error
        LastPosition = len(Fields) - 1
        for Index, Definition in enumerate(Fields):
            BaseMessage = ''.join(['Wrong definition of ', cls.__name__,
                            f'._Fields - {Definition} at position {Index} '])
            if (not isinstance(Definition, tuple)) or len(Definition) !=2:
                Error = UT_TypeError(Definition, tuple, SkipFrames = 2)
                Message = f'{BaseMessage} {Error.getMessage()} of size 2'
                Error.setMessage(Message)
                raise Error
            #check field declaration
            FieldName = Definition[0]
            if not isinstance(FieldName, str):
                Error = UT_TypeError(FieldName, str, SkipFrames = 2)
                Message = f'{BaseMessage} {Error.getMessage()}'
                Error.setMessage(Message)
                raise Error
            ElementType = Definition[1]
            if not IsC_Scalar(ElementType):
                try:
                    IsSubClass = issubclass(ElementType, (SerArray, SerStruct))
                except TypeError: #built-in data type
                    Error = UT_TypeError(ElementType,
                                    (ctypes._SimpleCData, SerArray, SerStruct),
                                                                SkipFrames = 2)
                    Message = f'{BaseMessage} {Error.getMessage()}'
                    Error.setMessage(Message)
                    raise Error from None
                if (IsSubClass and (ElementType.getSize() is None) and 
                                                        Index != LastPosition):
                    #dynamic not in final position
                    Error = UT_TypeError(1, int, SkipFrames = 2)
                    Message = '{} - dynamic {} not in final position'.format(
                                            BaseMessage, ElementType.__name__)
                    Error.setMessage(Message)
                    raise Error
                elif not IsSubClass:
                    Error = UT_TypeError(ElementType,
                                    (ctypes._SimpleCData, SerArray, SerStruct),
                                                                SkipFrames = 2)
                    Message = f'{BaseMessage} {Error.getMessage()}'
                    Error.setMessage(Message)
                    raise Error
    
    #public API
    
    @classmethod
    def getSize(cls) -> TIntNone:
        """
        Method to obtain the full declared size in bytes of the stored data.
        
        Signature:
            None -> int > 0 OR None
        
        Returns:
            * int > 0: size in bytes required to store in byte representation
                the entire declared data structure - for the fixed size objects
            * None: indication that the instance is not a fixed size object
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.1.0.1
        """
        Checker = type.__getattribute__(cls, '_checkDefinition')
        Checker() #UT_TypeError may be raised
        Fields = type.__getattribute__(cls, '_Fields')
        if not len(Fields):
            Size = 0
        else:
            LastType = Fields[-1][1]
            if not IsC_Scalar(LastType) and (LastType.getSize() is None):
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
        
        Version 1.0.0.1
        """
        Checker = type.__getattribute__(cls, '_checkDefinition')
        Checker() #UT_TypeError may be raised
        Fields = type.__getattribute__(cls, '_Fields')
        Size = 0
        if len(Fields):
            LastType = Fields[-1][1]
            if not IsC_Scalar(LastType):
                if LastType.getSize() is None:
                    CheckFields = Fields[:-1]
                    if hasattr(LastType, 'getMinSize'):
                        Size += LastType.getMinSize()
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
    
    def getCurrentSize(self) -> int:
        """
        Method to obtain the total size of the currently stored data in bytes.
        
        Signature:
            None -> int >= 0
        
        Version 1.0.0.0
        """
        Fields = object.__getattribute__(self, '_Fields')
        Size = 0
        if len(Fields):
            LastName, LastType = Fields[-1]
            for _, ElementType in Fields[:-1]:
                if IsC_Scalar(ElementType):
                    Size += ctypes.sizeof(ElementType)
                else:
                    Size += ElementType.getSize()
            if IsC_Scalar(LastType):
                Size += ctypes.sizeof(LastType)
            else:
                LastSize = LastType.getSize()
                if not (LastSize is None):
                    Size += LastSize
                elif hasattr(LastType, 'getCurrentSize'):
                    Size += getattr(self, LastName).getCurrentSize()
                else:
                    Size += (len(getattr(self, LastName)) *
                                                    LastType.getElementSize())
        return Size
    
    def getNative(self) -> TDict:
        """
        Method for convertion of the stored data into native Python data type.
        
        Signature:
            None -> dict(str -> type A)
        
        Returns:
            dict(str -> type A): native Python type representation of the stored
                data
        
        Version 1.0.0.1
        """
        Result = dict()
        Data = object.__getattribute__(self, '__dict__')
        for strName, gItem in Data.items():
            if hasattr(gItem, 'getNative'):
                Result[strName] = gItem.getNative()
            else:
                Result[strName] = gItem
        return Result
    
    def packBytes(self, BigEndian: Optional[bool] = None) -> bytes:
        """
        Method for serialization of the stored data into bytes. The optional
        argument BigEndian is interpreted either as None or as boolean value
        regardless of its actual data type.
        
        Signature:
            /bool OR None/ -> bytes
        
        Args:
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Returns:
            bytes: bytestring representing the entire stored data
        
        Version 1.1.0.0
        """
        Data = object.__getattribute__(self, '__dict__')
        Fields = object.__getattribute__(self, '_Fields')
        RawValues = list()
        for Field, FieldType in Fields:
            if IsC_Scalar(FieldType):
                RawValues.append(Scalar2Bytes(Data[Field], FieldType,
                                                        BigEndian = BigEndian))
            else:
                RawValues.append(Data[Field].packBytes(BigEndian = BigEndian))
        Result = b''.join(RawValues)
        return Result

class SerArray(Serializable):
    """
    Implements auto-serilizable and de-serializable object representing C-array
    like structured data storage. Can be instantiate without an argument or
    with a single optional argument of a sequence type or another array.
    
    Class methods:
        getSize():
            None -> int >= 0 OR None
        unpackBytes(Data, BigEndian = None):
            bytes /, bool OR None/ -> 'SerArray
        unpackJSON(Data):
            str -> 'SerArray
    
    Methods:
        packBytes(BigEndian = None):
            /bool OR None/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> list(type A)
    
    Version 1.0.0.1
    """
    
    #private class attributes - data structure definition
    
    _ElementType: ClassVar[TElement] = ctypes.c_int32
    
    _Length: ClassVar[int] = 0 #number of elements, must be > 0
    
    #special methods
    
    def __len__(self) -> int:
        """
        Magic method to implement the support for the built-in len() function,
        in order to get the length of the array.
        
        Signature:
            None -> int >= 0
        
        Returns:
            int >= 0: the current length of the array
        
        Version 1.0.0.0
        """
        return len(object.__getattribute__(self, '_Data'))
    
    def __getitem__(self, Index: int) -> Any:
        """
        Magic method implementing the read access to an element of the array by
        its index. For the C primitive declared data type of the elements the
        returned value is a native Python scalar type (int, float, etc.),
        otherwise the stored object (reference to) is returned.
        
        Signature:
            int -> type A
        
        Args:
            iIndex: int; the index of the element to be accesed
        
        Raises:
            UT_IndexError: the value of the index is outside the range OR it is
                not an integer number
        
        Version 1.0.0.1
        """
        if not isinstance(Index, int):
            raise UT_IndexError(self.__name__, Index, SkipFrames = 1)
        Data = object.__getattribute__(self, '_Data')
        Length = len(Data)
        if (Index > (Length - 1)) or (Index < (- Length)):
            raise UT_IndexError(self.__name__, Index, SkipFrames = 1)
        return Data[Index]
    
    def __setitem__(self, Index: int, Value: Any) -> None:
        """
        Magic method implementing the write access to an element of the array by
        its index. Assignment is allowed only if the declared type of the
        elements is C primitive and the passed value is compatible with the
        declared type.
        
        Signature:
            int, type A -> None
        
        Args:
            Index: int; the index of the element to be accesed
            Value: type A; value to be assigned to that element
        
        Raises:
            UT_TypeError: the passed value's type is not compatible with the
                declared type of the elements OR the declared data type is not C
                primitive
            UT_IndexError: the value of the index is outside the range OR it is
                not an integer number
        
        Version 1.0.0.1
        """
        if not isinstance(Index, int):
            raise UT_IndexError(self.__name__, Index, SkipFrames = 1)
        Data = object.__getattribute__(self, '_Data')
        Length = len(Data)
        if (Index > (Length - 1)) or (Index < (- Length)):
            raise UT_IndexError(self.__name__, Index, SkipFrames = 1)
        ElementType = object.__getattribute__(self, '_ElementType')
        if not IsC_Scalar(ElementType):
            Error = UT_TypeError(ElementType, ctypes._SimpleCData,
                                                                SkipFrames = 1)
            Error.appendMessage('- immutable elements')
            raise Error
        try:
            NewValue = ElementType(Value)
        except (TypeError, ValueError):
            Error = UT_TypeError(Value, ElementType, SkipFrames = 1)
            Error.appendMessage('type compatible')
            raise Error from None
        Data[Index] = NewValue.value
        del NewValue
    
    def __iter__(self) -> Iterator[Any]:
        """
        Magic method to implement iteration over the content of the array as in
        the construction 'for ... in ..'.
        
        Signature:
            None -> iter(type A)
        
        Version 1.0.0.0
        """
        return iter(object.__getattribute__(self, '_Data'))
    
    def __init__(self, Data: Optional[Union[TSeq, Serializable]]=None) -> None:
        """
        Initialization method - copies the data from the passed sequence per
        element. If the length of the passed sequence equals to or exceeds the
        declared length of the array N, only the those N first elements are
        copied, and the rest is ignored. Otherwise, all elements of the passed
        sequence / array are copied into the first elements of the array being
        created, and the remaining tailing elements are filled with the default
        values for the declared data type of the elements.
        
        Signature:
            /seq(str -> type A) OR 'SerArray/ -> None
        
        Args:
            Data: (optional) seq(str -> type A) OR 'SerArray; sequence or an
                instance of SerArray (sub-) class
        
        Raises:
            UT_TypeError: passed argument is not a sequence type or an instance
                of sub-class of SerArray or SerDynamicArray OR the data
                structure of the class is improperly defined
            UT_ValueError: not matching data type in one of the elements,
                concerning the declared data type for the array elements
        
        Version 1.0.0.1
        """
        Checker = object.__getattribute__(self, '_checkDefinition')
        Checker() #UT_TypeError may be raised
        if not (Data is None):
            Cond1 = not isinstance(Data, (collections.abc.Sequence, SerArray))
            Cond2 = isinstance(Data, (str, bytes))
            if Cond1 or Cond2:
                raise UT_TypeError(Data, (collections.abc.Sequence, SerArray),
                                                                SkipFrames = 1)
            InputLength = len(Data)
        else:
            InputLength = 0
        ElementType = object.__getattribute__(self, '_ElementType')
        Length = object.__getattribute__(self, '_Length')
        Elements = []
        for Index in range(Length):
            if Index < InputLength:
                try:
                    NewElement = ElementType(Data[Index])
                except (ValueError, TypeError):
                    Message = 'being compatible with {} at index {}'.format(
                                                    ElementType.__name__, Index)
                    
                    raise UT_ValueError(Data[Index], Message,
                                                    SkipFrames = 1) from None
            else:
                NewElement = ElementType()
            if IsC_Scalar(ElementType):
                Elements.append(NewElement.value)
                del NewElement
            else:
                Elements.append(NewElement)
        object.__setattr__(self, '_Data', Elements)
    
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
        
        Version 1.0.0.1
        """
        if not isinstance(Data, list):
            raise UT_TypeError(Data, list, SkipFrames = 2)
        ElementsType = type.__getattribute__(cls, '_ElementType')
        IsScalar = IsC_Scalar(ElementsType)
        Length = type.__getattribute__(cls, '_Length')
        DataLength = len(Data)
        if Length != DataLength:
            raise UT_ValueError(DataLength,
                        '= {} - array length'.format(Length), SkipFrames = 2)
        for Index, Element in enumerate(Data):
            try:
                if IsScalar:
                    Temp = ElementsType(Element)
                    del Temp
                else:
                    Checker = type.__getattribute__(ElementsType,
                                                        '_checkObjectContent')
                    Checker(Element)
            except (TypeError, ValueError):
                raise UT_ValueError(Element,
                        'compatible with {} type at index {}'.format(
                        ElementsType.__name__, Index), SkipFrames = 2) from None
    
    @classmethod
    def _parseBuffer(cls, Data: bytes,
                                    BigEndian: Optional[bool] = None) -> TList:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes/, bool OR None/ -> list(type A)
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Returns:
            list(type A): a native Python list containing only native Python
                data type elements, compatible with the declared array elements
                type
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        Size = cls.getSize()
        Length = type.__getattribute__(cls, '_Length')
        DataSize = len(Data)
        if DataSize != Size:
            raise UT_ValueError(DataSize, '= {} - string length'.format(Size),
                                                                SkipFrames = 2)
        ElementsType = type.__getattribute__(cls, '_ElementType')
        if IsC_Scalar(ElementsType):
            ElementSize = ctypes.sizeof(ElementsType)
            Result = [Bytes2Scalar(
                        Data[Index * ElementSize : (Index + 1) * ElementSize],
                                            ElementsType, BigEndian = BigEndian)
                                                    for Index in range(Length)]
        else:
            ElementSize = ElementsType.getSize()
            Result = []
            for Index in range(Length):
                DataSplice =  Data[Index * ElementSize : (Index+1)*ElementSize]
                NewObject = ElementsType.unpackBytes(DataSplice,
                                                        BigEndian = BigEndian)
                Result.append(NewObject.getNative())
                del NewObject
        return Result
    
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
        
        Version 1.0.0.1
        """
        #check presence of the required private class attributes
        for Name in ('_ElementType', '_Length'):
            try:
                type.__getattribute__(cls, Name)
            except AttributeError:
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = 'Wrong definition of {} - {} is missing'.format(
                                                            cls.__name__, Name)
                Error.setMessage(Message)
                raise Error from None
        #check element type declaration
        ElementType = type.__getattribute__(cls, '_ElementType')
        if not IsC_Scalar(ElementType):
            try:
                IsSubClass = issubclass(ElementType, (SerArray, SerStruct))
            except TypeError: #built-in data type
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = ''.join(['Wrong definition of ', cls.__name__,
                                        '._ElementType - ', str(ElementType),
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                Error.setMessage(Message)
                raise Error from None
            if IsSubClass and (ElementType.getSize() is None): #dynamic length
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = 'Wrong definition of {}.{} is dynamic {}'.format(
                            cls.__name__, '_ElementType', ElementType.__name__)
                Error.setMessage(Message)
                raise Error
            elif not IsSubClass:
                if not isinstance(ElementType, type): #instance
                    TypeValue = str(ElementType)
                else: #some class
                    TypeValue = ElementType.__name__
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = ''.join(['Wrong definition of ', cls.__name__,
                                    '._ElementType - ', TypeValue,
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                Error.setMessage(Message)
                raise Error
        #check length definition
        Length = type.__getattribute__(cls, '_Length')
        Message = ''.join(['Wrong definition of ', cls.__name__,'._Length - ',
                                            str(Length), ' is not int > 0'])
        if (not isinstance(Length, int)) or (Length <= 0):
            Error = UT_TypeError(1, int, SkipFrames = 2)
            Error.setMessage(Message)
            raise Error
    
    #public API
    
    @classmethod
    def getSize(cls) -> int:
        """
        Method to obtain the declared size in bytes of the stored data.
        
        Signature:
            None -> int > 0
        
        Returns:
            int > 0: size in bytes required to store in byte representation
                the entire array
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.1
        """
        Checker = type.__getattribute__(cls, '_checkDefinition')
        Checker() #UT_TypeError may be raised
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
        
        Version 1.0.0.1
        """
        ElementType = object.__getattribute__(self, '_ElementType')
        IsScalar = IsC_Scalar(ElementType)
        Data = object.__getattribute__(self, '_Data')
        if IsScalar:
            Result = list(Data)
        else:
            Result = [Item.getNative() for Item in Data]
        return Result
    
    def packBytes(self, BigEndian: Optional[bool] = None) -> bytes:
        """
        Method for serialization of the stored data into bytes. The optional
        argument BigEndian is interpreted either as None or as boolean value
        regardless of its actual data type.
        
        Signature:
            /bool OR None/ -> bytes
        
        Args:
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Returns:
            bytes: bytestring representing the entire stored data
        
        Version 1.0.0.0
        """
        ElementsType = object.__getattribute__(self, '_ElementType')
        Data = object.__getattribute__(self, '_Data')
        if len(Data):
            if IsC_Scalar(ElementsType):
                Result = b''.join(Scalar2Bytes(Element, ElementsType,
                                    BigEndian = BigEndian) for Element in Data)
            else:
                Result = b''.join(Element.packBytes(BigEndian = BigEndian)
                                                        for Element in Data)
        else:
            Result = b''
        return Result

class SerDynamicArray(SerArray):
    """
    Implements auto-serilizable and de-serializable object representing C-array
    like structured data storage. Can be instantiate without an argument or
    with a single optional argument of a sequence type or another array.
    
    Class methods:
        getSize():
            None -> int >= 0 OR None
        unpackBytes(Data, BigEndian = None):
            bytes /, bool OR None/ -> 'SerDynamicArray
        unpackJSON(Data):
            str -> 'SerDynamicArray
        getElementSize():
            None -> int > 0
    
    Methods:
        packBytes(BigEndian = None):
            /bool OR None/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> list(type A)
    
    Version 1.0.0.1
    """
    
    #special methods
    
    def __init__(self, Data: Optional[Union[TSeq, Serializable]]=None) -> None:
        """
        Initialization method - copies the data from the passed sequence per
        element. The length of the created array equals the length of the
        passed sequence (or array).
        
        Signature:
            /seq(str -> type A) OR 'SerArray/ -> None
        
        Args:
            Data: (optional) seq(str -> type A) OR 'SerArray; sequence or an
                instance of SerArray (sub-) class
        
        Raises:
            UT_TypeError: passed argument is not a sequence type or an instance
                of sub-class of SerArray or SerDynamicArray OR the class data
                structure is defined improperly
            UT_ValueError: not matching data type in one of the elements,
                concerning the declared data type for the array elements
        
        Version 1.0.0.1
        """
        Checker = object.__getattribute__(self, '_checkDefinition')
        Checker() #UT_TypeError may be raised
        if not (Data is None):
            Cond1 = not isinstance(Data, (collections.abc.Sequence, SerArray))
            Cond2 = isinstance(Data, (str, bytes))
            if Cond1 or Cond2:
                raise UT_TypeError(Data, (collections.abc.Sequence, SerArray),
                                                                SkipFrames = 1)
            InputLength = len(Data)
        else:
            InputLength = 0
        ElementType = object.__getattribute__(self, '_ElementType')
        Elements = []
        for Index in range(InputLength):
            try:
                NewElement = ElementType(Data[Index])
            except (ValueError, TypeError):
                Message = 'being compatible with {} at index {}'.format(
                                                ElementType.__name__, Index)
                    
                raise UT_ValueError(Data[Index], Message,
                                                    SkipFrames = 1) from None
            if IsC_Scalar(ElementType):
                Elements.append(NewElement.value)
                del NewElement
            else:
                Elements.append(NewElement)
        object.__setattr__(self, '_Data', Elements)
    
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
        
        Version 1.0.0.1
        """
        if not isinstance(Data, list):
            raise UT_TypeError(Data, list, SkipFrames = 2)
        ElementsType = type.__getattribute__(cls, '_ElementType')
        IsScalar = IsC_Scalar(ElementsType)
        for Index, Element in enumerate(Data):
            try:
                if IsScalar:
                    Temp = ElementsType(Element)
                    del Temp
                else:
                    Checker = type.__getattribute__(ElementsType,
                                                        '_checkObjectContent')
                    Checker(Element)
            except (TypeError, ValueError):
                raise UT_ValueError(Element,
                        'compatible with {} type at index {}'.format(
                        ElementsType.__name__, Index), SkipFrames = 2) from None
    
    @classmethod
    def _parseBuffer(cls, Data: bytes,
                                    BigEndian: Optional[bool] = None) -> TList:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            /bool OR None/ -> list(type A)
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Returns:
            list(type A): a native Python list containing only native Python
                data type elements, compatible with the declared array elements
                type
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.1
        """
        DataSize = len(Data)
        ElementsType = type.__getattribute__(cls, '_ElementType')
        if IsC_Scalar(ElementsType):
            ElementSize = ctypes.sizeof(ElementsType)
        else:
            ElementSize = ElementsType.getSize()
        Length = DataSize // ElementSize
        Remainder = DataSize % ElementSize
        if Remainder:
            raise UT_ValueError(DataSize,
                                f'multiple of {ElementSize} - string length',
                                                                SkipFrames = 2)
        Result = []
        if Length:
            if IsC_Scalar(ElementsType):
                Result = [Bytes2Scalar(
                        Data[Index * ElementSize : (Index + 1) * ElementSize],
                                            ElementsType, BigEndian = BigEndian)
                                                    for Index in range(Length)]
            else:
                for Index in range(Length):
                    DataSplice = Data[Index*ElementSize : (Index+1)*ElementSize]
                    NewObject = ElementsType.unpackBytes(DataSplice,
                                                        BigEndian = BigEndian)
                    Result.append(NewObject.getNative())
                    del NewObject
        return Result
    
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
        
        Version 1.0.0.1
        """
        #check presence of the required private class attributes
        for strName in ('_ElementType', ):
            try:
                type.__getattribute__(cls, strName)
            except AttributeError:
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = 'Wrong definition of {} - {} is missing'.format(
                                                        cls.__name__, strName)
                Error.setMessage(Message)
                raise Error from None
        #check element type declaration
        ElementType = type.__getattribute__(cls, '_ElementType')
        if not IsC_Scalar(ElementType):
            try:
                IsSubClass = issubclass(ElementType, (SerArray, SerStruct))
            except TypeError: #built-in data type
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = ''.join(['Wrong definition of ', cls.__name__,
                                        '._ElementType - ', str(ElementType),
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                Error.setMessage(Message)
                raise Error from None
            if IsSubClass and (ElementType.getSize() is None): #dynamic length
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = 'Wrong definition of {}.{} is dynamic {}'.format(
                            cls.__name__, '_ElementType', ElementType.__name__)
                Error.setMessage(Message)
                raise Error
            elif not IsSubClass:
                if not isinstance(ElementType, type): #instance
                    TypeValue = str(ElementType)
                else: #some class
                    TypeValue = ElementType.__name__
                Error = UT_TypeError(1, int, SkipFrames = 2)
                Message = ''.join(['Wrong definition of ', cls.__name__,
                                    '._ElementType - ', TypeValue,
                                        ' is not sub-class of ',
                                        '(ctypes._SimpleCData, SerArray, ',
                                        'SerStruct)'])
                Error.setMessage(Message)
                raise Error
    
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
        
        Version 1.0.0.1
        """
        Checker = type.__getattribute__(cls, '_checkDefinition')
        Checker() #UT_TypeError may be raised
        return None
    
    @classmethod
    def getElementSize(cls) -> int:
        """
        Class method to get the byte size of a single element, which can be
        stored in a dynamic array.
        
        Signature:
            None -> int > 0
        
        Returns:
            int > 0: size in bytes required to present a single element
        
        Raises:
            UT_TypeError: wrong definition of the data structure
        
        Version 1.0.0.1
        """
        Checker = type.__getattribute__(cls, '_checkDefinition')
        Checker() #UT_TypeError may be raised
        ElementType = type.__getattribute__(cls, '_ElementType')
        if IsC_Scalar(ElementType):
            Size = ctypes.sizeof(ElementType)
        else:
            Size = ElementType.getSize()
        return Size

class SerNumber(Serializable):
    """
    Meta-class (prototype) for the implementation of the serializable scalar
    C-types (specifically, integers and floating point numbers). Cannot be
    instantiated itself, since it misses the BaseType.
    
    The subclasses should be created as in the example below, passing the
    required base type via the keyword argument:
    
        class NewType(SerNumber, BaseType = ctypes.c_ushort):
            pass
    
    Attributes:
        Value: type A
    
    Class methods:
        getSize():
            None -> int > 0
        unpackBytes(Data, BigEndian = None):
            bytes /, bool OR None / -> 'SerNumber
        unpackJSON(Data):
            str -> 'SerNumber
    
    Methods:
        packBytes(BigEndian = None):
            /bool OR None/ -> bytes
        packJSON():
            None -> str
        getNative():
            None -> type A
    
    Version 1.0.0.0
    """
    
    #special methods
    
    def __init_subclass__(cls, *, BaseType: ctypes._SimpleCData,
                                                            **kwargs) -> None:
        """
        Magic method for customization of the sub-classes. Sets the declared
        C-type of the sub-class to the value passed as the keyword argument.
        
        Signature:
            class ctypes._SimpleCData/, **kwargs/ -> None
        
        Args:
            BaseType: (keyword) class ctypes._SimpleCData; the desired C-type of
                the subclass
        
        Raises:
            UT_TypeError: the passed value is of the wrong data type
        
        Version 1.0.0.0
        """
        ErrorMessage = '- BaseType is not a C scalar data type subclass'
        Error = UT_TypeError(BaseType, ctypes._SimpleCData, SkipFrames = 1)
        Error.appendMessage(ErrorMessage)
        try:
            IsC_ScalarType = issubclass(BaseType, ctypes._SimpleCData)
        except TypeError:
            raise Error from None
        if not IsC_ScalarType:
            raise Error
        del Error
        super().__init_subclass__(**kwargs)
        cls.BaseType = BaseType

    def __init__(self, Value: Any = 0) -> None:
        """
        Initialization method. The passed argument value must be compatible with
        the declared C-type of the class. The default value is 0.
        
        Signature:
            /type A/ -> None
        
        Raises:
            UT_TypeError: the class definition lacks the BaseType attribute or
                it holds improper value, not a C-type, OR the value of the
                passed argument is not compatible with the declared C-type
            
        Version 1.0.0.0
        """
        Checker = object.__getattribute__(self, '_checkDefinition')
        Checker()
        Checker = object.__getattribute__(self, '_checkObjectContent')
        Checker(Value)
        CastValue = self.BaseType(Value).value
        object.__setattr__(self, '_Value', CastValue)
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Special, magic method hooking the assignment to an attribute access.
        
        Signature:
            str, type A -> None
        
        Args:
            name: str; name of the attribute, can be only Value
            value: type A; value to be be assigned, must be compatible with the
                declared C-type of the class
        
        Raises:
            UT_AttributeError: assigment to any attribute except Value
            UT_TypeError: value to be assigned to Value is not compatible with
                the declared C-type of the class
        
        Version 1.0.0.0
        """
        if name != 'Value':
            raise UT_AttributeError(self, name, SkipFrames = 1)
        Checker = object.__getattribute__(self, '_checkObjectContent')
        Checker(value)
        CastValue = self.BaseType(value).value
        object.__setattr__(self, '_Value', CastValue)
    
    #private helper methods
    
    @classmethod
    def _checkObjectContent(cls, Data: Any) -> None:
        """
        Private class method to check if the extracted JSON object matches the
        declared C-type of the class.
        
        Signature:
            type A -> None
        
        Args:
            Data: type A; any type data to be checked
        
        Raises:
            UT_TypeError: the type of the passed argument is not compatible with
                the class
        
        Version 1.0.0.0
        """
        try:
            cls.BaseType(Data)
        except Exception as err:
            Message = f'- value incompatible with the class - {err.args[0]}'
            Error = UT_TypeError(Data, cls.BaseType, SkipFrames = 2)
            Error.appendMessage(Message)
            raise Error
    
    @classmethod
    def _parseBuffer(cls, Data: bytes, BigEndian: Optional[bool] = None) -> Any:
        """
        Private class method to parse the content of the passed byte string into
        a native Python object using the class data structure definition.
        
        Signature:
            bytes /, bool OR None/ -> type A
        
        Args:
            Data: bytes; data to be checked
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Raises:
            UT_ValueError: size of the passed bytestring does not match the
                declared data structure size
        
        Version 1.0.0.0
        """
        DataSize = len(Data)
        ExpectedSize = cls.getSize()
        if DataSize != ExpectedSize:
            raise UT_ValueError(DataSize, f'= {ExpectedSize} - data length',
                                                                SkipFrames = 2)
        Result = Bytes2Scalar(Data, cls.BaseType, BigEndian = BigEndian)
        return Result
    
    @classmethod
    def _checkDefinition(cls) -> None:
        """
        Private class method to check the definition of the data structure of
        the class. Supposed to be called by all class methods, including the
        unpacking (constructors), and the initialization instance method.
                
        Signature:
            None -> None
        
        Raises:
            UT_TypeError: required class attributes are missing OR they hold
            wrong type vales
        
        Version 1.0.0.0
        """
        if not hasattr(cls, 'BaseType'):
            Error = UT_TypeError(1, int, SkipFrames = 2)
            Message= f'Wrong definition of {cls.__name__} - BaseType is missing'
            Error.setMessage(Message)
            raise Error
        BaseType = cls.BaseType
        Error = UT_TypeError(BaseType, ctypes._SimpleCData, SkipFrames = 1)
        Message = f'Wrong definition of {cls.__name__} - BaseType is not C-type'
        Error.appendMessage(Message)
        try:
            IsC_ScalarType = issubclass(BaseType, ctypes._SimpleCData)
        except TypeError:
            raise Error from None
        if not IsC_ScalarType:
            raise Error
        del Error
    
    #public API
    
    #+ properties
    
    @property
    def Value(self) -> Any:
        """
        Getter property to access the stored value. The respective setter
        property is emulated via set access hook method.
        
        Signature:
            None -> type A
        
        Version 1.0.0.0
        """
        return object.__getattribute__(self, '_Value')
    
    #+ class methods
    
    @classmethod
    def getSize(cls) -> int:
        """
        Method to obtain the declared size in bytes of the C-type represented
        by this class.
        
        Signature:
            None -> int > 0
        
        Raises:
            UT_TypeError: the class definition lacks the BaseType attribute or
                it holds improper value, not a C-type
        
        Version 1.0.0.0
        """
        cls._checkDefinition()
        return ctypes.sizeof(cls.BaseType)
    
    #+ instance methods
    
    def getNative(self) -> Any:
        """
        Method for convertion of the stored C-type data into native Python data
        type.
        
        Signature:
            None -> type A
        
        Returns:
            type A: native Python type representation of the stored data
        
        Version 1.0.0.0
        """
        return self.Value
    
    def packBytes(self, BigEndian: Optional[bool] = None) -> bytes:
        """
        Method for serialization of the stored data into bytes. The optional
        argument BigEndian is interpreted either as None or as boolean value
        regardless of its actual data type.
        
        Signature:
            /bool OR None/ -> bytes
        
        Args:
            BigEndian: (optional) bool OR None; 3-way selector to indicate the
                desired endianness - the default value is None, meaning native,
                passed True value forces big endian format, passed False value
                forces little endian format.
        
        Returns:
            bytes: bytestring representing the entire stored data
        
        Version 1.0.0.0
        """
        return Scalar2Bytes(self.Value, self.BaseType, BigEndian = BigEndian)
