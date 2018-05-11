//==============================================================================
//
//  @@-COPYRIGHT-START-@@
//
//  Copyright 2015-2016 Qualcomm Technologies, Inc. All rights reserved.
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

#ifndef _SNPE_FACTORY_HPP_
#define _SNPE_FACTORY_HPP_

#include "SNPE/SNPE.hpp"
#include "DlSystem/DlEnums.hpp"
#include "DlSystem/UDLFunc.hpp"
#include "DlSystem/ZdlExportDefine.hpp"
#include "DlSystem/DlOptional.hpp"

namespace zdl {
   namespace DlSystem
   {
      class ITensorFactory;
      class IUserBufferFactory;
   }
   namespace DlContainer
   {
      class IDlContainer;
   }
}



namespace zdl { namespace SNPE {
/** @addtogroup c_plus_plus_apis C++
@{ */

/**
 * The factory class for creating SNPE objects.
 *
 */
class ZDL_EXPORT SNPEFactory
{
public:

   /**
    * Indicates whether the supplied runtime is available on the 
    * current platform.
    * 
    * @param[in] runtime The target runtime to check.
    *    
    * @return True if the supplied runtime is available; false, 
    *         otherwise.
    */
   static bool isRuntimeAvailable(zdl::DlSystem::Runtime_t runtime);

   /**
    * Gets a reference to the tensor factory.
    * 
    * @return A reference to the tensor factory.
    */
   static zdl::DlSystem::ITensorFactory& getTensorFactory();

   /**
    * Gets a reference to the UserBuffer factory.
    *
    * @return A reference to the UserBuffer factory.
    */
   static zdl::DlSystem::IUserBufferFactory& getUserBufferFactory();

   /**
    * Gets the version of the SNPE library.
    *
    * @return Version of the SNPE library.
    *
    */
   static zdl::DlSystem::Version_t getLibraryVersion();

   /**
    * Set the SNPE storage location for all SNPE instances in this
    * process. Note that this may only be called once, and if so
    * must be called before creating any SNPE instances.
    *
    * @param[in] storagePath Absolute path to a directory which SNPE may
    *  use for caching and other storage purposes.
    *
    * @return True if the supplied path was succesfully set as
    *  the SNPE storage location, false otherwise.
    */
   static bool setSNPEStorageLocation(const char* storagePath);
};

/** @} */ /* end_addtogroup c_plus_plus_apis C++ */
}}


#endif
