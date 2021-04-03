#include "unity.h"
#include <string.h>

#include "crc8_autosar.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc8_autosar(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint8_t result = crc8_autosar((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX8(0xdf, result);
}