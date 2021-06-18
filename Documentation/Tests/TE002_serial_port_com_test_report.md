# Test Report on the Module com_lib.serial_port_com

## Conventions

Each test is defined following the same format. Each test receives a unique test identifier and a reference to the ID(s) of the requirements it covers (if applicable). The goal of the test is described to clarify what is to be tested. The test steps are described in brief but clear instructions. For each test it is defined what the expected results are for the test to pass. Finally, the test result is given, this can be only pass or fail.

The test format is as follows:

**Test Identifier:** TEST-\[I/A/D/T\]-XYZ

**Requirement ID(s)**: REQ-uvw-xyz

**Verification method:** I/A/D/T

**Test goal:** Description of what is to be tested

**Expected result:** What test result is expected for the test to pass

**Test steps:** Step by step instructions on how to perform the test

**Test result:** PASS/FAIL

The test ID starts with the fixed prefix 'TEST'. The prefix is followed by a single letter, which defines the test type / verification method. The last part of the ID is a 3-digits *hexadecimal* number (0..9|A..F), with the first digit identifing the module, the second digit identifing a class / function, and the last digit - the test ordering number for this object. E.g. 'TEST-T-112'. Each test type has its own counter, thus 'TEST-T-112' and 'TEST-A-112' tests are different entities, but they refer to the same object (class or function) within the same module.

The verification method for a requirement is given by a single letter according to the table below:

| **Term**          | **Definition**                                                               |
| :---------------- | :--------------------------------------------------------------------------- |
| Inspection (I)    | Control or visual verification                                               |
| Analysis (A)      | Verification based upon analytical evidences                                 |
| Test (T)          | Verification of quantitative characteristics with quantitative measurement   |
| Demonstration (D) | Verification of operational characteristics without quantitative measurement |

## Tests preparations

In order to perform the tests the following preparations must be made.

### Unit tests com_lib.tests.ut002_serial_port_com.py

Implement the sub-classes of the asynchronous and synchronous communication classes. Both classes must use com_lib.mock_serial.MockSerial class as their backend instead of **serial.Serial** class from the **PySerial** library.

Both classes should prepare the command to be send by appending zero character ('\x00') to the passed byte string (actually, simple ASCII string as a textual command). Both classes should parse the received response by removing the last tailing zero character, if one is present. The synchronous communication sub-class must compare the command to be send (before parsing) and the parsed response, and return **True** if they are equal, otherwise - **False**.

### Functional test com_lib.tests.ft002_serial_port_com.py

Implement the sub-class of the synchronous communication class. It should prepare the sending from the passed comand code (as integer, 32-bit, unsigned) and the already prepared packed byte string command data by appending the high-first bytes representation of the command code to the command data string, encoding the resulting string with COBS algorithm and adding the zero character ('\x00') at the end. The received response should be stripped of the last tailing zero character (if present), decoded using COBS algorithm and split into the command code bytes (last 3 characters) and the actual response data (the rest before the last 3 bytes). The received command code bytes (only last 2) are to be converted into an integer assuming high-first byte order. The response command code is to be compared with the send command code as the response verification method.

### Functional tests com_lib.tests.ft003_serial_port_com.py and com_lib.tests.ft004_serial_port_com.py

Implement the sub-class of the synchronous communication class. The sending parser must accept 3 arguments: the command code, the command data and the type (class) onto which the response is to be cast. It should prepare the sending from the passed comand code (as integer, 32-bit, unsigned), the command data stored in a (nested) structure object, which should be packed into a byte string. The high-first bytes representation of the command code is to be appended to the packed command data byte string, and the resulting string should be encoded with COBS algorithm. The zero character ('\x00') should be added at the end. The received response should be stripped of the last tailing zero character (if present), decoded using COBS algorithm and split into the command code bytes (last 3 characters) and the actual response data (the rest before the last 3 bytes). The received command data should be unpacked into the an instance of the required type (class). The received command code bytes (only last 2) are to be converted into an integer assuming high-first byte order. The response command code is to be compared with the send command code as the response verification method.

## Test definitions (Test)

**Test Identifier:** TEST-T-200

**Requirement ID(s)**: REQ-FUN-201, REQ-FUN-202, REQ-FUN-203, REQ-FUN-210, REQ-FUN-211, REQ-AWM-200, REQ-AWM-201, REQ-AWM-202

**Verification method:** T

**Test goal:** Tests the asynchronous communication using mock serial connection as the backend. Checks the opening and closing the connection, quering the connection status, sending and receiving the data, including the timeout situation. Checks that the open connection cannot be open again. Checks that the closed connection cannot be either closed again or communicated with.

