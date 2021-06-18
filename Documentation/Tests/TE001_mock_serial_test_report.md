# Test Report on the Module libhps.tools.mock_serial

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

## Test definitions (Test)

**Test Identifier:** TEST-T-100

**Requirement ID(s)**: REQ-FUN-100, REQ-FUN-101, REQ-FUN-102, REQ-FUN-103,REQ-AWM-101, REQ-AWM-102

**Verification method:** T

**Test goal:** Check that the module implements the virtual serial port, which can be connected to a virtual device. Check that the virtual port provides the minimal API compatible with the **PySerial** library. Check that the virtual device generates 3 different time delayed responses to the commands 'fast', 'slow' and 'very_slow'. Test that the virtual devices emulates the 'physical' disconnect upon the command 'quit'. Check that other commands do not yield any response from the device. Test that the closed port (disconnected device) does not allow communication with the device, and that a closed port cannot be closed again.

**Expected result:** Five commands sent, 3 responses received, 2 exceptions raised.

**Test steps:** Implement as a functional test Python script.

* Create a stream listener object running in a separate thread, which listens to the output buffer stream of the virtual port, as all available bytes from the stream as soon as they become available, and prints to the console the entire accumulated package (byte-string) as soon as the package delimiter '\x00' is received, which starts the accumulation of a new package
* Open the virtual port, which create a virtul device, and bind this port to the threaded listener object
* Send commands 'fast', 'slow', 'unknown' and 'very_slow' and print them to the console as well
* Wait for 20 sec to allow all commands to be processed; the listener should report only 3 received responses: 'fast', 'slow' and 'very_slow'
* Print to the console and send to the port the command 'quit'
* Wait 1 sec to allow the processing of the command; the **SerialException** must be raised from the thread, where the listener object runs
* Stop the listener thread and await for its proper termination
* Try to close the serial port, wich should be already closed automatically it this point; the **SerialException** must be raised from the main thread

This test is implemented as com_lib.tests.ft001_mock_serial.py module.

**Test result:** PASS / FAIL

---

**Test Identifier:** TEST-T-101

**Requirement ID(s)**: REQ-AWM-100, REQ-AWM-101, REQ-AWM-102

**Verification method:** T

**Test goal:** Using unit test cases check that the already open port cannot be open again, that the closed port cannot be closed, that it is not possible to query the size of the ouput buffer of the closed port, that it is not possible to read from or write into the closed port.

**Expected result:** All unit test cases pass, i.e. the expected exception is raised and caught in each case.

**Test steps:** Implement the following unit test cases:

* open the port, try to open it again (exception must be raised), close the port
* open the port, close it, try to close it again (exception must be raised)
* open the port, close it, try to get the size of the buffer (exception must be raised)
* open the port, close it, try to send a command (exception must be raised)
* open the port, close it, try to read one byte from the buffer (exception must be raised)

This test is implemented as com_lib.tests.ut001_mock_serial.py module.

**Test result:** PASS / FAIL

## Traceability

For traceability the relation between tests and requirements is summarized in the table below:

| **Requirement ID** | **Covered in test(s)** | **Verified \[YES/NO\]**) |
| :----------------- | :--------------------- | :----------------------- |
| REQ-FUN-100        | TEST-T-100             | NO                       |
| REQ-FUN-101        | TEST-T-100             | NO                       |
| REQ-FUN-102        | TEST-T-100             | NO                       |
| REQ-FUN-103        | TEST-T-100             | NO                       |
| REQ-AWM-100        | TEST-T-101             | NO                       |
| REQ-AWM-101        | TEST-T-100, TEST-T-101 | NO                       |
| REQ-AWM-102        | TEST-T-100, TEST-T-101 | NO                       |

| **Software ready for production \[YES/NO\]** | **Rationale**        |
| :------------------------------------------: | :------------------- |
| NO                                           | Under development    |
