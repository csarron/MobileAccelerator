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

#ifndef _ITENSOR_ITR_IMPL_HPP_
#define _ITENSOR_ITR_IMPL_HPP_

#include "ZdlExportDefine.hpp"

#include <memory>
#include <iterator>
#include <vector>

namespace DlSystem
{
   class ITensorItrImpl;
}

class ZDL_EXPORT DlSystem::ITensorItrImpl
{
public:
   ITensorItrImpl() {}
   virtual ~ITensorItrImpl() {}

   virtual float getValue() const = 0;
   virtual float& getReference() = 0;
   virtual float& getReferenceAt(size_t idx) = 0;
   virtual float* dataPointer() const = 0;
   virtual void increment(int incVal = 1) = 0;
   virtual void decrement(int decVal = 1) = 0;
   virtual size_t getPosition() = 0;
   virtual std::unique_ptr<DlSystem::ITensorItrImpl> clone() = 0;

private:
   ITensorItrImpl& operator=(const ITensorItrImpl& other) = delete;
   ITensorItrImpl(const ITensorItrImpl& other) = delete;
};

#endif
