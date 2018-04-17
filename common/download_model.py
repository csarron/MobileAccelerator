#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import argparse
import glob
import os
import sys
import tarfile

try:
    import urllib.request as url_request
except ImportError:
    import urllib as url_request

model_url_map = {
    "inception_v3": {
        "url": "http://download.tensorflow.org/models/inception_v3_2016_08_28.tar.gz",
        "filename": "inception_v3_2016_08_28.tar.gz",
        "name": "inception_v3"
    },
    "mobilenet_v1_1.0": {
        "url": "http://download.tensorflow.org/models/mobilenet_v1_2018_02_22/mobilenet_v1_1.0_224.tgz",
        "filename": "mobilenet_v1_1.0_224.tgz",
        "name": "mobilenet_v1_1.0"
    },
    "mobilenet_v2_1.4": {
        "url": "https://storage.googleapis.com/mobilenet_v2/checkpoints/mobilenet_v2_1.4_224.tgz",
        "filename": "mobilenet_v2_1.4_224.tgz",
        "name": "mobilenet_v2_1.4"
    },
    "mobilenet_v2_1.3": {
        "url": "https://storage.googleapis.com/mobilenet_v2/checkpoints/mobilenet_v2_1.3_224.tgz",
        "filename": "mobilenet_v2_1.3_224.tgz",
        "name": "mobilenet_v2_1.3"
    },
    "mobilenet_v2_1.0": {
        "url": "https://storage.googleapis.com/mobilenet_v2/checkpoints/mobilenet_v2_1.0_224.tgz",
        "filename": "mobilenet_v2_1.0_224.tgz",
        "name": "mobilenet_v2_1.0"
    },
    "resnet_v1_50": {
        "url": "http://download.tensorflow.org/models/resnet_v1_50_2016_08_28.tar.gz",
        "filename": "resnet_v1_50_2016_08_28.tar.gz",
        "name": "resnet_v1_50"
    }
}


def _may_download_model(model_name, blob_dir):
    model_file_name = model_url_map[model_name]["name"]
    model_dir = os.path.join(blob_dir, model_file_name)

    tar_file = model_url_map[model_name]["filename"]
    tar_url = model_url_map[model_name]["url"]

    tar_path = os.path.join(model_dir, tar_file)

    if os.path.exists(tar_path):
        file_name = os.path.basename(tar_path)
        print("{} is already downloaded.".format(file_name))
    else:
        download_file(tar_path, tar_url)


def download_file(file_path_, download_url):
    file_name = os.path.basename(file_path_)

    def _progress(count, block_size, total_size):
        sys.stdout.write("\rDownloading %s %.1f%%" % (
            file_name, float(count * block_size) / float(total_size) * 100.0))
        sys.stdout.flush()

    file_path, _ = url_request.urlretrieve(download_url, file_path_, _progress)
    print()
    stat_info = os.stat(file_path)
    print("Downloaded {}, {:.2f}MB".format(file_name, stat_info.st_size / 1024 / 1024))


def process_model(model_name, data_dir_):
    model_file_name = model_url_map[model_name]["name"]
    model_dir = os.path.join(data_dir_, model_file_name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    _may_download_model(model_name, data_dir_)

    # files = glob.glob("{}/*.ckpt*".format(model_dir))
    # if files:
    #     print("{} is already processed".format(model_file_name))
    #     print()
    #     return

    tar_file = model_url_map[model_name]["filename"]
    file_path = os.path.join(model_dir, tar_file)

    tarfile.open(file_path, "r:gz").extractall(model_dir)
    print("Successfully extracted the model: {}".format(model_file_name))


def check_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        print("dir: {} created".format(dir_name))
    else:
        print("using dir: {}".format(dir_name))
    return dir_name


if __name__ == '__main__':
    models = ["inception_v3", "mobilenet_v1_1.0", "mobilenet_v2_1.0",
              "mobilenet_v2_1.3", "mobilenet_v2_1.4", "resnet_v1_50"]  # add alexnet, squeezenet_v1.1, vgg_16

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--model", choices=models, default="mobilenet_v2_1.0",
                       help="download specified model")
    group.add_argument("-a", "--all", action="store_true",
                       help="download all available models")
    parser.add_argument("-d", "--data_dir", type=check_dir, default="data/",
                        help="directory to put model files")
    args = parser.parse_args()
    data_dir = args.data_dir
    if not args.all and args.model:
        models = [args.model]

    for model in models:
        process_model(model, data_dir)
