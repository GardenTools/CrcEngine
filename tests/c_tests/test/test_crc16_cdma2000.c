#include "unity.h"
#include <string.h>

#include "crc16_cdma2000.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc16_cdma2000(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint16_t result = crc16_cdma2000((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX16(0x4c06, result);
}