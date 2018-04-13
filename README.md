# AcceleratorProject

## Requirements

- ***NOTE*** that SNPE only supports Python 2, 
it's better to run the code in a Python 2 environment although other scripts support Python 3.
- install TensorFlow, either CPU or GPU version. (tested for version 1.7.0)
- install Python dependencies by `pip install -r requirements.txt`

## Usage

### Model Preparation

- (required) Download model: `python common/download_model.py --model mobilenet_v2`

- (required for SNPE) Export model inference graph: `python common/slim/export_inference_graph.py --model_name mobilenet_v2 --image_size 224 --output_file data/mobilenet_v2/mobilenet_v2_inf.pb`

- (required for SNPE) Freeze model: `python common/freeze_model.py --checkpoint_file data/mobilenet_v2/mobilenet_v2_1.4_224.ckpt --inference_graph data/mobilenet_v2/mobilenet_v2_inf.pb`

- (optional) Visualizing model: `python common/visualize_model.py data/mobilenet_v2/mobilenet_v2_1.4_224.frozen.pb`

(Another awesome visualization tool is [Netron](https://lutzroeder.github.io/Netron/), just upload `mobilenet_v2_1.4_224.frozen.pb` in your browser)

### SNPE for Phone GPU

1. No more hassles of setting up SNPE now, just download the SNPE SDK from [Qualcomm website](https://developer.qualcomm.com/software/snapdragon-neural-processing-engine-ai).
Suppose the SDK is saved to `data/snpe-1.13.0.zip`.

2. Download the Android NDK from [Android NDK website](https://developer.android.com/ndk/downloads/index.html) if you don't have it, unzip the NDK. 
Then you can either `export ANDROID_NDK=path/to/android-ndk` for the `snpe/run_snpe.py` script or pass the NDK path as argument to the script.

3. Then just run `python snpe/run_snpe.py --snpe_sdk data/snpe-1.13.0.zip --model data/mobilenet_v2/mobilenet_v2_1.4_224.frozen.pb --android_ndk path/to/android-ndk `


### NCSDK for Movidius NCS

1. Convert model to ncs compatible format: `python ncs/convert_model.py --checkpoint_file data/mobilenet_v2/mobilenet_v2_1.4_224.ckpt --model mobilenet_v2 --image_size 224`

2. Run profiling on ncs: `python ncs/run_ncs.py --model data/mobilenet_v2/ncs_mobilenet_v2.meta`

### NCS API Demo on the Android Phone, macOS

see [ncs/api_demo/README.md](ncs/api_demo/README.md)

### TensorRT for Nvidia Jetson TX2

See the Nvidia [official examples](https://github.com/NVIDIA-Jetson/tf_to_trt_image_classification/)

## Common commands


Useful commands:

- export inception_v3 inference graph: `python common/slim/export_inference_graph.py -m inception_v3 -s 299 -o data/inception_v3/inception_v3_inf.pb`
- freeze inception_v3: `python common/freeze_model.py -c data/inception_v3/inception_v3.ckpt -g data/inception_v3/inception_v3_inf.pb`
- benchmark inception_v3 using snpe: `python snpe/run_snpe.py -m data/inception_v3/inception_v3.frozen.pb -s 299`
- convert inception_v3 for ncs: `python ncs/convert_model.py -c data/inception_v3/inception_v3.ckpt -s 299 -m inception_v3`
- profile inception_v3 on ncs: `python ncs/run_ncs.py -m data/inception_v3/ncs_inception_v3.meta`

- freeze resnet_v1_50: `python common/freeze_model.py -c data/resnet_v1_50/resnet_v1_50.ckpt -g data/resnet_v1_50/resnet_v1_50_inf.pb`
- (this command will ***fail*** since snpe-1.13.0 does not support resnet!) benchmark resnet_v1_50 using snpe: `python snpe/run_snpe.py -m data/resnet_v1_50/resnet_v1_50.frozen.pb`
- convert resnet_v1_50 for ncs: `python ncs/convert_model.py -c data/resnet_v1_50/resnet_v1_50.ckpt -m resnet_v1_50 -l 1`
- profile resnet_v1_50 on ncs: `python ncs/run_ncs.py -m data/resnet_v1_50/ncs_resnet_v1_50.meta`

## Useful papers

- [Fathom: Reference Workloads for Modern Deep Learning Methods](https://arxiv.org/pdf/1608.06581.pdf)
- [Latency and Throughput Characterization of Convolutional Neural Networks for Mobile Computer Vision](https://arxiv.org/pdf/1803.09492.pdf)