#include <jni.h>
#include <stdio.h>
#include <string.h>
//#include <string>
#include "../../../../../ncs/api_demo/api/src/usb_boot.h"
#include "../../../../../ncs/api_demo/api/src/common.h"
#include "../../../../../ncs/api_demo/api/include/mvnc.h"
#include "../../../../../ncs/api_demo/ncs_demo.h"


#ifdef __cplusplus
extern "C"
{
#endif

char graph_file[FILENAME_MAX];
char image_file[FILENAME_MAX];

JNIEXPORT void JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_setCmdFile(JNIEnv *env, jobject instance,
                                                    jstring cmdFilePath_) {
    const char *cmdFilePath = (*env)->GetStringUTFChars(env, cmdFilePath_, 0);
    strcpy(mv_cmd_file, cmdFilePath);
    (*env)->ReleaseStringUTFChars(env, cmdFilePath_, cmdFilePath);
}

JNIEXPORT void JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_setModelFile(JNIEnv *env, jobject instance,
                                                      jstring graphFile_) {
    const char *graphFile = (*env)->GetStringUTFChars(env, graphFile_, 0);
    strcpy(graph_file, graphFile);
    (*env)->ReleaseStringUTFChars(env, graphFile_, graphFile);
}

JNIEXPORT void JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_setImageFile(JNIEnv *env, jobject instance,
                                                      jstring imageFile_) {
    const char *imageFile = (*env)->GetStringUTFChars(env, imageFile_, 0);
    strcpy(image_file, imageFile);
    (*env)->ReleaseStringUTFChars(env, imageFile_, imageFile);
}

JNIEXPORT void JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_setLogLevel(JNIEnv *env, jobject instance, jint level) {

    mvnc_loglevel = level;

}

JNIEXPORT jfloatArray JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_getImageFloats(JNIEnv *env, jobject instance,
                                                        jstring imageFile_, jint width,
                                                        jint height) {
    const char *imageFile = (*env)->GetStringUTFChars(env, imageFile_, 0);

    float *imageData = getImageFloats(imageFile, width, height);

    jsize imageLen = width * height * 3;
    jfloatArray imageArray = (*env)->NewFloatArray(env, imageLen);

    if (NULL == imageArray) {
        return NULL;
    }
    (*env)->SetFloatArrayRegion(env, imageArray, 0, imageLen, imageData);

    (*env)->ReleaseStringUTFChars(env, imageFile_, imageFile);
    return imageArray;
}

JNIEXPORT jstring JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_decodePredictions(JNIEnv *env, jobject instance,
                                                           jfloatArray predictions_,
                                                           jint labelOffset) {
    jfloat *predictions = (*env)->GetFloatArrayElements(env, predictions_, NULL);
    jsize len = (*env)->GetArrayLength(env, predictions_);

    float maxResult = 0.0;
    int maxIndex = -1;
    for (int index = 0; index < len; index++) {
        if (predictions[index] > maxResult) {
            maxResult = predictions[index];
            maxIndex = index;
        }
    }

    (*env)->ReleaseFloatArrayElements(env, predictions_, predictions, 0);

    char result_str[100];
    sprintf(result_str, "Top1 result is: %d, %s, %.03f", maxIndex + labelOffset,
            imagenet_classes[maxIndex + labelOffset], predictions[maxIndex]);

    return (*env)->NewStringUTF(env, result_str);
}


JNIEXPORT jlong JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_openNcsDevice(JNIEnv *env, jobject instance, jint index) {

    void *deviceHandle;
    if (!OpenOneNCS(0, &deviceHandle)) {    // couldn't open first NCS device
        LOGE("OpenOneNCS failed!\n");
        return 0;
    }

    return (jlong) deviceHandle;
}

JNIEXPORT jlong JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_loadNcsModel(JNIEnv *env, jobject instance,
                                                      jstring modelFile_, jlong deviceHandle_) {
    const char *modelFile = (*env)->GetStringUTFChars(env, modelFile_, 0);
    if (strlen(modelFile) > 0) {
        strcpy(graph_file, modelFile);
    }

    void *deviceHandle = (void *) deviceHandle_;
    void *graphHandle;
    if (!LoadGraphToNCS(deviceHandle, graph_file, &graphHandle)) {
        mvncCloseDevice(deviceHandle);
        LOGE("LoadGraphToNCS failed!\n");
        return 0;
    }

    (*env)->ReleaseStringUTFChars(env, modelFile_, modelFile);
    return (jlong) graphHandle;
}

JNIEXPORT jfloatArray JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_inferOnNcs(JNIEnv *env, jobject instance,
                                                    jlong graphHandle_,
                                                    jfloatArray imageData_) {
    jfloat *imageData = (*env)->GetFloatArrayElements(env, imageData_, NULL);
    unsigned int imageSize = 224;
    LOGI("Convert float image tensor to half\n");

    half *imageBuf = (half *) malloc(sizeof(half) * imageSize * imageSize * 3);
    if (!imageBuf) {
        perror("malloc");
    }
    floattofp16((unsigned char *) imageBuf, imageData, imageSize * imageSize * 3);
    unsigned int lenBuf = 3 * imageSize * imageSize * sizeof(*imageBuf);
    void *graphHandle = (void *) graphHandle_;
    LOGI("Begin loading image tensor to ncs\n");

    mvncStatus retCode = mvncLoadTensor(graphHandle, imageBuf, lenBuf, NULL);
    free(imageBuf);
    if (retCode != MVNC_OK) {   // error loading tensor
        LOGE("Could not load tensor");
        LOGE(" mvncStatus from mvncLoadTensor is: %d\n", retCode);
        (*env)->ReleaseFloatArrayElements(env, imageData_, imageData, 0);
        return NULL;
    }

    LOGI("Successfully loaded the input image tensor\n");

    void *resultData16;
    void *userParam;
    unsigned int lenResultData;
    retCode = mvncGetResult(graphHandle, &resultData16, &lenResultData, &userParam);
    if (retCode != MVNC_OK) {
        LOGE("Could not get result for image\n");
        LOGE(" mvncStatus from mvncGetResult is: %d\n", retCode);

        unsigned int debug_len = 100;
        char debug_str[debug_len];

        retCode = mvncGetGraphOption(graphHandle, MVNC_DEBUG_INFO, &debug_str, &debug_len);

        LOGE("ncs debug (%d): %s\n", debug_len, *(char **)debug_str);
        LOGE(" mvncStatus from debug is: %d\n", retCode);

        (*env)->ReleaseFloatArrayElements(env, imageData_, imageData, 0);
        return NULL;
    }
    LOGI("Got the inference result: %d bytes which is %d 16-bit floats.\n", lenResultData,
         lenResultData / (int) sizeof(half));
    // convert half precision floats to full floats
    unsigned int numResults = lenResultData / sizeof(half);
    float *resultData32;
    resultData32 = (float *) malloc(numResults * sizeof(*resultData32));
    fp16tofloat(resultData32, (unsigned char *) resultData16, numResults);
    LOGI("Converted the results to float\n");

    jfloatArray predictions = (*env)->NewFloatArray(env, numResults);
    if (NULL == predictions) return NULL;
    (*env)->SetFloatArrayRegion(env, predictions, 0, numResults, resultData32);

    (*env)->ReleaseFloatArrayElements(env, imageData_, imageData, 0);
    return predictions;
}

JNIEXPORT void JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_cleanUpNcs(JNIEnv *env, jobject instance,
                                                    jlong graphHandle_, jlong deviceHandle_) {

    void *graphHandle = (void *) graphHandle_;
    void *deviceHandle = (void *) deviceHandle_;

    mvncStatus retCode = mvncDeallocateGraph(graphHandle);
    if (retCode != MVNC_OK) {
        LOGE("Cannot deallocate graph!");
    }

    retCode = mvncCloseDevice(deviceHandle);
    if (retCode != MVNC_OK) {
        LOGE("Cannot close device!");
    }
}

JNIEXPORT jfloatArray JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_getNcsLayerTimes(JNIEnv *env, jobject instance,
                                                          jlong graphHandle_, jint maxLayers_) {


    void *graphHandle = (void *) graphHandle_;
    float *layerTimes = (float *) malloc(sizeof(float *) * maxLayers_);

    unsigned int time_len = 0;
    mvncGetGraphOption(graphHandle, MVNC_TIME_TAKEN, &layerTimes, &time_len);
//    LOGI("NCS reported layers: %d\n", (int) (maxLayers_ / sizeof(float)));
    unsigned int layers = time_len / sizeof(float);
//    float ncs_inference_time = 0;
//    for (unsigned int i = 0; i < time_len / sizeof(float); i++) {
//        ncs_inference_time += layerTimes[i];
//    }
//    LOGI("NCS reported inference time: %.03f ms\n", ncs_inference_time);
    jfloatArray actualLayerTimes = (*env)->NewFloatArray(env, layers);
    if (NULL == actualLayerTimes) return NULL;
    (*env)->SetFloatArrayRegion(env, actualLayerTimes, 0, layers, layerTimes);
    return actualLayerTimes;
}


JNIEXPORT jint JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_getNumClasses(JNIEnv *env, jobject instance) {

    jint num = sizeof(imagenet_classes) / sizeof(imagenet_classes[0]);
    LOGI("classes: %d\n", num);
    return num;

}

#ifdef __cplusplus
}
#endif