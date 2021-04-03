#include "unity.h"
#include <string.h>

#include "crc15_can.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc15_can(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint16_t result = crc15_can((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX16(0x59e, result);
}