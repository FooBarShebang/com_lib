# DE000 General Design of the Library com_lib

## Intended Use and Functionality

This library is designed to provide object-oriented API as an abstraction layer between the **pySerial** library (treating serial port as a stream and operating with bytes) and the client software working with more abstract, more structured data types. The client software is supposed to provide some chunk of data, which is to be send as a single *package*. The response (if any) is supposed to be a *package*. Furthermore, the client software may operate as a pure *data provider* only sending some data or commands, whilst the other side doesn't send any responses, or they are ignored by the *provider*. Alternatively, the client software may operate as a pure *data consumer* simply listening to data coming from a different device. The third most common situation is synchronous bi-directional communication, when the client software requires and awaits a response to any send data package before it is able to proceed further.

Thus, the library **com_lib** is responsible for:

* *Atomic* data send and receive operations in form of *packages*
* Implementation of synchronous send-receive mode of communication
* Implementation of asynchronous mode of communication, when the requests to send or receive a package may be issued in any order
* Conversion of the data received from the client software into a package
* Conversion of the package received into a data in the format expected by the client software

Concerning the *packages* the design choice is to use *zero-terminated packages*. Basically, a package is an arbitrary length of non-zero bytes (1 <= byte\_value <= 255) followed by 0 value as the package terminator. This approach allows an arbitrary length of a package according to the amount of data to be transmitted. Furthermore, a sequence of *N* zeroes is treated as *N-1* empty packages following the last received non-empty package. Since zeroes are not allowed in a sequence of bytes to be send as a single package, the arbitrary bytestrings representing the actual data are COBS encoded before sending, and the received packages are COBS decoded.

In the asynchronous mode the **com_lib** library should send packages exactly in the same order as the respective data chunks are received. It should also accumulate and queue all received packages, and return them one at a time and exactly in the received order with each *receive package request*.

In the synchronous mode the **com_lib** must await a response to each sent package, which response should be returned to the client piece of software using the library. This mode implies that the other side always sends response on each received package. Thus, in the simplest form this mode is sending a packaging and awaiting a response until it is received and is to be returned to the caller, or until a timeout (threshold time interval between sending and receiving) is reached, which is *fault* situation.

However, the design decision is made to allow mixing synchronous and asynchronous communication in a single session. In such a situation it is difficult to differentiate between package received in response to the last (synchronously) sent package and the unclaimed responses to the previously asynchronously sent packages. In order to break the ambiguity the following procedure is applied assuming that the other side always sends response:

* Each package sent in either synchronous or asynchronous mode increments an internal *Sent* , which value is returned to the client software for book-keping
* Each received package increments internal counter *Received* and is queued together with the current value of that counter, until it is requested by and dispached to the client software
* In the asynchronous mode upon each *receive* request the incoming buffer is checked and all 'complete' packages are pulled out and queued. The first package awaiting in the queue is returned together with the coupled 'received index'; or nothing (None) is returned if the queue is empty
* In the synchronous mode the incoming buffer is repetitively pulled and the queue is populated until the timeout is reached or the values of the both *Sent* and *Received* counters become equal. If timeout is reached before the required response is received an exception should be raised to indicate a *fault* situation. Otherwise the last package in the queue is returned together with the corresponding index. In the both cases the packages remaining in the queue are discarded
* The asynchronous sending and package quering operations are virtually non-blocking, whereas the synchronous mode is blocking by design

Such design has no drawbacks if the synchronous or asynchronous mode is used exclusively during the session. It is beneficial in the case when the client software doesn't care about responses to some data sent, and it can spend some time in between sending to do something else without multi-threading. Only packages with the required response should be sent in the synchronous mode. However the synchronous and asynchronous modes can be mixed only if the communication is always bi-directional, otherwise the asynchronous mode should be used solely.

The [pySerial](https://pypi.org/project/pyserial/) operates with bytestrings, whereas the client software can provide data in the different format, thus it is also responsibility of the library **com_lib** to convert the data into a bytestring and to perform the reverse conversion of the received packages.

Thus, the intended use of the library is summarized in the diagram below

![Use cases](../UML/Design/use_cases.png)

The next diagram illustrates the place of the library in the entire communication process

![Layers](../UML/Design/layers.png)

## Design Details
