//
// @@-COPYRIGHT-START-@@
//
// Copyright 2017 Qualcomm Technologies, Inc. All rights reserved.
// Confidential & Proprietary - Qualcomm Technologies, Inc. ("QTI")
//
// The party receiving this software directly from QTI (the "Recipient")
// may use this software as reasonably necessary solely for the purposes
// set forth in the agreement between the Recipient and QTI (the
// "Agreement"). The software may be used in source code form solely by
// the Recipient's employees (if any) authorized by the Agreement. Unless
// expressly authorized in the Agreement, the Recipient may not sublicense,
// assign, transfer or otherwise provide the source code to any third
// party. Qualcomm Technologies, Inc. retains all ownership rights in and
// to the software
//
// This notice supersedes any other QTI notices contained within the software
// except copyright notices indicating different years of publication for
// different portions of the software. This notice does not supersede the
// application of any third party copyright notice to that third party's
// code.
//
// @@-COPYRIGHT-END-@@
//
//==============================================================================

#ifndef _IBUFFER_ATTRIBUTES_HPP
#define _IBUFFER_ATTRIBUTES_HPP
#include "IUserBuffer.hpp"
#include "TensorShape.hpp"
#include "ZdlExportDefine.hpp"

namespace zdl {
    namespace DlSystem {
        class UserBufferEncoding;
    }
}

namespace zdl {
namespace DlSystem {


/**
 * @brief IBufferAttributes returns a buffer's dimension and alignment
 *        requirements, along with info on its encoding type
 */
class ZDL_EXPORT IBufferAttributes {
public:

    /**
      * @brief Gets the buffer's element size, in bytes
      *
      * This can be used to compute the memory size required
      * to back this buffer.
      *
      * @return Element size, in bytes
     */
    virtual size_t getElementSize() const noexcept = 0;

    /**
      * @brief Gets the element's encoding type
      *
      * @return encoding type
     */
    virtual zdl::DlSystem::UserBufferEncoding::ElementType_t getEncodingType() const noexcept = 0;

    /**
      * @brief Gets the number of elements in each dimension
      *
      * @return Dimension size, in terms of number of elements
     */
    virtual const TensorShape getDims() const noexcept = 0;

    /**
      * @brief Gets the alignment requirement of each dimension
      *
      * Alignment per each dimension is expressed as an multiple, for
      * example, if one particular dimension can accept multiples of 8,
      * the alignment will be 8.
      *
      * @return Alignment in each dimension, in terms of multiple of
      *         number of elements
     */
    virtual const TensorShape getAlignments() const noexcept = 0;

    virtual ~IBufferAttributes() {}
};



/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

}
}

#endif
