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
#ifndef __IDIAGLOG_HPP_
#define __IDIAGLOG_HPP_

#ifndef ZDL_LOGGING_EXPORT
#define ZDL_LOGGING_EXPORT __attribute__((visibility("default")))
#endif

#include <string>

#include "DiagLog/Options.hpp"
#include "DlSystem/String.hpp"

namespace zdl
{
namespace DiagLog
{

/** @addtogroup c_plus_plus_apis C++
@{ */

/// @brief .
/// 
/// Interface for controlling logging for zdl components.

class ZDL_LOGGING_EXPORT IDiagLog
{
public:

   /// @brief .
   ///
   /// Sets the options after initialization occurs.
   ///
   /// @param[in] loggingOptions The options to set up diagnostic logging.
   ///
   /// @return False if the options could not be set. Ensure logging is not started.
   virtual bool setOptions(const Options& loggingOptions) = 0;

   /// @brief .
   ///
   /// Gets the curent options for the diag logger.
   ///
   /// @return Diag log options object.
   virtual Options getOptions() = 0;
   
   /// @brief .
   ///
   /// Allows for setting the log mask once diag logging has started
   ///
   /// @return True if the level was set successfully, false if a failure occurred.
   virtual bool setDiagLogMask(const std::string& mask) = 0;

   /// @brief .
   ///
   /// Allows for setting the log mask once diag logging has started
   ///
   /// @return True if the level was set successfully, false if a failure occurred.
   virtual bool setDiagLogMask(const zdl::DlSystem::String& mask) = 0;

   /// @brief .
   ///
   /// Enables logging for zdl components.
   ///
   /// Logging should be started prior to the instantiation of zdl components
   /// to ensure all events are captured.
   ///
   /// @return False if diagnostic logging could not be started.
   virtual bool start(void) = 0;

   /// @brief Disables logging for zdl components.
   virtual bool stop(void) = 0;

   virtual ~IDiagLog() {};
};

} // DiagLog namespace
} // zdl namespace

/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

#endif
