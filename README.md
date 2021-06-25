# MobileAccelerator

See https://awk.ai/#ncs for the paper, slides and presentation.

If you find our work useful to your research, please consider using the following citation:

````bib
@inproceedings{10.1145/3469116.3470011,
author = {Cao, Qingqing and Irimiea, Alexandru E. and Abdelfattah, Mohamed and Balasubramanian, Aruna and Lane, Nicholas D.},
title = {Are Mobile DNN Accelerators Accelerating DNNs?},
year = {2021},
isbn = {9781450385978},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3469116.3470011},
doi = {10.1145/3469116.3470011},
abstract = {Deep neural networks (DNNs) are running on many mobile and embedded devices with the goal of energy efficiency and highest possible performance. However, DNN workloads are getting more computationally intensive, and simultaneously their deployment is ever-increasing. This has led to the creation of many purpose-built low-power neural accelerators to replace or augment traditional mobile CPUs and GPUs. In this work, we provide an in-depth study of one set of commercially-available mobile accelerators, the Intel Neural Compute Sticks (NCS). We perform a systematic measurement study of the latency and energy of this accelerator under a variety of DNNs including convolutional neural networks (CNNs) for vision tasks and attention-based Transformer models for NLP tasks. We compare to the mobile processors (CPU, GPU, and DSP) on a smartphone and a mobile board. Our study shows commercial mobile accelerators like NCS are not ready yet to provide the performance as claimed. We also point out directions in optimizing the model architectures to better suit these accelerators.},
booktitle = {Proceedings of the 5th International Workshop on Embedded and Mobile Deep Learning},
pages = {7–12},
numpages = {6},
location = {Virtual, WI, USA},
series = {EMDL'21}
}
````

You may also find the NCS repo useful, https://github.com/csarron/ncs

## Requirements

- ***NOTE*** that SNPE only supports Python 2, and NCS profiling only supports Python 3.

it's better to run the code in a Python 2 environment but also prepare a Python 3 environment.
You can do it via virualenv: 

- create Python 3 env: `virtualenv -p python3 ~/p3dl`, 
- activate Python 3 env: `source ~/p3dl/bin/activate`
- install TensorFlow (1.7.0) by `pip install tensorflow==1.7.0`

- create Python 2 env: `virtualenv -p python2 ~/p2dl`; 
- activate Python 2 env: `source ~/p2dl/bin/activate`).
- then install Python dependencies by `pip install -r requirements.txt` (TensorFlow tested for version 1.8.0)

## Usage

### Model Preparation

#### Step by step
- (required) Download model: `python common/download_model.py --model mobilenet_v2_1.0` 
or download all supported models by `python common/download_model.py -a` 

- (required ) Export model inference graph: `python common/export_inference_graph.py  --model_name mobilenet_v2_1.0 --image_size 224 --output_file data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb`

- (required for SNPE) Freeze model: `python common/freeze_model.py --checkpoint_file data/mobilenet_v2_1.0/mobilenet_v2_1.0_224.ckpt --inference_graph data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb`
- (required for NCS) Convert model: `python ncs/convert_model.py --checkpoint_file data/mobilenet_v2_1.0/mobilenet_v2_1.0_224.ckpt --inference_graph data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb`

- (optional) Visualizing model: `python common/visualize_model.py data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb`

