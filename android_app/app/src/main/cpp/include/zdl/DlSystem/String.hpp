//=============================================================================
//  @@-COPYRIGHT-START-@@
//
//  Copyright 2017 Qualcomm Technologies, Inc. All rights reserved.
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

#ifndef PLATFORM_STANDARD_STRING_HPP
#define PLATFORM_STANDARD_STRING_HPP

#include <cstdio>
#include <string>
#include <ostream>

#ifndef ZDL_EXPORT
#define ZDL_EXPORT __attribute__((visibility("default")))
#endif

namespace zdl
{
namespace DlSystem
{
/** @addtogroup c_plus_plus_apis C++
@{ */

/**
 * @brief .
 *
 * Class for wrapping char * as a really stripped down std::string replacement.
 */
class ZDL_EXPORT String final
{
public:
   String() = delete;

   /**
    * Construct a string from std::string reference.
    * @param str Reference to a std::string
    */
   explicit String(const std::string& str);

   /**
    * Construct a string from char* reference.
    * @param a char*
    */
   explicit String(const char* str);

   /**
    * move constructor.
    */
   String(String&& other) noexcept;

   /**
    * copy constructor.
    */
   String(const String& other) = delete;

   /**
    * assignment operator.
    */
   String& operator=(const String&) = delete;

   /**
    * move assignment operator.
    */
   String& operator=(String&&) = delete;

   /**
    * class comparators
    */
   bool operator<(const String& rhs) const noexcept;
   bool operator>(const String& rhs) const noexcept;
   bool operator<=(const String& rhs) const noexcept;
   bool operator>=(const String& rhs) const noexcept;
   bool operator==(const String& rhs) const noexcept;
   bool operator!=(const String& rhs) const noexcept;

   /**
    * class comparators against std::string
    */
   bool operator<(const std::string& rhs) const noexcept;
   bool operator>(const std::string& rhs) const noexcept;
   bool operator<=(const std::string& rhs) const noexcept;
   bool operator>=(const std::string& rhs) const noexcept;
   bool operator==(const std::string& rhs) const noexcept;
   bool operator!=(const std::string& rhs) const noexcept;

   const char* c_str() const noexcept;

   ~String();
private:

   char* m_string;
};

/**
 * overloaded << operator
 */
ZDL_EXPORT std::ostream& operator<<(std::ostream& os, const String& str) noexcept;

} // DlSystem namespace
} // zdl namespace

/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

#endif // PLATFORM_STANDARD_STRING_HPP

