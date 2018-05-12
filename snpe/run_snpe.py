from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import numpy as np
import os
import tensorflow as tf
import zipfile as zp
import subprocess
import glob
import json
from PIL import Image
from collections import OrderedDict
import shutil
import stat
import sys


def convert_to_dlc(script_path, frozen_model_file, snpe_root, input_node='input', output_node='output', image_size=224):
    print('converting ' + frozen_model_file + ' to snpe dlc format')
    sys.stdout.flush()
    model_name_ = os.path.splitext(os.path.split(frozen_model_file)[1])[0]
    dlc_path = 'models/{}.dlc'.format(model_name_)
    dlc_full_path = os.path.join(snpe_root, 'benchmarks', dlc_path)
    # if os.path.exists(dlc_full_path):
    #     return dlc_path

    if not os.path.exists(os.path.dirname(dlc_full_path)):
        os.makedirs(os.path.dirname(dlc_full_path))
    cmd = [script_path,
           '--graph', os.path.abspath(frozen_model_file),
           '--input_dim', input_node, '{0},{0},3'.format(image_size),
           '--out_node', output_node,
           '--allow_unconsumed_nodes',
           '--dlc', dlc_full_path]
    subprocess.call(cmd)
    print()
    sys.stdout.flush()
    return dlc_path
    # print('INFO: Creating ' + DLC_QUANTIZED_FILENAME + ' quantized model')
    # data_cropped_dir = os.path.join(os.path.join(model_dir, 'data'), 'cropped')
    # cmd = ['snpe-dlc-quantize',
    #        '--input_dlc', os.path.join(dlc_dir, DLC_FILENAME),
    #        '--input_list', os.path.join(data_cropped_dir, RAW_LIST_FILE),
    #        '--output_dlc', os.path.join(dlc_dir, DLC_QUANTIZED_FILENAME)]
    # subprocess.call(cmd)


def __get_img_raw(img_file):
    img_file = os.path.abspath(img_file)
    img = Image.open(img_file)
    img_ndarray = np.array(img)  # read it
    if len(img_ndarray.shape) != 3:
        raise RuntimeError('Image shape' + str(img_ndarray.shape))
    if img_ndarray.shape[2] != 3:
        raise RuntimeError('Require image with rgb but channel is %d' % img_ndarray.shape[2])
    # reverse last dimension: rgb -> bgr
    return img_ndarray


def __create_mean_raw(img_raw, mean_rgb):
    if img_raw.shape[2] != 3:
        raise RuntimeError('Require image with rgb but channel is %d' % img_raw.shape[2])
    img_dim = (img_raw.shape[0], img_raw.shape[1])
    mean_raw_r = np.empty(img_dim)
    mean_raw_r.fill(mean_rgb[0])
    mean_raw_g = np.empty(img_dim)
    mean_raw_g.fill(mean_rgb[1])
    mean_raw_b = np.empty(img_dim)
    mean_raw_b.fill(mean_rgb[2])
    # create with c, h, w shape first
    tmp_transpose_dim = (img_raw.shape[2], img_raw.shape[0], img_raw.shape[1])
    mean_raw = np.empty(tmp_transpose_dim)
    mean_raw[0] = mean_raw_r
    mean_raw[1] = mean_raw_g
    mean_raw[2] = mean_raw_b
    # back to h, w, c
    mean_raw = np.transpose(mean_raw, (1, 2, 0))
    return mean_raw.astype(np.float32)


def __create_raw_img(img_file, mean_rgb, div, req_bgr_raw, save_uint8):
    img_raw = __get_img_raw(img_file)
    mean_raw = __create_mean_raw(img_raw, mean_rgb)

    snpe_raw = img_raw - mean_raw
    snpe_raw = snpe_raw.astype(np.float32)
    # scalar data divide
    snpe_raw /= div

    if req_bgr_raw:
        snpe_raw = snpe_raw[..., ::-1]

    if save_uint8:
        snpe_raw = snpe_raw.astype(np.uint8)
    else:
        snpe_raw = snpe_raw.astype(np.float32)

    img_file = os.path.abspath(img_file)
    filename, ext = os.path.splitext(img_file)
    snpe_raw_filename = filename
    snpe_raw_filename += '.raw'
    snpe_raw.tofile(snpe_raw_filename)

    return 0


def __resize_square_to_jpg(src, dst, size):
    src_img = Image.open(src)
    # If black and white image, convert to rgb (all 3 channels the same)
    if len(np.shape(src_img)) == 2: src_img = src_img.convert(mode='RGB')
    # center crop to square
    width, height = src_img.size
    short_dim = min(height, width)
    crop_coord = (
        (width - short_dim) / 2,
        (height - short_dim) / 2,
        (width + short_dim) / 2,
        (height + short_dim) / 2
    )
    img = src_img.crop(crop_coord)
    # resize to alexnet size
    dst_img = img.resize((size, size), Image.ANTIALIAS)
    # save output - save determined from file extension
    dst_img.save(dst)
    return 0


