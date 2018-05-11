//=============================================================================
//
//  @@-COPYRIGHT-START-@@
//
//  Copyright 2016-2017 Qualcomm Technologies, Inc. All rights reserved.
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
//=============================================================================

#ifndef _DL_SYSTEM_IUDL_HPP_
#define _DL_SYSTEM_IUDL_HPP_

#include "ZdlExportDefine.hpp"

namespace zdl {
namespace DlSystem {
/** @addtogroup c_plus_plus_apis C++
@{ */

/**
 * @brief .
 *
 * Base class user concrete UDL implementation.
 *
 * All functions are marked as:
 *
 * - virtual
 * - noexcept
 *
 * User should make sure no exceptions are propagated outside of
 * their module. Errors can be communicated via return values.
 */
class ZDL_EXPORT IUDL {
public:
   /**
    * @brief .
    *
    * Destructor
    */
   virtual ~IUDL() = default;

   /**
    * @brief Sets up the user's environment.
    * This is called by the SNPE framework to allow the user the
    * opportunity to setup anything which is needed for running
    * user defined layers.
    *
    * @param cookie User provided opaque data returned by the SNPE
    *               runtime
    *
    * @param insz How many elements in input size array
    * @param indim Pointer to a buffer that holds input dimension
    *               array
    * @param indimsz Input dimension size  array of the buffer
    *                 'indim'. Corresponds to indim
    *
    * @param outsz How many elements in output size array
    * @param outdim Pointer to a buffer that holds output
    *              dimension array
    * @param outdimsz Output dimension size of the buffer 'oudim'.
    *                  Corresponds to indim
    *
    * @return true on success, false otherwise
    */
   virtual bool setup(void *cookie,
                      size_t insz, const size_t **indim, const size_t *indimsz,
                      size_t outsz, const size_t **outdim, const size_t *outdimsz)  = 0;

   /**
    * @brief Close the instance. Invoked by the SNPE
    * framework to allow the user the opportunity to release any resources
    * allocated during setup.
    *
    * @param cookie - User provided opaque data returned by the SNPE runtime
    */
   virtual void close(void *cookie) noexcept = 0;

   /**
    * @brief Execute the user defined layer
    *
    * @param cookie User provided opaque data returned by the SNPE 
    *               runtime
    *
    * @param input Const pointer to a float buffer that contains
    *               the input
    *
    * @param output Float pointer to a buffer that would hold
    *                 the user defined layer's output. This buffer
    *                 is allocated and owned by SNPE runtime.
    */
   virtual bool execute(void *cookie, const float **input, float **output)  = 0;
};
/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

} // ns DlSystem

} // ns zdl

#endif // _DL_SYSTEM_IUDL_HPP_
