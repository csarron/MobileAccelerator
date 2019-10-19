#!/usr/bin/env python
"""
 Copyright (C) 2018-2019 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
from __future__ import print_function
import sys
import os
from argparse import ArgumentParser, SUPPRESS
import cv2
import numpy as np
import logging as log
from time import time
from openvino.inference_engine import IENetwork, IEPlugin


def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument("-m", "--model", help="Required. Path to an .xml file with a trained model.", required=True,
                      type=str)
    args.add_argument("-i", "--input", help="Required. Path to a folder with images or path to an image files",
                      required=True,
                      type=str, nargs="+")
    args.add_argument("-l", "--cpu_extension",
                      help="Optional. Required for CPU custom layers. "
                           "MKLDNN (CPU)-targeted custom layers. Absolute path to a shared library with the"
                           " kernels implementations.", type=str, default=None)
    args.add_argument("-pp", "--plugin_dir", help="Optional. Path to a plugin folder", type=str, default=None)
    args.add_argument("-d", "--device",
                      help="Optional. Specify the target device to infer on; CPU, GPU, FPGA, HDDL, MYRIAD or HETERO: is "
                           "acceptable. The sample will look for a suitable plugin for device specified. Default "
                           "value is CPU",
                      default="CPU", type=str)
    args.add_argument("--labels", help="Optional. Path to a labels mapping file", default=None, type=str)
    args.add_argument("-nt", "--number_top", help="Optional. Number of top results", default=10, type=int)
    args.add_argument("-ni", "--number_iter", help="Optional. Number of inference iterations", default=1, type=int)
    args.add_argument("-pc", "--perf_counts", help="Optional. Report performance counters", default=False,
                      action="store_true")
    parser.add_argument("-of", "--output_file", type=str, default=0,
                        help="Output file for results")
    parser.add_argument("-1", "--cust_arg_1", type=int, default=0,
                        help="Custom argument 1")
    parser.add_argument("-2", "--cust_arg_2", type=int, default=0,
                        help="Custom argument 2")
    parser.add_argument("-384", "--new_384_depth", type=int, default=0,
                        help="new_384_depth")

    return parser


def main():
    # log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
    args = build_argparser().parse_args()

    log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO,
        filename=args.output_file + '.log')

    model_xml = args.model
    model_bin = os.path.splitext(model_xml)[0] + ".bin"

    # Plugin initialization for specified device and load extensions library if specified
    plugin = IEPlugin(device=args.device, plugin_dirs=args.plugin_dir)
    # Read IR
    log.info("Loading network files:\n\t{}\n\t{}".format(model_xml, model_bin))
    net = IENetwork(model=model_xml, weights=model_bin)

    assert len(net.inputs.keys()) == 1, "Sample supports only single input topologies"
    assert len(net.outputs) == 1, "Sample supports only single output topologies"

    log.info("Preparing input blobs")
    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))
    net.batch_size = len(args.input)

    # Read and pre-process input images
    n, c, h, w = net.inputs[input_blob].shape
    images = np.ndarray(shape=(n, c, h, w))
    for i in range(n):
        image = cv2.imread(args.input[i])
        if image.shape[:-1] != (h, w):
            log.warning("Image {} is resized from {} to {}".format(args.input[i], image.shape[:-1], (h, w)))
            image = cv2.resize(image, (w, h))
        image = image.transpose((2, 0, 1))  # Change data layout from HWC to CHW
        images[i] = image
    log.info("Batch size is {}".format(n))

    # Loading model to the plugin
    log.info("Loading model to the plugin")
    exec_net = plugin.load(network=net)

    # Start sync inference
    log.info("Starting inference ({} iterations)".format(args.number_iter))
    infer_time = []
    for i in range(args.number_iter):
        t0 = time()
        res = exec_net.infer(inputs={input_blob: images})
        infer_time.append((time() - t0) * 1000)

    average_total_time = np.average(np.asarray(infer_time))
    log.info("Average running time of one iteration: {} ms".format(average_total_time))

    specific_layer_time = 0
    partial_layer_time = 0
    total_execution_time = 0

    if args.perf_counts:
        output_file = open(args.output_file, 'a+')
        perf_counts = exec_net.requests[0].get_perf_counts()
        log.info("Performance counters:")
        print("{:<70} {:<15} {:<15} {:<15} {:<10}".format('name', 'layer_type', 'exet_type', 'status', 'real_time, us'))

        for layer, stats in perf_counts.items():
            # log_content = "{:<70} {:<15} {:<15} {:<15} {:<10}".format(layer, stats['layer_type'],
            #     stats['exec_type'], stats['status'], stats['real_time'])
            log_content = "{}\t{}\t{}\t{}\t{}".format(layer, stats['layer_type'],
                stats['exec_type'], stats['status'], stats['real_time'])
            print(log_content)
            log.info(log_content)

            #if stats['layer_type'] == 'Convolution' and stats['exec_type'] == 'MyriadXHwOp':
            total_execution_time += stats['real_time']
            # output_file.write(layer + '\t' + str(stats['real_time']) + '\n')

            if 'AlexandruIrimiea2/Conv/Conv2D' in layer or 'AlexandruIrimiea3/Conv/Conv2D' in layer:
                # result1 = str(args.cust_arg_1) + '= ' + str(stats['real_time']) + '\n'
                specific_layer_time += stats['real_time']

                if 'injected' not in layer:
                    partial_layer_time += stats['real_time']

    # output_file.write('Total_layer_execution_time_alex\t' + str(total_execution_time) + '\n')

    output_file.write(str(args.cust_arg_2) + '\t' + str(args.cust_arg_1) +'\t' + str(specific_layer_time/1000.0) +'\t' + str(partial_layer_time/1000.0) + '\t' + str(average_total_time) + '\t' + str(total_execution_time/1000.0) + '\n')

    #output_file.write(str(args.new_384_depth) + '\t' + str(total_execution_time/1000) +'\t' + str(average_total_time) + '\n')

if __name__ == '__main__':
    sys.exit(main() or 0)