**Expected result:** All associated unit tests pass

**Test steps:** Implemented as the unit tests suite **Test_MockComAssync** within the module com_lib.tests.ut002_serial_port_com.py, defines the following test cases

* initialize the connection, check the status (must be **True**), close the connection, check the status (must be **False**)
* initialize the connection, try to open the connection again - **SerialException** must be raised, close the connection
* initialize the connection, close it, try to close the connection again - **SerialException** must be raised
* initialize the connection, close it, try to send the 'fast' command - **SerialException** must be raised
* initialize the connection, close it, try to read from the port - **SerialException** must be raised
* initialize the connection, send 3 commands 'fast', 'slow', 'very_slow', read from the times 3 times with specifically indicated long timeout period (of 20 sec) and check the results - the same commands and in the same order must be received; close the connection
* initialize the connection, send the command 'fast' and check the result with the default timeout (0.1 sec) - should receive 'fast' back; then send the command 'very_slow' and check the result with the default timeout (0.1 sec) - should receive *None* value (timeout); close the connection

**Test result:** PASS / FAIL

---

**Test Identifier:** TEST-T-201

**Requirement ID(s)**: REQ-FUN-201, REQ-FUN-202, REQ-FUN-203, REQ-FUN-220, REQ-FUN-221, REQ-AWM-200, REQ-AWM-201, REQ-AWM-202

**Verification method:** T

**Test goal:** Tests the synchronous communication using mock serial connection as the backend. Checks the opening and closing the connection, quering the connection status, sending and receiving the data, including the timeout situation. Checks that the open connection cannot be open again. Checks that the closed connection cannot be either closed again or communicated with. Check that timeout results in the closing of the connection and raising **SerialTimeoutException**. Check that explicit call of the *getResponse*() method even after the successfull sending returns **None**.

**Expected result:** All associated unit tests pass

**Test steps:** Implemented as the unit tests suite **Test_MockComSync** within the module com_lib.tests.ut002_serial_port_com.py, defines the following test cases

* initialize the connection, check the status (must be **True**), close the connection, check the status (must be **False**)
* initialize the connection, try to open the connection again - **SerialException** must be raised, close the connection
* initialize the connection, close it, try to close the connection again - **SerialException** must be raised
* initialize the connection, close it, try to send the 'fast' command - **SerialException** must be raised
* initialize the connection, close it, try to read from the port - **SerialException** must be raised
* initialize the connection, send 3 commands 'fast', 'slow', 'very_slow' with specifically indicated long timeout period (of 20 sec) and check the results each time - the same commands must be received; close the connection
* initialize the connection, send the command 'fast' with the default timeout (10 sec) - should receive 'fast' back; then send the command 'very_slow' with the default timeout (10 sec) - should raise the **SerialTimeoutException** (timeout); check the connection - should be **False** (closed)
* initialize the connection, send the command 'fast' with the default timeout (10 sec); then read from the port explicitly with the default timeout (10 sec) - should return *None* value; close the connection

**Test result:** PASS / FAIL

---

**Test Identifier:** TEST-T-202

**Requirement ID(s)**: REQ-FUN-220, REQ-FUN-221, REQ-FUN-204

**Verification method:** T

**Test goal:** Demonstrate compatibility of the module (asynchronous and synchronous communication wrapper classes) with the **PySerial** library, specifically with the **serial.Serial** class as the backend. Test that the communication with a real CFR rev 1 device is established using the name of the port it is connected to as the argument of the initialization method. Test the communication layer by sending the simple commands like setting the output of a single specific light source and reading a specified number of samples from a specific detector / sensor.

**Expected result:** The device blinks the specified number of times with the specified light source and reports the read-outs from its sensor, which depend on the source light intensity and the measurement target placed on top of the device.

**Test steps:**

Use the settings defined in either the com_lib.tests.ft002_serial_port_com.py or the com_lib.tests.ft003_serial_port_com.py functional tests module, i.e. **PySerial** library as the backend and synchronous communication with a real CFR rev 1 device (actual measurements).

