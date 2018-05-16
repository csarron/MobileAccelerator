#! /usr/bin/env python3
from __future__ import absolute_import
from __future__ import print_function

import argparse
import os

import tensorflow as tf
from tensorflow.core.framework import attr_value_pb2
from tensorflow.python.framework import tensor_util
import numpy as np
from google.protobuf import text_format

from tensorflow.core.framework import graph_pb2
from tensorflow.python import pywrap_tensorflow
from tensorflow.python.training import saver as saver_lib


def check_frozen_graph(graph_file):
    if not os.path.exists(graph_file):
        print(graph_file, "does not exist!")
        exit(0)
    else:
        return graph_file


def prune_weights(inf_graph, threshold):
    how_many_converted = 0
    out_graph_def = tf.GraphDef()
    for input_node in inf_graph.node:
        output_node = out_graph_def.node.add()
        output_node.MergeFrom(input_node)

        if output_node.op == 'Const':
            tensor_proto = output_node.attr['value'].tensor
            if tensor_proto.tensor_content:
                np_array = tensor_util.MakeNdarray(tensor_proto)
                np_array[np.abs(np_array) < threshold] = 0
                hp_tensor_proto = tensor_util.make_tensor_proto(np_array)
                output_node.attr["value"].CopyFrom(attr_value_pb2.AttrValue(tensor=hp_tensor_proto))
                how_many_converted += 1
    print("pruned %d nodes to zero." % how_many_converted)
    return out_graph_def


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("frozen_graph", type=check_frozen_graph,
                        help="model inference frozen graph")
    parser.add_argument("-i", "--input_node", type=str, default='input',
                        help="input node name in the model")
    parser.add_argument("-o", "--output_node", type=str, default='output',
                        help="output node name in the model")
    parser.add_argument("-s", "--image_size", type=int, default=224,
                        help="input image size")
    parser.add_argument("-t", "--threshold", type=int, default=1e-3,
                        help="model weights threshold")
    parser.add_argument("-r", "--prune_ratio", type=float, default=0.5,
                        help="prune_ratio")
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

    out_graph_def = prune_weights(graph_def, args.threshold)

    model_path = os.path.join(model_dir, '{}.pruned.pb'.format(model_name))
    with tf.gfile.FastGFile(model_path, "wb") as f:
        # if as_text:
        #     f.write(str(out_graph_def))
        # else:
        f.write(out_graph_def.SerializeToString())
        print('{} pruned model converted to: {}'.format(model_name, os.path.abspath(model_path)))

    # with graph.as_default():
    #     tf.import_graph_def(out_graph_def)
    #
    # with tf.Session(graph=graph) as sess:
    #     _ = tf.import_graph_def(input_graph_def, name="")
    #
    #     var_list = {}
    #     reader = pywrap_tensorflow.NewCheckpointReader(checkpoint_file)
    #     var_to_shape_map = reader.get_variable_to_shape_map()
    #     for key in var_to_shape_map:
    #         try:
    #             tensor = sess.graph.get_tensor_by_name(key + ":0")
    #         except KeyError:
    #             # This tensor doesn't exist in the graph (for example it's
    #             # 'global_step' or a similar housekeeping element) so skip it.
    #             continue
    #         var_list[key] = tensor
    #     saver = saver_lib.Saver(var_list=var_list)
    #
    #     model_path = os.path.join(model_dir, 'ncs_{}'.format(model_name))
    #     saver.save(sess, model_path)
    #     print('{} model meta file saved to: {}.meta'.format(model_name, os.path.abspath(model_path)))
