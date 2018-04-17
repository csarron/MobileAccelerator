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
Java_com_cscao_apps_ncsdemo_MainActivity_setGraphFile(JNIEnv *env, jobject instance,
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

JNIEXPORT jstring JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_doInference(JNIEnv *env, jobject instance,
                                                     jstring graphFile_, jstring imageFile_,
                                                     jint labelOffset_) {
    const char *graphFile = (*env)->GetStringUTFChars(env, graphFile_, 0);
    const char *imageFile = (*env)->GetStringUTFChars(env, imageFile_, 0);

    if (strlen(graphFile) > 0) {
        strcpy(graph_file, graphFile);
    }

    if (strlen(imageFile) > 0) {
        strcpy(image_file, imageFile);
    }

    unsigned int image_size = 224;
    unsigned int label_offset = (unsigned int) labelOffset_;

    LOGI("Inference graph: %s\n", graph_file);
    LOGI("Test image: %s\n", image_file);
    LOGI("Image size: %d\n", image_size);

    mvncStatus retCode;
    void *deviceHandle;
    if (!OpenOneNCS(0, &deviceHandle)) {    // couldn't open first NCS device
        LOGE("OpenOneNCS failed!\n")
    }

    void *graphHandle;
    if (!LoadGraphToNCS(deviceHandle, graph_file, &graphHandle)) {
        mvncCloseDevice(deviceHandle);
        LOGE("LoadGraphToNCS failed!\n")
    }

    LOGI("\n---Doing inference now ---\n");
    struct timeval tval_before, tval_after, tval_result;

    float image_mean[] = {128, 128, 128};
    float image_std = 1 / 128.0f;

    if (label_offset == 1) {
        // vgg processing
        image_mean[0] = 0;
        image_mean[1] = 0;
        image_mean[2] = 0;
        image_std = 1;
    }

    gettimeofday(&tval_before, NULL);

    DoInferenceOnImageFile(graphHandle, image_file, image_size, image_mean, image_std,
                           label_offset);

    gettimeofday(&tval_after, NULL);
    timersub(&tval_after, &tval_before, &tval_result);

    LOGI("-----------------------\n");
    float elapsed_time = tval_result.tv_sec + tval_result.tv_usec / 1000.0f;
//    LOGI("Time elapsed: %ld.%06ld s\n", (long int) tval_result.tv_sec, (long int) tval_result.tv_usec);
    float *ncs_time = (float *) malloc(sizeof(float *) * 200);
//    memset(ncs_time, 0, 200);

    unsigned int time_len = 0;
    mvncGetGraphOption(graphHandle, MVNC_TIME_TAKEN, &ncs_time, &time_len);
    LOGI("NCS reported layers: %d\n", (int) (time_len / sizeof(float)));
    float ncs_inference_time = 0;
    for (unsigned int i = 0; i < time_len / sizeof(float); i++) {
        ncs_inference_time += ncs_time[i];
    }
    LOGI("NCS reported inference time: %.03f ms\n", ncs_inference_time);
    LOGI("Time elapsed: %.03f ms\n", elapsed_time);

    retCode = mvncDeallocateGraph(graphHandle);
    if (retCode != MVNC_OK) {
        LOGE("Cannot deallocate graph!");
    }
    graphHandle = NULL;

    retCode = mvncCloseDevice(deviceHandle);
    if (retCode != MVNC_OK) {
        LOGE("Cannot close device!");
    }
    deviceHandle = NULL;

//    for (unsigned int i = 0; i < time_len / sizeof(float); i++) {
//        LOGI("ncs layer time: %d, %f ms\n",i, ncs_time[i]);
//    }

    LOGI("-----------------------\n");
    LOGI("NCS work done.\n");

    char result_str[100];
    sprintf(result_str, "inference: %.02f ms, total: %.02f ms", ncs_inference_time, elapsed_time);

    (*env)->ReleaseStringUTFChars(env, graphFile_, graphFile);
    (*env)->ReleaseStringUTFChars(env, imageFile_, imageFile);

    return (*env)->NewStringUTF(env, result_str);
}

JNIEXPORT void JNICALL
Java_com_cscao_apps_ncsdemo_MainActivity_setLogLevel(JNIEnv *env, jobject instance, jint level) {

    mvnc_loglevel = level;

}

#ifdef __cplusplus
}
#endif