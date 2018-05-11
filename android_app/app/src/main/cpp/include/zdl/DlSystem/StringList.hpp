//=============================================================================
//  @@-COPYRIGHT-START-@@
//
//  Copyright 2016 Qualcomm Technologies, Inc. All rights reserved.
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
#include <cstdio>
#include "ZdlExportDefine.hpp"

#ifndef DL_SYSTEM_STRINGLIST_HPP
#define DL_SYSTEM_STRINGLIST_HPP

namespace zdl
{
namespace DlSystem
{
/** @addtogroup c_plus_plus_apis C++
@{ */

/**
 * @brief .
 *
 * Class for holding an order list of null-terminated ASCII strings.
 */
class ZDL_EXPORT StringList final
{
public:
   StringList() {}

   /**
    * Construct a string list with some pre-allocated memory.
    * @warning Contents of the list will be uninitialized
    * @param[in] length Number of elements for which to pre-allocate space.
    */
   explicit StringList(size_t length);

   /**
    * Append a string to the list.
    * @param[in] str Null-terminated ASCII string to append to the list.
    */
   void append(const char* str);

   /**
    * Returns the string at the indicated position,
    *  or an empty string if the positions is greater than the size
    *  of the list.
    * @param[in] idx Position in the list of the desired string
    */
   const char* at(size_t idx) const noexcept;

   /**
    * Pointer to the first string in the list.
    *  Can be used to iterate through the list.
    */
   const char** begin() const noexcept;

   /**
    * Pointer to one after the last string in the list.
    *  Can be used to iterate through the list.
    */
   const char** end() const noexcept;

   /**
    * Return the number of valid string pointers held by this list.
    */
   size_t size() const noexcept;


   /**
    * assignment operator. 
    */
   StringList& operator=(const StringList&) noexcept;

   /**
    * copy constructor.
    * @param[in] other object to copy.
    */
   StringList(const StringList& other);

   /**
    * move constructor.
    * @param[in] other object to move.    
    */
   StringList(StringList&& other) noexcept;

   ~StringList();
private:
   void copy(const StringList& other);

   void resize(size_t length);

   void clear();

   static const char* s_Empty;
   const char** m_Strings = nullptr;
   const char** m_End = nullptr;
   size_t       m_Size = 0;
};

} // DlSystem namespace
} // zdl namespace

/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

#endif // DL_SYSTEM_STRINGLIST_HPP

