#include "unity.h"
#include <string.h>

#include "crc24_flexray16_b.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc24_flexray16_b(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint32_t result = crc24_flexray16_b((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX32(0x1f23b8, result);
}