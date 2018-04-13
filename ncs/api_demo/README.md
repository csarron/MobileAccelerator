# NCS API Demo

With this demo, you can use NCS on macOS, Ubuntu, Android phones.


# Usage

## Requirements
**Hardware**: 
You need a USB Type C to Type A converter to plug in the NCS for newer MacBooks. You also need an OTG cable if you want to use the NCS on Android Phones.

**Software**: No requirements need for the C version. For the Python version, `Pillow` package is used to process the images, you can install by `pip install pillow`.

## macOS and Ubuntu

- build: `mkdir build && cd build && cmake .. && make`

- show usage: `./ncs_demo`

- run the demo: `./ncs_demo mobilenet_v1.graph keyboard.jpg` or run the Python version: `python ncs_demo.py`

example output:
```bash
inference graph: mobilenet_v1.graph
test image: keyboard.jpg
image size: 224
Booted 1.3.3 -> VSC
Successfully opened NCS device at index 0!
Successfully allocated graph for mobilenet_v1.graph

---doing inference now ---
Successfully loaded the tensor for image keyboard.jpg
Successfully got the inference result for image keyboard.jpg
Top1 result is: 509, computer keyboard, 0.817871
-----------------------
ncs reported layers: 31
ncs reported inference time: 48.797756 ms
time elapsed: 81.182999 ms
-----------------------
NCS work done.

```

***Note***: macOS tested on High Sierra 10.13.4, Ubuntu tested on 16.04.

In case the prebuilt `libusb` library does not work, 
you can install the libusb by `brew install libusb` on macOS or by `sudo apt install libusb-1.0-0-dev` on Ubuntu, and 
change `CMakeLists.txt` compiler and linker flags such as adding `pkg-config --libs --cflags libusb-1.0`

## Android

***Note***: tested on **rooted** Nexus 5 Phone running LineageOS 15.1 (based on Android 8.1.0), but it should also work on the stock ROM (Android 6.0) as long as it's rooted.

(A non rooted version should be a normal Android application that will use standard Android API to access USB devices, the demo may be added later.)
 
- prepare ndk: download ndk from [here](https://developer.android.com/ndk/downloads/index.html), and `export ANDROID_NDK=/path/to/your/ndk/`, e.g. `export ANDROID_NDK=/opt/android-ndk-r16b`

- build: `mkdir build_arm && cd build_arm && cmake -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK/build/cmake/android.toolchain.cmake -DANDROID_ABI="armeabi-v7a" -DANDROID_PLATFORM=android-17 ..  && make`

- push to the phone (it's better to use wireless adb since NCS is attached to the phone, see the debugging considerations [here](https://developer.android.com/guide/topics/connectivity/usb/index.html)):
`adb push armeabi-v7a ncs_demo keyboard.jpg mobilenet_v1.graph /data/local/tmp && adb push mvnc /data/local/tmp/armeabi-v7a`


- run demo: `adb shell`, `su`, `cd /data/local/tmp && export LD_LIBRARY_PATH=armeabi-v7a && ./ncs_demo mobilenet_v1.graph keyboard.jpg`

example output:
```text
hammerhead:/ $ su
hammerhead:/ # cd /data/local/tmp && export LD_LIBRARY_PATH=armeabi-v7a && ./ncs_demo mobilenet_v1.graph keyboard.jpg
inference graph: mobilenet_v1.graph
test image: keyboard.jpg
image size: 224
Booted 1 -> VSC
Successfully opened NCS device at index 0!
Successfully allocated graph for mobilenet_v1.graph

---doing inference now ---
Successfully loaded the tensor for image keyboard.jpg
Successfully got the inference result for image keyboard.jpg
Top1 result is: 509, computer keyboard, 0.817871
-----------------------
ncs reported layers: 31
ncs reported inference time: 49.192039 ms
time elapsed: 196.473999 ms
-----------------------
NCS work done.
hammerhead:/data/local/tmp #
```