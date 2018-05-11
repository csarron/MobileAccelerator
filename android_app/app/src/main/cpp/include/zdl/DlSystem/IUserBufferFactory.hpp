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

#ifndef _IUSERBUFFER_FACTORY_HPP
#define _IUSERBUFFER_FACTORY_HPP

#include "IUserBuffer.hpp"
#include "TensorShape.hpp"
#include "ZdlExportDefine.hpp"

namespace zdl {
    namespace DlSystem {
        class IUserBuffer;

        class TensorShape;
    }
}

namespace zdl {
namespace DlSystem {

/** @addtogroup c_plus_plus_apis C++
@{ */

/**
* Factory interface class to create IUserBuffer objects.
*/
class ZDL_EXPORT IUserBufferFactory {
public:
    virtual ~IUserBufferFactory() = default;

    /**
     * @brief Creates a UserBuffer
     *
     * @param[in] buffer Pointer to the buffer that the caller supplies
     *
     * @param[in] bufSize Buffer size, in bytes
     *
     * @param[in] strides Total number of bytes between elements in each dimension.
     *          E.g. A tightly packed tensor of floats with dimensions [4, 3, 2] would have strides of [24, 8, 4].
     *
     * @param[in] userBufferEncoding Reference to an UserBufferEncoding object
     *
     * @note Caller has to ensure that memory pointed to by buffer stays accessible
     *       for the lifetime of the object created
     */
    virtual std::unique_ptr<IUserBuffer>
    createUserBuffer(void *buffer, size_t bufSize, const zdl::DlSystem::TensorShape &strides, zdl::DlSystem::UserBufferEncoding* userBufferEncoding) noexcept = 0;

};
/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

}
}


#endif