def convert_img(src, dest, size):
    print("converting images...")
    for root, dirs, files in os.walk(src):
        for jpgs in files:
            src_image = os.path.join(root, jpgs)
            if '.jpg' in src_image:
                print(src_image)
                dest_image = os.path.join(dest, jpgs)
                __resize_square_to_jpg(src_image, dest_image, size)

    for root, dirs, files in os.walk(dest):
        for jpgs in files:
            src_image = os.path.join(root, jpgs)
            print(src_image)
            mean_rgb = (128, 128, 128)
            __create_raw_img(src_image, mean_rgb, 128, False, False)


def create_file_list(input_dir, output_filename, ext_pattern, print_out=True, rel_path=True):
    input_dir = os.path.abspath(input_dir)
    output_filename = os.path.abspath(output_filename)
    output_dir = os.path.dirname(output_filename)

    if not os.path.isdir(input_dir):
        raise RuntimeError('input_dir %s is not a directory' % input_dir)

    if not os.path.isdir(output_dir):
        raise RuntimeError('output_filename %s directory does not exist' % output_dir)

    glob_path = os.path.join(input_dir, ext_pattern)
    file_list = glob.glob(glob_path)

    if rel_path:
        file_list = [os.path.relpath(file_path, output_dir) for file_path in file_list]

    if len(file_list) <= 0:
        if print_out:
            print('no results with %s' % glob_path)
    else:
        with open(output_filename, 'w') as f:
            f.write('\n'.join(file_list))
            if print_out:
                print('%s created listing %d files.' % (output_filename, len(file_list)))


def prepare_data_images(image_size, snpe_root):
    # make a copy of the image files from the alex net model data dir
    image_dir_relative_path = 'models/alexnet/data'
    image_dir = os.path.join(snpe_root, image_dir_relative_path)

    data_cropped_dir = os.path.join(image_dir, 'cropped_%s' % image_size)
    raw_list = os.path.join(image_dir, 'target_raw_list_%s.txt' % image_size)

    if not os.path.exists(raw_list):
        os.makedirs(data_cropped_dir)
        print('creating inception style raw image data')
        convert_img(image_dir, data_cropped_dir, image_size)

        print('Create file lists')
        create_file_list(data_cropped_dir, raw_list, '*.raw')
    print()
    sys.stdout.flush()
    return data_cropped_dir, raw_list


# generate bench config json file
def gen_config(dlc_path, input_list_file, input_data, processors_, runs):
    name = os.path.splitext(os.path.basename(dlc_path))[0]
    config = OrderedDict()
    config['Name'] = name
    config['HostRootPath'] = name
    config['HostResultsDir'] = os.path.join(name, 'results')
    config['DevicePath'] = '/data/local/tmp/snpebm'
    config['Devices'] = ["123"]
    config['Runs'] = runs

    model = OrderedDict()
    model['Name'] = name
    model['Dlc'] = dlc_path
    model['InputList'] = input_list_file
    model['Data'] = [input_data]
    config['Model'] = model

    config['Runtimes'] = processors_
    config['Measurements'] = ['timing']  # ['timing', 'mem']

    return config


def write_config(config, save_path):
    with open(save_path, 'w') as f:
        json.dump(config, f, indent=4)


def check_processor_arg(processor_str):
    default = "GPU,DSP,CPU"
    processor_list = default.split(',')

    parsed_processors = []
    for p in processor_str.split(','):
        if p not in processor_list:
            print("please use either GPU, DSP or CPU or any combination of them, seperated by comma(',')")
            print("e.g. -p GPU,DSP means running on GPU and DSP; -p CPU means only running on CPU")
            exit(-1)
        else:
            parsed_processors.append(p)

    return parsed_processors


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-sdk", "--snpe_sdk", type=str, default="data/snpe-1.15.0.zip",
                        help="path to snpe sdk zip file")
    parser.add_argument("-p", "--processors", type=check_processor_arg, default="GPU,DSP,CPU",
                        help="processor to use, use GPU,DSP,CPU or any combination of them (separated by comma)")
    parser.add_argument("-n", "--runs", type=int, default=10,
                        help="number of times to repeat the run")
    parser.add_argument("-ndk", "--android_ndk", type=str,
                        help="path to android ndk")
    parser.add_argument("-m", "--model", type=str, default="data/mobilenet_v1/mobilenet_v1_1.0_224.frozen.pb",
                        help="frozen tensorflow model")
    parser.add_argument("-s", "--image_size", type=int, default=224,
                        help="input image size")
    parser.add_argument("-i", "--input_node", type=str, default='input',
                        help="input node name in the model")
    parser.add_argument("-o", "--output_node", type=str, default='output',
                        help="output node name in the model")
    parser.add_argument("-t", "--show_time", action='store_true',
                        help="show time in csv")
    return parser.parse_args()


