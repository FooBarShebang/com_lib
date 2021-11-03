# UD003 User and API Reference for the Module serialization

## Scope

## Design and Functionality

## Implementation Details

The components diagram of the module is shown below.

![Components diagram](../UML/serialization/serialization_components.png)

All functions defined in the module are 'helper' functions for the defined classes; however their functionality can be usefull in many situations, so it is implemented in the form of functions instead of the methods of the classes. Note that they do not perform the input data sanity checks, therefore, use with caution.

The function *IsC_Scalar*() returns **True** only if the passed argument is a sub-class of **ctypes._SimpleCData** (but not an instance, i.e. **type** not **object**). Otherwise it returns **False**.

The functions *Scalar2BytesNE*(), *Scalar2BytesLE*() and *Scalar2BytesBE*() return the bytestring representation of a native Python scalar value (e.g. **int** or **float** type value) according to specific C data type internal structure in the platform native, forced little endian and forced big endian byte order. For instance, the native Python integer value 1 is represented as b'\x01\x00' for C **int16** (**short**) type with the little endianness, but as b'\x00\x00\x00\x01' for **int32** (**long**) with the big endianness. Note, that the passed native Python value must be compatible with the passed **ctypes** type (class) initialization method optional argument. The function *Scalar2Bytes*() is a wrapper, which calls one of the functions above based on the values of the optional argument.

The functions *Bytes2ScalarNE*(), *Bytes2ScalarLE*() and *Bytes2ScalarBE*() perform the inverse operation, they convert a bytestring into a native Python scalar value, assuming that the passed bytestring contains the platform native, forced little endian and forced big endian byte order respectively byte representation of the value of a specific C type, which is passed as the second argument. The function *Bytes2Scalar*() is a wrapper, which calls one of the functions above based on the values of the optional argument. Note, that the bytestring should be not shorter than the number of bytes required to represent the corresponding C data type.

The class diagram of the module is given below.

![Class diagram](../UML/serialization/serialization_classes.png)

The class **Serializable** is a *prototype* for the specialized sub-classes **SerNULL**, **SerStruct**, **SerArray** and **SerDynamicArray**. It implements all functionality common for the specialized sub-classes and defines logic of the future implementation of the sub-class specific functionality. Basically, a number of methods are declared as *abstract* methods, therefore, it cannot be instantiated, and any sub-class MUST implement the corresponding methods as not abstract, otherwise sub-class cannot be instantated either.

## API

### Functions

### Classes