(Another awesome visualization tool is [Netron](https://lutzroeder.github.io/Netron/), just upload `mobilenet_v2_1.0_224.frozen.pb` in your browser)

#### All in one

Just run `common/prepare_all.sh`

**Known SDK Issues**: 
- `mobilenet_v2_1.3` and `mobilenet_v2_1.4` although can be profiled on the NCS, 
but the inference results are always the same and not correct. Maybe the NCS sdk is not parsing the models correctly.
- `resnet_v1_50` for SNPE is not working correctly, the DLC conversion may not handle ResNet correctly.

### SNPE for Phone GPU

1. No more hassles of setting up SNPE now, just download the SNPE SDK from [Qualcomm website](https://developer.qualcomm.com/software/snapdragon-neural-processing-engine-ai).
Suppose the SDK is saved to `data/snpe-1.14.1.zip`.

2. Download the Android NDK from [Android NDK website](https://developer.android.com/ndk/downloads/index.html) if you don't have it, unzip the NDK. 
Then you can either `export ANDROID_NDK=path/to/android-ndk` for the `snpe/run_snpe.py` script or pass the NDK path as argument to the script.

3. Then just run `python snpe/run_snpe.py --model data/mobilenet_v2_1.0/mobilenet_v2_1.0_224.frozen.pb --snpe_sdk data/snpe-1.14.1.zip --android_ndk path/to/android-ndk `


### NCSDK for Movidius NCS on Ubuntu and macOS

Just run profiling on ncs: `python ncs/run_ncs.py --model data/mobilenet_v2_1.0/ncs_mobilenet_v2_1.0_224.meta`

**NOTE**: you can specify a separated Python 3 environment by `-p3 /path/to/python3` instead of the `python3` on your system , e.g. 
`python ncs/run_ncs.py --model data/mobilenet_v2_1.0/ncs_mobilenet_v2_1.0_224.meta -p ~/p3dl/bin/python`

### NCS API Demo on the Android Phone, macOS

see [ncs/api_demo/README.md](ncs/api_demo/README.md)


### Android App

**NOTE**: current version needs root access, although non-root version can be developed later (using Androi USB API instead of native libusb).

Tested on Nexus 6P and OnePlus3, both works for NCS.

### Monsoon Power Measurements

Tested on macOS

- Just sample and save to csv file: `python energy/measure.py`

- Sample and display: `python energy/sample.py`

### TensorRT for Nvidia Jetson TX2

See the Nvidia [official examples](https://github.com/NVIDIA-Jetson/tf_to_trt_image_classification/)

## Useful commands for ResNet

- export inference graph for resnet_v1_50: `python common/export_inference_graph.py -m resnet_v1_50 -o data/resnet_v1_50/resnet_v1_50.inf.pb -l 1`
- freeze resnet_v1_50: `python common/freeze_model.py -c data/resnet_v1_50/resnet_v1_50.ckpt -g data/resnet_v1_50/resnet_v1_50.inf.pb`
- (this command will ***fail*** since snpe-1.14.1 does not support resnet!) benchmark resnet_v1_50 using snpe: `python snpe/run_snpe.py -m data/resnet_v1_50/resnet_v1_50.frozen.pb`
- convert resnet_v1_50 for ncs: `python ncs/convert_model.py -c data/resnet_v1_50/resnet_v1_50.ckpt -g data/resnet_v1_50/resnet_v1_50.inf.pb`
- profile resnet_v1_50 on ncs: `python ncs/run_ncs.py -m data/resnet_v1_50/ncs_resnet_v1_50.meta`

## Generate Models With Fake Weights

Example: `model=alexnet_v2` or `model=squeezenet`
 
`mkdir -p data/$model;`

`python common/export_inference_graph.py -m $model -o data/$model/$model.inf.pb;`

`python common/gen_weights.py -m $model -o data/$model/$model.ckpt;`

`python common/freeze_model.py -c data/$model/$model.ckpt -g data/$model/$model.inf.pb;`

`python ncs/convert_model.py -c data/$model/$model.ckpt -g data/$model/$model.inf.pb;`

Run NCS: `python ncs/run_ncs.py -m data/$model/ncs_$model.meta -p3 ~/p3dl/bin/python;`

Run SNPE: `python snpe/run_snpe.py -m data/$model/$model.frozen.pb`

## Generate TensorFlow Lite Models

`python tflite/convert_model.py  data/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.frozen.pb`

macOS: `tflite/macos/label_image -m data/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.frozen.tflite -i tflite/res/grace_hopper.bmp -l tflite/res/labels.txt`

Android(arm64): `adb push tflite/arm64/label_image data/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.frozen.tflite tflite/res/* /data/local/tmp`;

`adb shell 'cd /data/local/tmp; ./label_image -m ./mobilenet_v2_1.0_224.frozen.tflite -c 10'`

## Useful papers

- [Fathom: Reference Workloads for Modern Deep Learning Methods](https://arxiv.org/pdf/1608.06581.pdf)
- [Latency and Throughput Characterization of Convolutional Neural Networks for Mobile Computer Vision](https://arxiv.org/pdf/1803.09492.pdf)


