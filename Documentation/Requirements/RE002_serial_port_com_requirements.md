# Requirements for the Module com_lib.serial_port_com

## Conventions

Requirements listed in this document are constructed according to the following structure:

**Requirement ID:** REQ-UVW-XYZ

**Title:** Title / name of the requirement

**Description:** Descriprion / definition of the requirement

**Verification Method:** I / A / T / D

The requirement ID starts with the fixed prefix 'REQ'. The prefix is followed by 3 letters abbreviation (in here 'UVW'), which defines the requiement type - e.g. 'FUN' for a functional and capability requirement, 'AWM' for an alarm, warnings and operator messages, etc. The last part of the ID is a 3-digits *hexadecimal* number (0..9|A..F), with the first digit identifing the module, the second digit identifing a class / function, and the last digit - the requirement ordering number for this object. E.g. 'REQ-FUN-112'. Each requirement type has its own counter, thus 'REQ-FUN-112' and 'REQ-AWN-112' requirements are different entities, but they refer to the same object (class or function) within the same module.

The verification method for a requirement is given by a single letter according to the table below:

| **Term**          | **Definition**                                                               |
| :---------------- | :--------------------------------------------------------------------------- |
| Inspection (I)    | Control or visual verification                                               |
| Analysis (A)      | Verification based upon analytical evidences                                 |
| Test (T)          | Verification of quantitative characteristics with quantitative measurement   |
| Demonstration (D) | Verification of operational characteristics without quantitative measurement |

## Functional and capability requirements

**Requirement ID:** REQ-FUN-200

**Title:** Asynchronous and synchronous communication classes

**Description:** The module should implement two classes: for the asynchronous and synchronous communication with a device via a serial port respectively. Both classes should wrap the functionality of the **PySerial** library, but they should allow replacement of the backend by another implementation of the serial port communication, or even by a mock object.

**Verification Method:** A

---

**Requirement ID:** REQ-FUN-201

**Title:** Openning the connection

**Description:** Both asynchronous and synchronous communication classes must provide method *open*() to open the connection. This method should require the name of the port to connect to, other connection parameters are optional and could be passed as the keyword arguments. Already open connection cannot be openned again - this is an error, which should result in an exception.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-202

**Title:** Closing the connection

**Description:** Both asynchronous and synchronous communication classes must provide method *close*() to close the connection. This method should not require any arguments. Already closed connection cannot be closed again - this is an error, which should result in an exception.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-203

**Title:** Querring the connection status

**Description:** Both asynchronous and synchronous communication classes must provide poperty *IsOpen* to query the connection status. It must return **True** if the connection is open, and **False** otherwise.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-204

**Title:** Serial ports via USB enumeration

**Description:** The module must provide a function / method to list the names of all USB ports, which can be used as the serial ports to communicate with the real devices, i.e. those ports, which have not *None* VID and PID.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-210

**Title:** Sending command asynchronously

**Description:** The asynchronous communication class must provide method *sendCommand*() to send a command to a device. It must not await the response form the device, and it must return the control immediately.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-211

**Title:** Receiving response asynchronously

**Description:** The asynchronous communication class must provide method *getResponse*() to receive a response to a device. It must await the response form the device but no longer than the timeout period. The response from the device must be acquired as a complete package and returned as a string with the package delimiter removed. If the expiration of the timeout is reached but the package is not received, it should return *None* value.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-220

**Title:** Sending command synchronously

**Description:** The synchronous communication class must provide method *sendCommand*() to send a command to a device. It must await the response form the device, and it must return the the device's response, thus it should block the execution flow until the response is received, or the timeout period is expired. The response from the device must be acquired as a complete package and returned to the caller. Expiration of the timeout period should result in closing the connection and raising the **SerialTimeoutException**.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-221

**Title:** Receiving response synchronously

**Description:** With the synchronous communication the response from the device must be automatically returned by the *sendCommand*() method. The synchronous communication class may provide method *getResponse*() to receive a response to a device, but the class' clent is not supposed to use it directly, since the communication buffer should be empty between the sendings. Thus, if called directly, this method should wait for the timeout expiration and return *None* value.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-222

**Title:** Minimal call overhead

**Description:** With the synchronous communication the sending command and receiving the device's response work flow should not introduce an overhead of more than ~ 1 ms in the real life scenarios, e.g. communicating with a CFR rev 1 device from a typical modern PC.

**Verification Method:** T

## Alarms, warnings and operator messages

**Requirement ID:** REQ-AWM-200

**Title:** Opening of an open connection raises an exception

**Description:** An attempt to open again the already open connection must raise **SerialException**.

**Verification Method:** T

---

**Requirement ID:** REQ-AWM-201

**Title:** Closing of a closed connection raises an exception

**Description:** An attempt to close the already closed connection must raise **SerialException**.

**Verification Method:** T

---

**Requirement ID:** REQ-AWM-202

**Title:** Communication with a closed connection raises an exception

**Description:** An attempt to write into or read from a closed connection must raise **SerialException**.

**Verification Method:** T
