# AcceleratorProject

## Requirements

- ***NOTE*** that SNPE only supports Python 2, 
it's better to run the code in a Python 2 environment although other scripts support Python 3.
- install TensorFlow, either CPU or GPU version. (tested for version 1.7.0)
- install Python dependencies by `pip install -r requirements.txt`

## Usage

### Model Preparation

Download model: `python common/download_model.py --model mobilenet_v2`

Export model inference graph: `python common/slim/export_inference_graph.py --model_name=mobilenet_v2 --image_size=224 --output_file=data/mobilenet_v2/mobilenet_v2_inf.pb`

Freeze model: `python common/freeze_model.py --checkpoint_file data/mobilenet_v2/mobilenet_v2_1.4_224.ckpt --inference_graph data/mobilenet_v2/mobilenet_v2_inf.pb`

Visualizing model: `python common/visualize_model.py data/mobilenet_v2/mobilenet_v2_1.4_224.frozen.pb`

(Another awesome visualization tool is [Netron](https://lutzroeder.github.io/Netron/), just upload `mobilenet_v2_1.4_224.frozen.pb` in your browser)

### SNPE for Phone GPU

No more hassles of setting up SNPE now, just download the SNPE SDK from [Qualcomm website](https://developer.qualcomm.com/software/snapdragon-neural-processing-engine-ai).
Suppose the SDK is saved to `data/snpe-1.13.0.zip`.

Download the Android NDK from [Android NDK website](https://developer.android.com/ndk/downloads/index.html) if you don't have it, unzip the NDK. 
Then you can either `export ANDROID_NDK=path/to/android-ndk` for the `snpe/run_snpe.py` script or pass the NDK path as argument to the script.

Then just run `python snpe/run_snpe.py --snpe_sdk data/snpe-1.13.0.zip --model data/mobilenet_v2/mobilenet_v2_1.4_224.frozen.pb --android_ndk path/to/android-ndk `


### NCSDK for Movidius NCS

Convert model to ncs compatible format: `python ncs/convert_model.py --checkpoint_file data/mobilenet_v2/mobilenet_v2_1.4_224.ckpt --model mobilenet_v2 --image_size 224`
(for inception_v3, you can do `python ncs/convert_model.py -c data/inception_v3/inception_v3.ckpt -s 299 -m inception_v3`)

Run profiling on ncs: `python ncs/run_ncs.py --model data/mobilenet_v2/ncs_mobilenet_v2.meta`

### TensorRT for Nvidia Jetson TX2