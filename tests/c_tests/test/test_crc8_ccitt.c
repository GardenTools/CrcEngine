#include "unity.h"
#include <string.h>

#include "crc8_ccitt.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc8_ccitt(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint8_t result = crc8_ccitt((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX8(0xa1, result);
}