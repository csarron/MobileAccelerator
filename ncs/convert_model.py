#! /usr/bin/env python3
from __future__ import absolute_import
from __future__ import print_function

import argparse
import os

import tensorflow as tf
from tensorflow.core.framework import graph_pb2
from tensorflow.python import pywrap_tensorflow
from tensorflow.python.training import saver as saver_lib


def run(args_):
    tf.logging.set_verbosity(tf.logging.INFO)
    checkpoint_file = args_.checkpoint_file
    model_dir = os.path.dirname(checkpoint_file)
    if not saver_lib.checkpoint_exists(checkpoint_file):
        print("Checkpoint file", checkpoint_file, "doesn't exist!")
        exit(-1)

    model_name = os.path.splitext(os.path.basename(args_.checkpoint_file))[0]
    with tf.Session() as sess:
        input_graph_def = graph_pb2.GraphDef()
        with tf.gfile.FastGFile(args_.inference_graph, "rb") as f:
            input_graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(input_graph_def, name="")

        var_list = {}
        reader = pywrap_tensorflow.NewCheckpointReader(checkpoint_file)
        var_to_shape_map = reader.get_variable_to_shape_map()
        for key in var_to_shape_map:
            try:
                tensor = sess.graph.get_tensor_by_name(key + ":0")
            except KeyError:
                # This tensor doesn't exist in the graph (for example it's
                # 'global_step' or a similar housekeeping element) so skip it.
                continue
            var_list[key] = tensor
        saver = saver_lib.Saver(var_list=var_list)

        saver.restore(sess, checkpoint_file)

        model_path = os.path.join(model_dir, 'ncs_{}'.format(model_name))
        saver.save(sess, model_path)
        print('{} model meta file saved to: {}.meta'.format(model_name, os.path.abspath(model_path)))


def check_inference_graph(inf_graph_file):
    script = "python common/slim/export_inference_graph.py  --model_name mobilenet_v2_1.0 "
    params = "--image_size 224 --output_file data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb"
    usage = script + params

    if not os.path.exists(inf_graph_file):
        print(inf_graph_file, "does not exist! example for generating mobilenet_v2_1.0 inference graph is:")
        print(usage)
        exit(0)
    else:
        return inf_graph_file


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--checkpoint_file", type=str,
                        default="data/mobilenet_v2_1.0/mobilenet_v2_1.0_224.ckpt",
                        help="a TensorFlow model checkpoint file")
    parser.add_argument('-g', "--inference_graph", type=check_inference_graph,
                        default="data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb",
                        help="model inference graph")

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    run(args)
