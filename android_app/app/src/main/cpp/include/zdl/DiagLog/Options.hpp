//=============================================================================
//  @@-COPYRIGHT-START-@@
//
//  Copyright 2015 Qualcomm Technologies, Inc. All rights reserved.
//  Confidential & Proprietary - Qualcomm Technologies, Inc. ("QTI")
//
//  The party receiving this software directly from QTI (the "Recipient")
//  may use this software as reasonably necessary solely for the purposes
//  set forth in the agreement between the Recipient and QTI (the
//  "Agreement"). The software may be used in source code form solely by
//  the Recipient's employees (if any) authorized by the Agreement. Unless
//  expressly authorized in the Agreement, the Recipient may not sublicense,
//  assign, transfer or otherwise provide the source code to any third
//  party. Qualcomm Technologies, Inc. retains all ownership rights in and
//  to the software
//
//  This notice supersedes any other QTI notices contained within the software
//  except copyright notices indicating different years of publication for
//  different portions of the software. This notice does not supersede the
//  application of any third party copyright notice to that third party's
//  code.
//
//  @@-COPYRIGHT-END-@@
//=============================================================================
#ifndef __DIAGLOG_OPTIONS_HPP_
#define __DIAGLOG_OPTIONS_HPP_

#ifndef ZDL_LOGGING_EXPORT
#define ZDL_LOGGING_EXPORT __attribute__((visibility("default")))
#endif

#include <string>
#include <set>

namespace zdl
{
namespace DiagLog
{
/** @addtogroup c_plus_plus_apis C++
@{ */

/// @brief .
///
/// Options for setting up diagnostic logging for zdl components.
class ZDL_LOGGING_EXPORT Options
{
public:
   Options() :
      DiagLogMask(""),
      LogFileDirectory("diaglogs"),
      LogFileName("DiagLog"),
      LogFileRotateCount(20)
   {
      // Solves the empty string problem with multiple std libs
      DiagLogMask.reserve(1);
   }

   /// @brief .
   /// 
   /// Enables diag logging only on the specified area mask (DNN_RUNTIME=ON | OFF)
   std::string DiagLogMask;

   /// @brief .
   /// 
   /// The path to the directory where log files will be written.
   /// The path may be relative or absolute. Relative paths are interpreted
   /// from the current working directory.
   /// Default value is "diaglogs"
   std::string LogFileDirectory;

   /// @brief .
   /// 
   //// The name used for log files. If this value is empty then BaseName will be
   /// used as the default file name.
   /// Default value is "DiagLog"
   std::string LogFileName;

   /// @brief .
   /// 
   /// The maximum number of log files to create. If set to 0 no log rotation 
   /// will be used and the log file name specified will be used each time, overwriting
   /// any existing log file that may exist.
   /// Default value is 20
   uint32_t LogFileRotateCount;
};
/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

} // DiagLog namespace
} // zdl namespace


#endif
