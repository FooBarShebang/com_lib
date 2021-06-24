# Entire Library Requirements and Tests Traceability List

## Relation between modules, classes and the requirements and tests indexing

* entire library - 00x
* module *mock_serial* - 1xx
* module *serial_port_com* - 2xx
* module *serialization* - 3xx

## Requirements vs Tests Traceability

| **Requirement ID** | **Covered in test(s)** | **Verified \[YES/NO\]**) |
| :----------------- | :--------------------- | :----------------------- |
| REQ-FUN-000        | TEST-A-000             | NO                       |
| REQ-FUN-001        | TEST-A-000             | NO                       |
| REQ-INT-000        | TEST-I-000             | NO                       |
| REQ-IAR-000        | TEST-D-000             | NO                       |
| REQ-IAR-001        | TEST-D-001             | NO                       |
| REQ-IAR-002        | TEST-D-000             | NO                       |
| REQ-UDR-000        | TEST-I-001             | NO                       |
| REQ-FUN-100        | TEST-T-100             | NO                       |
| REQ-FUN-101        | TEST-T-100             | NO                       |
| REQ-FUN-102        | TEST-T-100             | NO                       |
| REQ-FUN-103        | TEST-T-100             | NO                       |
| REQ-AWM-100        | TEST-T-101             | NO                       |
| REQ-AWM-101        | TEST-T-100, TEST-T-101 | NO                       |
| REQ-AWM-102        | TEST-T-100, TEST-T-101 | NO                       |
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
| NO                                           | Under development    |
