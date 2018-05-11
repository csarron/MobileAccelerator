#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>
#include <stdlib.h>
#include <stdbool.h>
#include <getopt.h>

#include "tx2power.h"

int main(int argc, char *argv[])
{
    unsigned int val;
    unsigned long rate;

    float convFromMilli = 1;
    char *wunit = "mW";
    char *aunit = "mA";
    char *vunit = "mV";

    tx2_get_ina3221(VDD_IN, POWER, &val);
    printf("[POWER] module power input: %.3f%s\n", convFromMilli * val, wunit);
    tx2_get_ina3221(VDD_SYS_CPU, POWER, &val);
    printf("[POWER] GPU power rail: %.3f%s\n", convFromMilli * val, wunit);
    tx2_get_ina3221(VDD_SYS_GPU, POWER, &val);
    printf("[POWER] CPU power rail: %.3f%s\n", convFromMilli * val, wunit);
    printf("\n");

    tx2_get_ina3221(VDD_IN, CURRENT, &val);
    printf("[CURRENT] module power input: %.3f%s\n", convFromMilli * val, aunit);
    tx2_get_ina3221(VDD_SYS_CPU, CURRENT, &val);
    printf("[CURRENT] GPU power rail: %.3f%s\n", convFromMilli * val, aunit);
    tx2_get_ina3221(VDD_SYS_GPU, CURRENT, &val);
    printf("[CURRENT] CPU power rail: %.3f%s\n", convFromMilli * val, aunit);
    printf("\n");

    tx2_get_ina3221(VDD_IN, VOLTAGE, &val);
    printf("[VOLTAGE] module power input: %.3f%s\n", convFromMilli * val, vunit);
    tx2_get_ina3221(VDD_SYS_CPU, VOLTAGE, &val);
    printf("[VOLTAGE] GPU power rail: %.3f%s\n", convFromMilli * val, vunit);
    tx2_get_ina3221(VDD_SYS_GPU, VOLTAGE, &val);
    printf("[VOLTAGE] CPU power rail: %.3f%s\n", convFromMilli * val, vunit);
    printf("\n");

    return 0;

}