* Connect an CFR rev 1 device to the PC and make sure that this connection is recognized as the only one or the first real serial communication port (with VID and PID)
* Use function *list_comports*() defined in the module libhps.tools.serial_port_communication to produce the list of the active COM-port names and use the first entry as the argument to open the connection
* Send a command to set the intensity of a selected light source (e.g. UV) to the specified value > 0 (e.g. 100)
* Send a command to to 'read' the specified number of samples from the specified detector (e.g. emission sensor)
* Print the received resonse (sensor's read-out) into the console
* Wait (sleep) for a short period, e.g. ~ 1 sec
* Send a command to set the intensity of the same light source to 0 (zero)
* Send a command to to 'read' the same number of samples from the same detector
* Print the received resonse (sensor's read-out) into the console
* Wait (sleep) for a short period, e.g. ~ 1 sec
* Repeat the last 8 steps 4 times
* Close the connection

**Test result:** PASS / FAIL

---

**Test Identifier:** TEST-T-220

**Requirement ID(s)**: REQ-FUN-222

**Verification method:** T

**Test goal:** Measure the overhead introduced by the data processing (packing of a structure into a bytestring, encoding, decoding, unpacking of a byte sequence into a structure, etc.), the switching between the threads and the actual serial port communication.

**Expected result:** The call overhead should be no more than ~ 1 ms.

**Test steps:**

Use the settings defined in the com_lib.tests.ft004_serial_port_com.py functional tests module, i.e. **PySerial** library as the backend, synchronous communication with a real CFR rev 1 device (actual measurements), (nested) structure data types as the arguments (command data) and retruned values (response data). The test steps are:

* Connect an CFR rev 1 device to the PC and make sure that this connection is recognized as the only one or the first real serial communication port (with VID and PID)
* Use function *list_comports*() defined in the module libhps.tools.serial_port_communication to produce the list of the active COM-port names and use the first entry as the argument to open the connection
* Start the timer and send the command to the device to 'read' the specified number of samples from the specified detector (e.g. emission sensor)
* Upon receiving the response from the device stop the timer and report the measured time period and the number of samples used
* Repeat the measurement 5 times with each number of samples to calculate the averaged value, thus minimizing the jitter related to the threads switching
* Repeat the measurements with the different number of samples from 10 to 10000 using logarithmic scale of the steps
* Close the connection
* Use linear regression / linear fit model to determine the average (sampling) rate as the slope and the overhead as the offset

**Test result:** PASS / FAIL

## Test definitions (Analysis)

**Test Identifier:** TEST-A-200

**Requirement ID(s)**: REQ-FUN-200

**Verification method:** A

**Test goal:** Both classes must have either a method or a property or a field, which defines the backend serial port interface. Both classes by default must refer to the **PySerial** library, but their sub-classes can re-define the corresponding attributes.

**Expected result:** The required attributes are defined for the both classes, and they refer to the **PySerial** library. Sub-classes can change those attributes so that the mock serial port object is used instead of that library. Upon implementation of all required helper methods these sub-classes can be instantiated, and they should provide the proper communication with the virtual device via the virtual port as defined in the com_lib.mock_serial.py module.

**Test steps:** Analyze the source code. Implement the asynchronous and synchronous communcation sub-classes based upon libhps.tools.mock_serial.MockSerial class. Use them in the unit tests defined by the test cases TEST-T-200 and TEST-T-201. Implement the synchronous communication sub-class based upon serial.Serial class as the backend (**PySerial** library) and use it in the functional tests TEST-T-202 and TEST-T-220.

**Test result:** PASS

## Traceability

For traceability the relation between tests and requirements is summarized in the table below:

| **Requirement ID** | **Covered in test(s)** | **Verified \[YES/NO\]**) |
| :----------------- | :--------------------- | :----------------------- |
| REQ-FUN-200        | TEST-A-200             | NO                       |
| REQ-FUN-201        | TEST-T-200, TEST-T-201 | NO                       |
| REQ-FUN-202        | TEST-T-200, TEST-T-201 | NO                       |
| REQ-FUN-203        | TEST-T-200, TEST-T-201 | NO                       |
| REQ-FUN-204        | TEST-T-202             | NO                       |
| REQ-FUN-210        | TEST-T-200             | NO                       |
| REQ-FUN-211        | TEST-T-200             | NO                       |
| REQ-FUN-220        | TEST-T-201, TEST-T-202 | NO                       |
| REQ-FUN-221        | TEST-T-201, TEST-T-202 | NO                       |
| REQ-FUN-222        | TEST-T-220             | NO                       |
| REQ-AWN-200        | TEST-T-200             | NO                       |
| REQ-AWN-201        | TEST-T-200             | NO                       |
| REQ-AWN-202        | TEST-T-200             | NO                       |

| **Software ready for production \[YES/NO\]** | **Rationale**        |
| :------------------------------------------: | :------------------- |
| YES                                          | All tests are passed |
