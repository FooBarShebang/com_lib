# Entire Library Requirements and Tests Traceability List

## Relation between modules, classes and the requirements and tests indexing

* entire library - 00x
* module *mock_serial* - 1xx
* module *serial_port_com* - 2xx
* module *serialization* - 3xx

## Requirements vs Tests Traceability

| **Requirement ID** | **Covered in test(s)** | **Verified \[YES/NO\]**) |
| :----------------- | :--------------------- | :----------------------- |
| REQ-FUN-000        | TEST-A-000             | YES                      |
| REQ-FUN-001        | TEST-A-000             | YES                      |
| REQ-FUN-002        | TEST-A-001             | YES                      |
| REQ-INT-000        | TEST-I-000             | YES                      |
| REQ-IAR-000        | TEST-D-000             | YES                      |
| REQ-IAR-001        | TEST-D-001             | YES                      |
| REQ-IAR-002        | TEST-D-000             | YES                      |
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
| REQ-FUN-200        | TEST-A-200             | YES                      |
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
| REQ-FUN-228        | TEST-T-224             | YES                      |
| REQ-AWM-220        | TEST-T-225             | YES                      |
| REQ-AWM-221        | TEST-T-226             | YES                      |
| REQ-AWM-222        | TEST-T-223             | YES                      |
| REQ-AWM-223        | TEST-T-227             | YES                      |
| REQ-AWM-224        | TEST-T-228             | YES                      |
| REQ-FUN-300        | TEST-A-300             | YES                      |
| REQ-FUN-301        | TEST-A-300             | YES                      |
| REQ-FUN-302        | TEST-T-300             | YES                      |
| REQ-FUN-303        | TEST-T-309             | YES                      |
| REQ-FUN-310        | TEST-T-310             | YES                      |
| REQ-FUN-311        | TEST-T-311             | YES                      |
| REQ-FUN-320        | TEST-T-305, TEST-T-320 | YES                      |
| REQ-FUN-321        | TEST-T-321             | YES                      |
| REQ-FUN-322        | TEST-T-322             | YES                      |
| REQ-FUN-323        | TEST-T-309             | YES                      |
| REQ-FUN-324        | TEST-T-309             | YES                      |
| REQ-FUN-325        | TEST-T-323             | YES                      |
| REQ-FUN-326        | TEST-T-324             | YES                      |
| REQ-FUN-327        | TEST-T-321             | YES                      |
| REQ-FUN-328        | TEST-T-320             | YES                      |
| REQ-FUN-330        | TEST-T-305, TEST-T-330 | YES                      |
| REQ-FUN-331        | TEST-T-331             | YES                      |
| REQ-FUN-332        | TEST-T-332             | YES                      |
| REQ-FUN-333        | TEST-T-309             | YES                      |
| REQ-FUN-334        | TEST-T-309             | YES                      |
| REQ-FUN-335        | TEST-T-333             | YES                      |
| REQ-FUN-336        | TEST-T-334             | YES                      |
| REQ-FUN-337        | TEST-T-331             | YES                      |
| REQ-FUN-338        | TEST-T-330             | YES                      |
| REQ-FUN-340        | TEST-T-305, TEST-T-340 | YES                      |
| REQ-FUN-341        | TEST-T-341             | YES                      |
| REQ-FUN-342        | TEST-T-342             | YES                      |
| REQ-FUN-343        | TEST-T-309             | YES                      |
| REQ-FUN-344        | TEST-T-309             | YES                      |
| REQ-FUN-345        | TEST-T-343             | YES                      |
| REQ-FUN-346        | TEST-T-344             | YES                      |
| REQ-FUN-347        | TEST-T-341             | YES                      |
| REQ-FUN-348        | TEST-T-340             | YES                      |
| REQ-AWM-300        | TEST-T-305             | YES                      |
| REQ-AWM-301        | TEST-T-304             | YES                      |
| REQ-AWM-302        | TEST-T-308             | YES                      |
| REQ-AWM-303        | TEST-T-302             | YES                      |
| REQ-AWM-304        | TEST-T-303             | YES                      |
| REQ-AWM-305        | TEST-T-301             | YES                      |
| REQ-AWM-306        | TEST-T-306             | YES                      |
| REQ-AWM-307        | TEST-T-307             | YES                      |

| **Software ready for production \[YES/NO\]** | **Rationale**        |
| :------------------------------------------: | :------------------- |
| NO                                           | Under development    |