if __name__ == '__main__':
    web_url = "https://developer.qualcomm.com/software/snapdragon-neural-processing-engine-ai"
    tf_path = os.path.dirname(tf.__file__)

    args = parse_args()

    snpe_sdk_file = args.snpe_sdk

    snpe_dir = os.path.dirname(snpe_sdk_file)
    snpe_sdk_path = os.path.abspath(os.path.splitext(snpe_sdk_file)[0])
    snpe_name = os.path.basename(snpe_sdk_path)

    if not os.path.exists(snpe_sdk_file):
        print("please download SNPE SDK from:", web_url)
        exit(-1)
    elif not os.path.exists(snpe_sdk_path):
        print("extracting snpe to:", snpe_sdk_path, "...")
        zp_ref = zp.ZipFile(snpe_sdk_file, 'r')
        zp_ref.extractall(snpe_dir)
        zp_ref.close()
        print("snpe sdk extraction done.")
    else:
        print("found snpe sdk at:", snpe_sdk_path)
        sys.stdout.flush()
    print()
    sys.stdout.flush()

    ndk_path = os.environ.get("ANDROID_NDK", None) or args.android_ndk
    if not ndk_path:
        print("please set ndk path either by specify -ndk or set 'export ANDROID_NDK=path/to/android-ndk'")
        exit(-1)

    # may install pkg deps
    if not os.path.exists('/tmp/{}_deps_checked'.format(snpe_name)):
        print("copying libs from ndk to snpe sdk...")

        shutil.copy('{}/sources/cxx-stl/gnu-libstdc++/4.9/libs/arm64-v8a/libgnustl_shared.so'.format(ndk_path),
                    '{}/lib/aarch64-linux-gcc4.9'.format(snpe_sdk_path))

        shutil.copy('{}/sources/cxx-stl/gnu-libstdc++/4.9/libs/armeabi-v7a/libgnustl_shared.so'.format(ndk_path),
                    '{}/lib/arm-android-gcc4.9'.format(snpe_sdk_path))
        print("gcc libs copied.")
        print()
        sys.stdout.flush()

        print("checking package dependencies...")
        check_cmd = 'yes | bash {}/bin/dependencies.sh'.format(snpe_sdk_path)
        subprocess.call(check_cmd, shell=True)

        print("checking python dependencies...")
        check_cmd = 'yes | bash {}/bin/check_python_depends.sh'.format(snpe_sdk_path)
        subprocess.call(check_cmd, shell=True)

        for os_type in ["arm-android-gcc4.9", "x86_64-linux-clang"]:
            for bin_file in os.listdir("{}/bin/{}".format(snpe_sdk_path, os_type)):
                script_file_path = os.path.join("{}/bin/{}".format(snpe_sdk_path, os_type), bin_file)
                print('set script:', script_file_path, ' to executable')
                sys.stdout.flush()
                st = os.stat(script_file_path)
                os.chmod(script_file_path, st.st_mode | stat.S_IEXEC)

        open('/tmp/{}_deps_checked'.format(snpe_name), 'a').close()

    os.environ["SNPE_ROOT"] = snpe_sdk_path
    py_path = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = "{0}/lib/python:{1}".format(snpe_sdk_path, py_path)

    os.environ["TENSORFLOW_HOME"] = tf_path
    bin_path = os.environ.get("PATH", "")
    os.environ["PATH"] = "{}/bin/x86_64-linux-clang:{}".format(snpe_sdk_path, bin_path)

    model_file = args.model
    if not os.path.exists(model_file):
        print(model_file, "not exist!")
        exit(-1)

    convert_dlc_script = "{}/bin/x86_64-linux-clang/snpe-tensorflow-to-dlc".format(snpe_sdk_path)

    dlc_file = convert_to_dlc(convert_dlc_script, model_file, snpe_sdk_path,
                              args.input_node, args.output_node, args.image_size)

    data_dir, raw_file_list = prepare_data_images(args.image_size, snpe_sdk_path)

    print('generating benchmark configuration...')
    sys.stdout.flush()
    config = gen_config(dlc_file, raw_file_list, data_dir, args.processors, args.runs)

    model_name = os.path.splitext(os.path.split(model_file)[1])[0]

    config_path = os.path.join('{}/benchmarks'.format(snpe_sdk_path), "{}.json".format(model_name))
    write_config(config, config_path)
    print('benchmark configuration generated.')
    print()
    sys.stdout.flush()

    print('running benchmark on {}...'.format(' '.join(args.processors)))
    print()
    sys.stdout.flush()

    bench_cmd = ['python', 'snpe_bench.py', '-c', config_path, '-a']
    subprocess.call(bench_cmd, cwd='{}/benchmarks'.format(snpe_sdk_path))

    stats_file = model_file.replace('.pb', '.csv')
    shutil.copy('{0}/benchmarks/{1}/results/latest_results/benchmark_stats_{1}.csv'.format(snpe_sdk_path, model_name),
                stats_file)
    print('benchmark results saved to:', stats_file)
    if args.show_time:
        import csv
        with open(stats_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if 'Total Inference Time' in row:
                    gpu_time = float(row[3])/1000
                    dsp_time = float(row[9])/1000
                    cpu_time = float(row[18])/1000
                    print('GPU, DSP, CPU')
                    print('{:4.2f}, {:4.2f}, {:4.2f}'.format(gpu_time, dsp_time, cpu_time))

    print('all done.')
