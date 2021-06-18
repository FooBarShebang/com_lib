# Requirements for the Module com_lib.mock_serial

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

**Requirement ID:** REQ-FUN-100

**Title:** Implements virtual serial port to a virtual device

**Description:** The module should implement a virtual device and a virtual serial port able to connect to and communicate with that virtual device.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-101

**Title:** Virtual serial port API

**Description:** The object implementing the virtual serial port must provide the minimal set of the API compatible with the **PySerial** library, i.e. the methods *open*(), *close*(), *write*(), *read*() and *IsOpen*() as well as the property *in_waiting* with the same functionality as in the mentioned library.

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-102

**Title:** Virtual device commands

**Description:** The virtual device implementation should accept the commands as plain ASCII strings send via the virtual port and send the response when applicable also as plain ASCII strings. The minimum set of the commands requied is: 'fast', 'slow', 'very_slow' and 'quit'. The response to the first 3 commands should be the command name itself but returned either immediately or with ~ 1 sec delay or with > 5 sec delay respectively. There should be no response for the last command, but the unexpected disconnection of the device from the port should be emulated (the port remains connected). Any other command recieved should be simply ignored (no response).

**Verification Method:** T

---

**Requirement ID:** REQ-FUN-103

**Title:** Communication with the virtual device

**Description:** The virtual device should consume the command from the port (input buffer) immediately and as an atom. The device should generate the response one byte (character) at the time, and the end of the response should be marked by the zero character ('\x00') package delimiter.

**Verification Method:** T

---

## Alarms, warnings and operator messages

**Requirement ID:** REQ-AWM-100

**Title:** Opening of an open connection raises an exception

**Description:** An attempt to open again the already open connection must raise **SerialException**.

**Verification Method:** T

---

**Requirement ID:** REQ-AWM-101

**Title:** Closing of a closed connection raises an exception

**Description:** An attempt to close the already closed connection must raise **SerialException**.

**Verification Method:** T

---

**Requirement ID:** REQ-AWM-102

**Title:** Communication with a closed connection raises an exception

**Description:** An attempt to write into, read from or query the size of the output buffer of a closed connection must raise **SerialException**.

**Verification Method:** T
