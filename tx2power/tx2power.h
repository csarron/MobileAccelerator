/**
 * @file tx2power.h
 * @author cs
 * @brief This header file contains a declaration of the function 
 * for accessing on-board and on-module INA3221's values together 
 * with enumerated types.
 */
#ifndef TX2POWER_H_
#define TX2POWER_H_
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>    
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <linux/i2c-dev.h>
#include <byteswap.h>
#define MAX_BUFF 128

/**
 * @brief Enumeration indexing each INA3221's input.
 */
typedef enum tx2_rails {
    VDD_IN = 0,
    VDD_SYS_CPU,
    VDD_SYS_SRAM,
    VDD_SYS_GPU,
    VDD_SYS_SOC,
    VDD_4V0_WIFI
} tx2_rail;

/**
 * @brief Enumeration indexing each type of measurement.
 */
typedef enum tx2_rail_types {
    VOLTAGE = 0, ///< Voltage given in milli-volts or mV
    POWER, ///< Power given in milli-watts or mW
    CURRENT ///< Power given in milli-amps mA
} tx2_rail_type;

/**
 * @brief Read INA3221's values from 0x42 and 0x43 addresses using sysfs files
 * 
 * Use sysf files to access on-board INA3221 sensor 
 * and read power, current, and voltage information.
 *
 * @param rail Indexed by ::jtx1_rail
 * @param measure Either VOLTAGE, POWER or CURRENT. See ::jtx1pow_ina3321_measure
 * @param *val Output's reference
 */
static void tx2_get_ina3221(tx2_rail rail,
                  tx2_rail_type measure,
                  unsigned int *val)
{
    
  if (rail < 0 || rail > 6) {
    printf("type not supported: %s\n", rail);
    exit(-1);
  }
  FILE *fp;
  int addr;
  int ans;
  char buff[MAX_BUFF];
  char *mea = "voltage";
    
  if (rail >= 0 && rail <= 2) {
    addr = 1;
  } else {
    addr = 0;
  }

  switch (measure) {
  case 0: {
    mea = "voltage";
    break;
  }
  case 1: {
    mea = "power";
    break;
  }
  case 2: {
    mea = "current";
    break;
  }
  default:
    break;
  }

  snprintf(buff, sizeof(buff),
       "/sys/bus/i2c/devices/0-004%d/iio_device/in_%s%d_input",
       addr, mea, rail % 2);

  fp = fopen(buff, "r");

  if (fp == NULL) {
    fprintf(stderr, "Error opening file: %s\n", strerror(errno));
    exit(EXIT_FAILURE);
  } else if (!fscanf(fp, "%d", &ans)) {
    fprintf(stderr, "Error scanning the file: %s\n", strerror(errno));
    exit(EXIT_FAILURE);
  } else {
    fclose(fp);
  }

  *val = ans;

}


#endif // TX2POWER_H_
