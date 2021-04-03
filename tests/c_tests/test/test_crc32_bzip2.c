#include "unity.h"
#include <string.h>

#include "crc32_bzip2.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_crc32_bzip2(void)
{
  const char* check_string = "123456789";
  size_t check_length = strlen(check_string);
  uint32_t result = crc32_bzip2((const uint8_t*)check_string, check_length);
  TEST_ASSERT_EQUAL_HEX32(0xfc891918, result);
}