//==============================================================================
//
//  @@-COPYRIGHT-START-@@
//
//  Copyright 2014-2015 Qualcomm Technologies, Inc. All rights reserved.
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
//
//==============================================================================


#ifndef _DL_VERSION_HPP_
#define _DL_VERSION_HPP_

#include "ZdlExportDefine.hpp"
#include <stdint.h>
#include <string>
#include "DlSystem/String.hpp"


namespace zdl {
namespace DlSystem
{
   class Version_t;
}}


namespace zdl { namespace DlSystem
{
/** @addtogroup c_plus_plus_apis C++
@{ */

/**
 * A class that contains the different portions of a version number.
 */
class ZDL_EXPORT Version_t
{
public:
   /// Holds the major version number. Changes in this value indicate
   /// major changes that break backward compatibility.
   int32_t         Major;

   /// Holds the minor version number. Changes in this value indicate
   /// minor changes made to library that are backwards compatible
   /// (such as additions to the interface).
   int32_t         Minor;

   /// Holds the teeny version number. Changes in this value indicate
   /// changes such as bug fixes and patches made to the library that
   /// do not affect the interface.
   int32_t         Teeny;

   /// This string holds information about the build version.
   ///
   std::string     Build;

   static zdl::DlSystem::Version_t fromString(const std::string &stringValue);

   static zdl::DlSystem::Version_t fromString(const zdl::DlSystem::String &stringValue);

   /**
    * @brief Returns a string in the form Major.Minor.Teeny.Build
    *
    * @return A formatted string holding the version information.
    */
   const std::string toString() const;

   /**
    * @brief Returns a string in the form Major.Minor.Teeny.Build
    *
    * @return A formatted string holding the version information.
    */
   const zdl::DlSystem::String asString() const;
};

}}

/** @} */ /* end_addtogroup c_plus_plus_apis */

#endif
