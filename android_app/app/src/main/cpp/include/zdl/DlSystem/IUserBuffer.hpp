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

#ifndef _IUSER_BUFFER_HPP
#define _IUSER_BUFFER_HPP

#include "TensorShape.hpp"
#include "ZdlExportDefine.hpp"

namespace zdl {
namespace DlSystem {

/** @addtogroup c_plus_plus_apis C++
@{ */


/**
  * @brief .
  *
  * A base class buffer encoding type
  */
class ZDL_EXPORT UserBufferEncoding {
public:

    /**
      * @brief .
      *
      * An enum class of all supported element types in a IUserBuffer
      */
    enum class ElementType_t
    {
        UNKNOWN         = 0,
        FLOAT           = 1,
        UNSIGNED8BIT    = 2,
        TF8             = 10

    };

    /**
      * @brief Retrieves the size of the element, in bytes.
      *
      * @return Size of the element, in bytes.
     */
    virtual size_t getElementSize() const noexcept = 0;

    /**
      * @brief Retrieves the element type
      *
      * @return Element type
     */
    ElementType_t getElementType() const noexcept {return m_ElementType;};

protected:
    UserBufferEncoding(ElementType_t  elementType) : m_ElementType(elementType) {};
private:
    const ElementType_t  m_ElementType;
};

/**
  * @brief .
  *
  * An encoding type where each element is represented by an unsigned int
  */
class ZDL_EXPORT UserBufferEncodingUnsigned8Bit : public UserBufferEncoding {
public:
    UserBufferEncodingUnsigned8Bit() : UserBufferEncoding(ElementType_t::UNSIGNED8BIT) {};
    size_t getElementSize() const noexcept override;

protected:
    UserBufferEncodingUnsigned8Bit(ElementType_t  elementType) : UserBufferEncoding(elementType) {};

};

/**
  * @brief .
  *
  * An encoding type where each element is represented by a float
  */
class ZDL_EXPORT UserBufferEncodingFloat : public UserBufferEncoding {
public:
    UserBufferEncodingFloat() : UserBufferEncoding(ElementType_t::FLOAT) {};
    size_t getElementSize() const noexcept override;

};

/**
  * @brief .
  *
  * An encoding type where each element is represented by tf8, which is an
  * 8-bit quantizd value, which has an exact representation of 0.0
  */
class ZDL_EXPORT UserBufferEncodingTf8 : public UserBufferEncodingUnsigned8Bit {
public:
    UserBufferEncodingTf8() = delete;
    UserBufferEncodingTf8(unsigned char stepFor0, float stepSize) :
            UserBufferEncodingUnsigned8Bit(ElementType_t::TF8),
            m_StepExactly0(stepFor0),
            m_QuantizedStepSize(stepSize) {};

    /**
      * @brief Sets the step value that represents 0
      *
      * @param[in] stepExactly0 The step value that represents 0
      *
     */
    void setStepExactly0(const unsigned char stepExactly0) {
        m_StepExactly0 = stepExactly0;
    }

    /**
      * @brief Sets the float value that each step represents
      *
      * @param[in] quantizedStepSize The float value of each step size
      *
     */
    void setQuantizedStepSize(const float quantizedStepSize) {
        m_QuantizedStepSize = quantizedStepSize;
    }

    /**
      * @brief Retrieves the step that represents 0.0
      *
      * @return Step value
     */
    unsigned char getStepExactly0() const {
        return m_StepExactly0;
    }

    float getMin() const {
        return -(m_StepExactly0 * m_QuantizedStepSize);
    }

    float getMax() const {
        return (m_QuantizedStepSize * 256) + (-m_QuantizedStepSize * m_QuantizedStepSize) - 1;
    }

    /**
      * @brief Retrieves the step size
      *
      * @return Step size
     */
    float getQuantizedStepSize() const {
        return m_QuantizedStepSize;
    }

private:
    unsigned char m_StepExactly0;

    float m_QuantizedStepSize;
};

/**
 * @brief UserBuffer contains a pointer and info on how to walk it and interpret its content.
 */
class ZDL_EXPORT IUserBuffer {
public:
    virtual ~IUserBuffer() = default;
    
    /**
      * @brief Retrieves the total number of bytes between elements in each dimension if
      * the buffer were to be interpreted as a multi-dimensional array.
      *
      * @return Number of bytes between elements in each dimension.
      * e.g. A tightly packed tensor of floats with dimensions [4, 3, 2] would
      * return strides of [24, 8, 4].
     */
    virtual const TensorShape& getStrides() const = 0;

    /**
      * @brief Retrieves the size of the buffer, in bytes.
      *
      * @return Size of the underlying buffer, in bytes.
     */
    virtual size_t getSize() const = 0;

    /**
      * @brief Changes the underlying memory that backs the UserBuffer.
      *
      * This can be used to avoid creating multiple UserBuffer objects
      * when the only thing that differs is the memory location.
      *
      * @param[in] buffer Pointer to the memory location
      *
      * @return Whether the set succeeds.
     */
    virtual bool setBufferAddress(void *buffer) noexcept = 0;

    /**
      * @brief Gets a const reference to the data encoding object of
      *        the underlying buffer
      *
      * This is necessary when the UserBuffer is filled by SNPE with
      * data types such as TF8, where the caller needs to know the quantization
      * parameters in order to interpret the data properly
      *
      * @return A read-only encoding object
     */
    virtual const UserBufferEncoding& getEncoding() const noexcept = 0;

    /**
      * @brief Gets a reference to the data encoding object of
      *        the underlying buffer
      *
      * This is necessary when the UserBuffer is re-used, and the encoding
      * parameters can change.  For example, each input can be quantized with
      * different step sizes.
      *
      * @return Data encoding meta-data
     */
    virtual UserBufferEncoding& getEncoding() noexcept = 0;

};

/** @} */ /* end_addtogroup c_plus_plus_apis C++ */

}
}

#endif
