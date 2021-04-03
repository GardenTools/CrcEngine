#include "unity.h"
#include <string.h>

#include "crc32_c.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc32_c(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint32_t result = crc32_c((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX32(0xe3069283, result);
}