#! /usr/bin/env python3
from __future__ import absolute_import
from __future__ import print_function

import argparse
import os

import tensorflow as tf


def check_frozen_graph(graph_file):
    if not os.path.exists(graph_file):
        print(graph_file, "does not exist!")
        exit(0)
    else:
        return graph_file


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("frozen_graph", type=check_frozen_graph,
                        default="data/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.frozen.pb",
                        help="model inference frozen graph")
    parser.add_argument("-i", "--input_node", type=str, default='input',
                        help="input node name in the model")
    parser.add_argument("-o", "--output_node", type=str, default='output',
                        help="output node name in the model")
    parser.add_argument("-s", "--image_size", type=int, default=224,
                        help="input image size")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    tf.logging.set_verbosity(tf.logging.INFO)
    model_dir = os.path.dirname(args.frozen_graph)

    model_name = os.path.splitext(os.path.basename(args.frozen_graph))[0]

    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(args.frozen_graph, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    with tf.Session(graph=graph) as sess:
        input_name = "import/" + args.input_node
        output_name = "import/" + args.output_node
        input_operation = graph.get_operation_by_name(input_name)
        output_operation = graph.get_operation_by_name(output_name)
        input_tensor = input_operation.outputs[0]
        output_tensor = output_operation.outputs[0]
        input_tensor.set_shape([1, args.image_size, args.image_size, 3])
        # print(input_tensor)
        # print(output_tensor)
        tf_lite_model = tf.contrib.lite.toco_convert(
            sess.graph_def, [input_tensor], [output_tensor])
        model_path = os.path.join(model_dir, '{}.tflite'.format(model_name))
        with tf.gfile.FastGFile(model_path, "wb") as f:
            f.write(tf_lite_model)
        print('{} frozen model converted to: {}'.format(model_name, os.path.abspath(model_path)))
