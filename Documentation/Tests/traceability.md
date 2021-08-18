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
| REQ-FUN-100        | TEST-A-100             | YES                      |
| REQ-FUN-110        | TEST-T-110             | YES                      |
| REQ-FUN-120        | TEST-T-120             | YES                      |
| REQ-FUN-121        | TEST-T-121             | YES                      |
| REQ-FUN-122        | TEST-T-12A             | YES                      |
| REQ-FUN-123        | TEST-T-12A             | YES                      |
| REQ-FUN-124        | TEST-T-12A             | YES                      |
| REQ-FUN-125        | TEST-T-12A             | YES                      |
| REQ-FUN-126        | TEST-T-12B             | YES                      |
| REQ-AWM-120        | TEST-T-122             | YES                      |
| REQ-AWM-121        | TEST-T-123             | YES                      |
| REQ-AWM-122        | TEST-T-124             | YES                      |
| REQ-AWM-123        | TEST-T-125             | YES                      |
| REQ-AWM-124        | TEST-T-126             | YES                      |
| REQ-AWM-125        | TEST-T-127             | YES                      |
| REQ-AWM-126        | TEST-T-128             | YES                      |
| REQ-AWM-127        | TEST-T-129             | YES                      |
| REQ-AWM-128        | TEST-T-12A             | YES                      |
| REQ-FUN-200        | TEST-A-200             | NO                       |
| REQ-FUN-201        | TEST-A-201             | YES                      |
| REQ-FUN-210        | TEST-T-210             | YES                      |
| REQ-FUN-220        | TEST-T-220             | YES                      |
| REQ-FUN-221        | TEST-T-221             | YES                      |
| REQ-FUN-222        | TEST-T-221, TEST-T-223 | YES                      |
| REQ-FUN-223        | TEST-T-221             | YES                      |
| REQ-FUN-224        | TEST-T-222             | YES                      |
| REQ-FUN-225        | TEST-T-222             | YES                      |
| REQ-FUN-226        | TEST-T-223             | YES                      |
| REQ-FUN-227        | TEST-T-220             | YES                      |
| REQ-FUN-228        | TEST-T-224             | NO                       |
| REQ-AWM-220        | TEST-T-225             | YES                      |
| REQ-AWM-221        | TEST-T-226             | YES                      |
| REQ-AWM-222        | TEST-T-223             | YES                      |
| REQ-AWM-223        | TEST-T-227             | NO                       |
| REQ-AWM-224        | TEST-T-228             | NO                       |

| **Software ready for production \[YES/NO\]** | **Rationale**        |
| :------------------------------------------: | :------------------- |
| NO                                           | Under development    |
