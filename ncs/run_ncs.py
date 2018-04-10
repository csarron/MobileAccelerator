#! /usr/bin/env python3
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
import tarfile

try:
    import urllib.request as url_request
except ImportError:
    import urllib as url_request


def download_file(download_url, file_path_):
    file_name = os.path.basename(file_path_)

    def _progress(count, block_size, total_size):
        sys.stdout.write("\rDownloading %s %.1f%%" % (
            file_name, float(count * block_size) / float(total_size) * 100.0))
        sys.stdout.flush()

    file_path, _ = url_request.urlretrieve(download_url, file_path_, _progress)
    print()
    stat_info = os.stat(file_path)
    print("Downloaded {}, {:.2f}MB".format(file_name, stat_info.st_size / 1024 / 1024))


# run snpe bench script
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-sdk", "--ncs_sdk", type=str, default="data/NCSDK-1.12.00.01.tar.gz",
                        help="path to snpe sdk zip file")
    parser.add_argument("-m", "--model", type=str, default="data/mobilenet_v2/ncs_mobilenet_v2.meta",
                        help="frozen tensorflow model")
    parser.add_argument("-s", "--shave_cores", type=int, default=12,
                        help="input image size")
    parser.add_argument("-i", "--input_node", type=str, default='input',
                        help="input node name in the model")
    parser.add_argument("-o", "--output_node", type=str, default='output',
                        help="output node name in the model")
    return parser.parse_args()


if __name__ == '__main__':
    sdk_info_url = "https://raw.githubusercontent.com/movidius/ncsdk/master/install.sh"

    args = parse_args()

    sdk_file = args.ncs_sdk

    sdk_url = None
    if not os.path.exists(sdk_file):
        print("not found NCSDK file:", sdk_file, "trying to download...")
        sys.stdout.flush()
        data_dir = 'data'

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        install_file_name = os.path.basename(sdk_info_url)
        install_file = os.path.join(data_dir, install_file_name)
        download_file(sdk_info_url, install_file)
        for line in open(install_file):
            if line.startswith('ncsdk_link'):
                sdk_url = line.split('=')[1].strip()
                break
        if sdk_url is None:
            print("automatically finding sdk failed, please manually download sdk")
            print("by finding ncsdk file link in file:", sdk_info_url)
        else:
            sdk_file_name = os.path.basename(sdk_url)
            sdk_file = os.path.join(data_dir, sdk_file_name)
            download_file(sdk_url, sdk_file)
    else:
        print("found NCSDK file at:", sdk_file)
        sys.stdout.flush()
        data_dir = os.path.dirname(sdk_file)

    sdk_path = os.path.splitext(os.path.splitext(sdk_file)[0])[0]
    if not os.path.exists(sdk_path):
        tarfile.open(sdk_file, "r:gz").extractall(data_dir)
        print("Successfully extracted NCSDK {} to {}".format(sdk_file, data_dir))
    else:
        print("found NCSDK path at:", sdk_path)
    sys.stdout.flush()

    # may install pkg deps
    if not os.path.exists('/tmp/ncs_deps_checked'):
        print("checking package dependencies...")
        check_cmd = "sudo apt install -qq $(cat '{}/requirements_apt.txt') > /dev/null".format(sdk_path)
        subprocess.call(check_cmd, shell=True)
        sys.stdout.flush()

        print("checking python dependencies...")
        check_cmd = 'pip install -q -r {}/requirements.txt && pip install -q --upgrade -r requirements.txt'.format(sdk_path)
        subprocess.call(check_cmd, shell=True)
        print()
        sys.stdout.flush()
        open('/tmp/ncs_deps_checked', 'a').close()

    model_file = args.model
    if not os.path.exists(model_file):
        print(model_file, "not exist!")
        exit(-1)

    print('begin profiling', model_file, '...')

    bench_cmd = ['python', 'mvNCProfile.py', '-s', str(args.shave_cores),
                 os.path.abspath(model_file), '-in', args.input_node, '-on', args.output_node]
    subprocess.call(bench_cmd, cwd='{}/ncsdk-x86_64/tk'.format(sdk_path))
    print('all done.')
