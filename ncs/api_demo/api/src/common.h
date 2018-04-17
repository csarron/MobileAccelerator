/*
* Copyright 2017 Intel Corporation.
* The source code, information and material ("Material") contained herein is
* owned by Intel Corporation or its suppliers or licensors, and title to such
* Material remains with Intel Corporation or its suppliers or licensors.
* The Material contains proprietary information of Intel or its suppliers and
* licensors. The Material is protected by worldwide copyright laws and treaty
* provisions.
* No part of the Material may be used, copied, reproduced, modified, published,
* uploaded, posted, transmitted, distributed or disclosed in any way without
* Intel's prior express written permission. No license under any patent,
* copyright or other intellectual property rights in the Material is granted to
* or conferred upon you, either expressly, by implication, inducement, estoppel
* or otherwise.
* Any license under such intellectual property rights must be express and
* approved by Intel in writing.
*/

// Common logging macros

#ifndef _COMMON_H_
#define _COMMON_H_

#       ifdef ANDROID
#           define ANSI_BOLD   ""
#           define ANSI_RED     ""
#           define ANSI_RED_B    ""
#           define ANSI_GREEN   ""
#           define ANSI_YELLOW  ""
#           define ANSI_BLUE    ""
#           define ANSI_BLUE_B    ""
#           define ANSI_MAGENTA ""
#           define ANSI_CYAN    ""
#           define ANSI_RESET   ""
// LOGS ANDROID
#           include <android/log.h>

#           define LOG_TAG "mvnc_api"
#           define LOGD(...) {if (mvnc_loglevel >= 2) {__android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__);}}
#           define LOGI(...) {if (mvnc_loglevel >= 1) {__android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__);}}
#           define LOGW(...) {if (mvnc_loglevel >= 0) {__android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__);}}
#           define LOGE(...) {if (mvnc_loglevel >= 0) {__android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__);}}
#       else
#           define ANSI_BOLD   "\033[1m"
#           define ANSI_RED     "\033[31m"
#           define ANSI_RED_B    "\033[31m\033[1m"
#           define ANSI_GREEN   "\033[32m"
#           define ANSI_YELLOW  "\033[33m"
#           define ANSI_BLUE    "\033[34m"
#           define ANSI_BLUE_B    "\033[34m\033[1m"
#           define ANSI_MAGENTA "\033[35m"
#           define ANSI_CYAN    "\033[36m"
#           define ANSI_RESET   "\033[0m"
// LOGS NO ANDROID
#           include <stdio.h>
#           define LOGD(...) {if (mvnc_loglevel >= 2) {printf(ANSI_BLUE "DEBUG:" ANSI_BLUE_B);printf(__VA_ARGS__);printf("" ANSI_RESET);}}
#           define LOGI(...) {if (mvnc_loglevel >= 1) {printf(ANSI_CYAN "");printf(__VA_ARGS__);printf("" ANSI_RESET);}}
#           define LOGW(...) {if (mvnc_loglevel >= 0) {printf(ANSI_MAGENTA "* Warning: " ANSI_BOLD);printf(__VA_ARGS__);printf("" ANSI_RESET);}}
#           define LOGE(...) {if (mvnc_loglevel >= 0) {printf(ANSI_RED "*** Error: " ANSI_RED_B);printf(__VA_ARGS__);printf("" ANSI_RESET);}}
#       endif // ANDROID

// Common defines
#define DEFAULT_VID                0x03E7
#define DEFAULT_PID                0x2150    // Myriad2v2 ROM
#define DEFAULT_OPEN_VID            DEFAULT_VID
#define DEFAULT_OPEN_PID            0xf63b    // Once opened in VSC mode, VID/PID change
#endif
