#! /usr/bin/env python3

# Copyright 2017 Intel Corporation.
# The source code, information and material ("Material") contained herein is
# owned by Intel Corporation or its suppliers or licensors, and title to such
# Material remains with Intel Corporation or its suppliers or licensors.
# The Material contains proprietary information of Intel or its suppliers and
# licensors. The Material is protected by worldwide copyright laws and treaty
# provisions.
# No part of the Material may be used, copied, reproduced, modified, published,
# uploaded, posted, transmitted, distributed or disclosed in any way without
# Intel's prior express written permission. No license under any patent,
# copyright or other intellectual property rights in the Material is granted to
# or conferred upon you, either expressly, by implication, inducement, estoppel
# or otherwise.
# Any license under such intellectual property rights must be express and
# approved by Intel in writing.

import mvncapi as mvnc
import argparse
import os
import numpy as np
from PIL import Image


def __create_mean_raw(img_raw, mean_rgb):
    if img_raw.shape[2] < 3:
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
    return mean_raw.astype(np.float16)


def process_image(image_data, image_size, mean_rgb_, std_):
    # center crop to square
    width, height = image_data.size
    short_dim = min(height, width)
    crop_coord = (
        (width - short_dim) / 2,
        (height - short_dim) / 2,
        (width + short_dim) / 2,
        (height + short_dim) / 2
    )
    cropped_image = image_data.crop(crop_coord)
    rescaled_image = cropped_image.resize((image_size, image_size), Image.ANTIALIAS)
    image_array = np.array(rescaled_image)  # read it
    mean_raw = __create_mean_raw(image_array, mean_rgb_)
    scaled_image_array = image_array - mean_raw
    scaled_image_array = scaled_image_array.astype(np.float16)
    # scalar test_resources divide
    scaled_image_array *= std_
    return scaled_image_array


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--graph_file", type=str, default='mobilenet_v1.graph',
                        help="a ncs model graph file")
    parser.add_argument("-i", "--image_file", type=str, default='keyboard.jpg',
                        help="input image size")
    parser.add_argument("-l", "--label_file", type=str, default='labels.txt',
                        help="input image size")
    parser.add_argument("-p", "--processing_style", choices=("inception", "vgg"), default="inception",
                        help="image processing style")
    parser.add_argument("-s", "--image_size", type=int, default=224,
                        help="input image size")

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    # mvnc.SetGlobalOption(mvnc.GlobalOption.LOGLEVEL, 2)
    devices = mvnc.EnumerateDevices()
    if len(devices) == 0:
        print('No devices found')
        quit()

    graph_filename = args.graph_file
    image_filename = args.image_file
    labels_filename = args.label_file

    for filename in [graph_filename, image_filename, labels_filename]:
        if not os.path.exists(filename):
            print(filename, 'not exist!')
            quit(-1)

    # Load categories
    image_classes = []
    with open(labels_filename, 'r') as f:
        for line in f:
            cat = line.split('\n')[0]
            image_classes.append(cat)
        print('Number of image classes:', len(image_classes) - 1)

    # Processing image
    if args.processing_style == 'inception':
        mean = 128
        std = 1 / 128
        mean_rgb = (mean, mean, mean)
        label_offset = 0
    else:
        std = 1.0
        mean_rgb = (0, 0, 0)
        label_offset = 1
        # mean_rgb = (123.68, 116.78, 103.94)

    src_img = Image.open(image_filename)
    # If black and white image, convert to rgb (all 3 channels the same)
    if len(np.shape(src_img)) == 2:
        src_img = src_img.convert(mode='RGB')

    processed_image = process_image(src_img, args.image_size, mean_rgb, std)

    model_name = os.path.splitext(os.path.split(graph_filename)[1])[0]

    device = mvnc.Device(devices[0])
    device.OpenDevice()

    # Load graph
    with open(graph_filename, mode='rb') as f:
        graph_file = f.read()

    graph = device.AllocateGraph(graph_file)

    print('Transfer image to NCS...')
    graph.LoadTensor(processed_image, 'user object')
    output, user_obj = graph.GetResult()
    time_taken = graph.GetGraphOption(mvnc.GraphOption.TIME_TAKEN)
    inference_time = np.sum(time_taken)
    graph.DeallocateGraph()
    device.CloseDevice()

    top_indices = output.argsort()[::-1][:5]

    print('Running inference on NCS using', model_name)
    print()
    print("Top5 predictions are:")

    for i in range(5):
        print(top_indices[i] + label_offset, ',',
              image_classes[top_indices[i] + label_offset].split(',')[0], ',',
              output[top_indices[i]])

    print()
    print('Inference time is:', inference_time, 'ms')
