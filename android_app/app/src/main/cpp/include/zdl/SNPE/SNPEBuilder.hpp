//==============================================================================
//
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
//
//==============================================================================

#ifndef _SNPE_BUILDER_HPP_
#define _SNPE_BUILDER_HPP_

#include "SNPE/SNPE.hpp"
#include "DlSystem/DlEnums.hpp"
#include "DlSystem/UDLFunc.hpp"
#include "DlSystem/DlOptional.hpp"
#include "DlSystem/TensorShapeMap.hpp"

namespace zdl {
   namespace DlContainer
   {
      class IDlContainer;
   }
}

struct SNPEBuilderImpl;


namespace zdl { namespace SNPE {
/** @addtogroup c_plus_plus_apis C++
@{ */

/**
 * The builder class for creating SNPE objects.
 * Not meant to be extended.
 */
class ZDL_EXPORT SNPEBuilder final
{
private:
   std::unique_ptr<::SNPEBuilderImpl> m_Impl;
public:

   /**
    * @brief Constructor of NeuralNetwork Builder with a supplied model.
    *
    * @param[in] container A container holding the model.
    *
    * @return A new instance of a SNPEBuilder object
    *         that can be used to configure and build
    *         an instance of SNPE.
    *
    */
   explicit SNPEBuilder(
      zdl::DlContainer::IDlContainer* container);
   ~SNPEBuilder();

   /**
    * @brief Sets the runtime processor.
    *
    * @param[in] targetRuntimeProcessor The target runtime.
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setRuntimeProcessor(
      zdl::DlSystem::Runtime_t targetRuntimeProcessor);

   /**
    * @brief Requests a performance profile.
    *
    * @param[in] targetRuntimeProfile The target performance profile.
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setPerformanceProfile(
      zdl::DlSystem::PerformanceProfile_t performanceProfile);

    /**
     * @brief Sets a preference for execution priority.
     *
     * This allows the caller to give coarse hint to SNPE runtime
     * about the priority of the network.  SNPE runtime is free to use
     * this information to co-ordinate between different workloads
     * that may or may not extend beyond SNPE.
     *
     * @param[in] ExecutionPriorityHint_t The target performance profile.
     *
     * @return The current instance of SNPEBuilder.
     */
   SNPEBuilder& setExecutionPriorityHint(
            zdl::DlSystem::ExecutionPriorityHint_t priority);

    /**
    * @brief Sets the layers that will generate output.
    *
    * @param[in] outputLayerNames List of layer names to
    *                             output. An empty list will
    *                             result in only the final
    *                             layer of the model being
    *                             the output layer.  The list
    *                             will be copied.
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setOutputLayers(
      const zdl::DlSystem::StringList& outputLayerNames);

   /**
    * @brief Passes in a User-defined layer.
    *
    * @param udlBundle Bundle of udl factory function and a cookie
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setUdlBundle(
      zdl::DlSystem::UDLBundle udlBundle);

   /**
    * @brief Sets whether this neural network will perform inference with
    *        input from user-supplied buffers, and write output to user-supplied
    *        buffers.  Default behaviour is to use tensors created by
    *        ITensorFactory.
    *
    * @param[in] bufferMode Whether to use user-supplied buffer or not.
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setUseUserSuppliedBuffers(
      bool bufferMode);

    /**
    * @brief Sets the debug mode of the runtime.
    *
    * @param[in] debugMode This enables debug mode for the runtime. It
    *                      does two things. For an empty
    *                      outputLayerNames list, all layers will be
    *                      output. It might also disable some internal
    *                      runtime optimizations (e.g., some networks
    *                      might be optimized by combining layers,
    *                      etc.).
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setDebugMode(
      bool debugMode);

   /**
    * @brief Sets the mode of CPU fallback functionality.
    *
    * @param[in] mode   This flag enables/disables the functionality
    *                   of CPU fallback. When the CPU fallback
    *                   functionality is enabled, layers in model that
    *                   violates runtime constraints will run on CPU
    *                   while the rest of non-violating layers will
    *                   run on the chosen runtime processor. In
    *                   disabled mode, models with layers violating
    *                   runtime constraints will NOT run on the chosen
    *                   runtime processor and will result in runtime
    *                   exception. By default, the functionality is
    *                   enabled.
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setCPUFallbackMode(
      bool mode);


   /**
    * @brief Sets network's input dimensions to enable resizing of dimensions
    *        each layer of fully convolution networks.
    *
    * @param[in] tensorShapeMap The map of input names and their new dimensions.
    *                           This new dimensions overwrite the input dimensions
    *                           embedded in model and then resize each and every layer
    &                           of model. If the model happens to contain
    *                           layers whose  dimensions can't be resized e.g fc,
    *                           exception will be thrown when SNPE instance is actually built.
    *                           After resizing of layers' dimensions in model based
    *                           on new input dimensions, the new model is revalidated
    *                           against all runtime constraints, whose failures may
    *                           result in cpu fallback situation.
    *
    * @return The current instance of SNPEBuilder.
    */
   SNPEBuilder& setInputDimensions(const zdl::DlSystem::TensorShapeMap& inputDimensionsMap);

   /**
    * @brief Returns an instance of SNPE based on the current parameters.
    *
    * @return A new instance of a SNPE object that can be used
    *         to execute models or null if any errors occur.
    */
   std::unique_ptr<SNPE> build() noexcept;

};
/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

}}

#endif
