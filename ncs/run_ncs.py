#! /usr/bin/env python3
from __future__ import absolute_import
from __future__ import print_function
import argparse
import os
import platform
import zipfile as zp
import subprocess
import shutil
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
    parser.add_argument("-p3", "--python3", type=str, default="python3",
                        help="Python 3 path, better to use virtualenv python3")
    parser.add_argument("-m", "--model", type=str, default="data/mobilenet_v2_1.0/ncs_mobilenet_v2_1.0.meta",
                        help="frozen tensorflow model")
    parser.add_argument("-s", "--shave_cores", type=int, default=12,
                        help="input image size")
    parser.add_argument("-i", "--input_node", type=str, default='input',
                        help="input node name in the model")
    parser.add_argument("-o", "--output_node", type=str, default='output',
                        help="output node name in the model")
    return parser.parse_args()


if __name__ == '__main__':
    sdk_info_url = "https://github.com/movidius/ncsdk/archive/master.zip"

    args = parse_args()

    sdk_file = args.ncs_sdk
    sdk_path = os.path.splitext(os.path.splitext(sdk_file)[0])[0]

    sdk_url = None
    if not os.path.exists(sdk_file):
        print("Not found NCSDK file:", sdk_file, "trying to download...")
        sys.stdout.flush()
        data_dir = 'data'

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        api_zip_file_name = os.path.basename(sdk_info_url)
        api_zip_file = os.path.join(data_dir, api_zip_file_name)

        if not os.path.exists(api_zip_file):
            download_file(sdk_info_url, api_zip_file)

        print("Extracting NCSDK api zip to:", data_dir, "...")
        zp_ref = zp.ZipFile(api_zip_file, 'r')
        zp_ref.extractall(data_dir)
        zp_ref.close()
        print("NCSDK api extraction done.")
        install_file = os.path.join(data_dir, 'ncsdk-master', 'install.sh')
        for line in open(install_file):
            if line.startswith('ncsdk_link'):
                sdk_url = line.split('=')[1].strip()
                break
        if sdk_url is None:
            print("Automatically finding sdk failed, please manually download sdk")
            print("by finding ncsdk file link in file:", sdk_info_url)
            exit(-1)
        else:
            sdk_file_name = os.path.basename(sdk_url)
            sdk_file = os.path.join(data_dir, sdk_file_name)
            download_file(sdk_url, sdk_file)
    else:
        print("Found NCSDK file at:", sdk_file)
        sys.stdout.flush()
        data_dir = os.path.dirname(sdk_file)

    if not os.path.exists(sdk_path):
        tarfile.open(sdk_file, "r:gz").extractall(data_dir)
        print("Successfully extracted NCSDK {} to {}".format(sdk_file, data_dir))
    else:
        print("Found NCSDK path at:", sdk_path)
    sys.stdout.flush()

    # may install api and package dependencies
    sdk_name = os.path.basename(sdk_path)
    if not os.path.exists('/tmp/{}_api_checked'.format(sdk_name)):
        os_name = platform.system()
        api_dir = "ncs/api_demo"
        if os_name == "Linux":
            print("Installing package dependencies for Linux...")
            sys.stdout.flush()

            check_cmd = "sudo apt install -qq $(cat '{}/requirements_apt.txt') > /dev/null".format(sdk_path)
            subprocess.call(check_cmd, shell=True)

            check_cmd = "sudo apt install libusb-1.0-0-dev"
            subprocess.call(check_cmd, shell=True)

            # need to set usb permission
            check_cmd = "sudo mkdir -p /etc/udev/rules.d/ && "
            check_cmd += "sudo cp {}/api/97-usbboot.rules /etc/udev/rules.d/".format(api_dir)
            subprocess.call(check_cmd, shell=True)

            check_cmd = "sudo udevadm control --reload-rules && sudo udevadm trigger"
            subprocess.call(check_cmd, shell=True)

        elif os_name == "Darwin":
            print("Installing package dependencies (libusb) for macOS through Homebrew...")
            sys.stdout.flush()

            check_cmd = "brew install libusb".format(sdk_path)
            subprocess.call(check_cmd, shell=True)

        else:
            print("Only Linux and macOS are supported yet!")
            exit(-1)

        print("Building ncs api for {}...".format(os_name))
        sys.stdout.flush()

        build_dir = os.path.join(api_dir, "{}_build".format(os_name))
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        build_api_cmd = "cmake .. && make ".format(build_dir)
        subprocess.call(build_api_cmd, shell=True, cwd=build_dir)

        copy_api_cmd = "cp {0}/mvncapi.py {0}/mvnc".format(build_dir)
        subprocess.call(copy_api_cmd, shell=True)

        mvnc_lib_name = "libmvnc.dylib" if os_name == "Darwin" else "libmvnc.so"
        copy_cmd = "cp -rf {0}/mvnc {0}/{1} {2}/ncsdk-x86_64/tk".format(build_dir, mvnc_lib_name, sdk_path)
        subprocess.call(copy_cmd, shell=True)

        if not os.path.exists('/tmp/{}_py_checked'.format(sdk_name)):
            print("Installing python dependencies...")
            sys.stdout.flush()
            pip_path = os.path.join(os.path.dirname(args.python3), 'pip')
            if not os.path.exists(pip_path):
                pip_path = 'pip3'

            check_cmd = '{0} install -r {1}/requirements.txt && {0} install --upgrade -r requirements.txt'.format(
                pip_path,
                sdk_path)

            subprocess.call(check_cmd, shell=True)
            print()
            sys.stdout.flush()
            open('/tmp/{}_py_checked'.format(sdk_name), 'a').close()

        open('/tmp/{}_api_checked'.format(sdk_name), 'a').close()

    model_file = args.model
    if not os.path.exists(model_file):
        print(model_file, "not exist!")
        exit(-1)

    print('Begin profiling', model_file, '...')

    bench_cmd = [args.python3, 'mvNCProfile.py', '-s', str(args.shave_cores),
                 os.path.abspath(model_file), '-in', args.input_node, '-on', args.output_node]
    subprocess.call(bench_cmd, cwd='{}/ncsdk-x86_64/tk'.format(sdk_path))

    report_file = model_file.replace('.meta', '_report.html')
    shutil.copy('{}/ncsdk-x86_64/tk/output_report.html'.format(sdk_path), report_file)

    graph_file = model_file.replace('.meta', '.graph')
    shutil.copy('{}/ncsdk-x86_64/tk/graph'.format(sdk_path), graph_file)

    print('Model graph copied to\033[32m', os.path.abspath(graph_file), '\033[0m')
    print('Profiling report copied to\033[32m', os.path.abspath(report_file), '\033[0m')
    print('All done.')
