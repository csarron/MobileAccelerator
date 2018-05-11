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
#include <initializer_list>
#include <cstdio>
#include <memory>
#include <vector>
#include "ZdlExportDefine.hpp"
#include "DlSystem/TensorShape.hpp"
#include "DlSystem/StringList.hpp"

#ifndef DL_SYSTEM_TENSOR_SHAPE_MAP_HPP
#define DL_SYSTEM_TENSOR_SHAPE_MAP_HPP

namespace DlSystem
{
   // Forward declaration of tensor shape map implementation.
   class TensorShapeMapImpl;
}

namespace zdl
{
namespace DlSystem
{

/** @addtogroup c_plus_plus_apis C++
@{ */

/**
  * @brief .
  *
  * A class representing the map of names and tensorshapes.
  */
class ZDL_EXPORT TensorShapeMap final
{
public:

    /**
    * @brief .
    *
    * Creates a new tensor shape map
    *
    */
   TensorShapeMap();

   /**
   * @brief .
   *
   * copy constructor.
   * @param[in] other object to copy.
   */
   TensorShapeMap(const TensorShapeMap& other);

   /**
    * @brief .
    *
    * assignment operator.
    */
   TensorShapeMap& operator=(const TensorShapeMap& other);

   /**
    * @brief Adds a name and the corresponding tensor pointer
    *        to the map
    *
    * @param[in] name The name of the tensor
    * @param[out] tensor The pointer to the tensor
    *
    * @note If a tensor with the same name already exists, no new
    *       tensor is added.
    */
   void add(const char *name, const zdl::DlSystem::TensorShape& tensorShape);

   /**
    * @brief Removes a mapping of tensor and its name by its name
    *
    * @param[in] name The name of tensor to be removed
    *
    * @note If no tensor with the specified name is found, nothing
    *       is done.
    */
   void remove(const char *name) noexcept;

   /**
    * @brief Returns the number of tensors in the map
    */
   size_t size() const noexcept;

   /**
    * @brief .
    *
    * Removes all tensors from the map
    */
   void clear() noexcept;

   /**
    * @brief Returns the tensor given its name.
    *
    * @param[in] name The name of the tensor to get.
    *
    * @return nullptr if no tensor with the specified name is
    *         found; otherwise, a valid pointer to the tensor.
    */
   zdl::DlSystem::TensorShape getTensorShape(const char *name) const noexcept;

   /**
    * @brief .
    *
    * Returns the names of all tensor shapes
    */
   zdl::DlSystem::StringList getTensorShapeNames() const;

   ~TensorShapeMap();
private:
   void swap(const TensorShapeMap &other);
   std::unique_ptr<::DlSystem::TensorShapeMapImpl> m_TensorShapeMapImpl;
};

} // DlSystem namespace
} // zdl namespace

/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

#endif // DL_SYSTEM_TENSOR_SHAPE_MAP_HPP

