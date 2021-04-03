#include "unity.h"
#include <string.h>

#include "crc64_ecma.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc64_ecma(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint64_t result = crc64_ecma((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX64(0x6c40df5f0b497347, result);
}