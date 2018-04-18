#include "ncs_demo.h"

int main(int argc, char **argv) {
    unsigned int image_size = 224;
    unsigned int label_offset = 0;
    if (argc <= 2) {
        LOGI(ANSI_YELLOW "Example usage: ./ncs_demo mobilenet_v1.graph keyboard.jpg 224\n");
        LOGI(ANSI_CYAN "Example usage 2: ./ncs_demo inception_v3.graph keyboard.jpg 299\n");
        LOGI(ANSI_MAGENTA "Example usage 3: ./ncs_demo resnet_v1_50.graph keyboard.jpg 224 1 (1 means label offset)\n");
        exit(1);
    }

    const char *graph_file = argv[1];
    const char *image_file = argv[2];

    if (argc >= 4) {
        image_size = (unsigned int) strtol(argv[3], &argv[3], 10);
    }

    if (argc >= 5) {
        label_offset = 1;
    }

    LOGI("Inference graph: " ANSI_BOLD ANSI_GREEN "%s\n", graph_file);

    LOGI("Test image: " ANSI_BOLD ANSI_GREEN "%s\n", image_file);

    LOGI("Image size: " ANSI_BOLD ANSI_GREEN "%d\n", image_size);

    mvncStatus retCode;
    void *deviceHandle;
    if (!OpenOneNCS(0, &deviceHandle)) {    // couldn't open first NCS device
        exit(-1);
    }

    void *graphHandle;
    if (!LoadGraphToNCS(deviceHandle, graph_file, &graphHandle)) {
        mvncCloseDevice(deviceHandle);
        exit(-2);
    }

    LOGI(ANSI_RESET ANSI_BOLD "\n---Doing inference now ---\n");
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
    char result_str[100];

    gettimeofday(&tval_before, NULL);

    DoInferenceOnImageFile(graphHandle, image_file, image_size,
                           image_mean, image_std, label_offset,
                           result_str);

    gettimeofday(&tval_after, NULL);
    timersub(&tval_after, &tval_before, &tval_result);

    LOGI(ANSI_RESET ANSI_BOLD "-----------------------\n");
    float elapsed_time = tval_result.tv_sec + tval_result.tv_usec / 1000.0f;
//    LOGI("Time elapsed: %ld.%06ld s\n", (long int) tval_result.tv_sec, (long int) tval_result.tv_usec);
    float *ncs_time = (float *) malloc(sizeof(float *) * 200);
//    memset(ncs_time, 0, 200);

    unsigned int time_len = 0;
    mvncGetGraphOption(graphHandle, MVNC_TIME_TAKEN, &ncs_time, &time_len);
    LOGI("NCS reported layers: " ANSI_GREEN "%d\n", (int) (time_len / sizeof(float)));
    float total_time = 0;
    for (unsigned int i = 0; i < time_len / sizeof(float); i++) {
        total_time += ncs_time[i];
    }
    LOGI("NCS reported inference time: " ANSI_BOLD ANSI_GREEN "%.03f ms\n", total_time);
    LOGI("Time elapsed: " ANSI_GREEN "%.03f ms\n", elapsed_time);

    retCode = mvncDeallocateGraph(graphHandle);
    graphHandle = NULL;

    retCode = mvncCloseDevice(deviceHandle);
    deviceHandle = NULL;

//
//    for (unsigned int i = 0; i < time_len / sizeof(float); i++) {
//        LOGI("ncs layer time: %d, %f ms\n",i, ncs_time[i]);
//    }
    LOGI(ANSI_RESET ANSI_BOLD "-----------------------\n");
    LOGI(ANSI_RESET ANSI_BOLD "NCS work done.\n");
}