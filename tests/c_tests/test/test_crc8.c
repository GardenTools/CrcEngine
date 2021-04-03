#include "unity.h"
#include <string.h>

#include "crc8.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc8(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint8_t result = crc8((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX8(0xbc, result);
}