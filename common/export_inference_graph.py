# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""Saves out a GraphDef containing the architecture of the model.

To use it, run something like this, with a model name defined by slim:

bazel build tensorflow_models/research/slim:export_inference_graph
bazel-bin/tensorflow_models/research/slim/export_inference_graph \
--model_name=inception_v3 --output_file=/tmp/inception_v3_inf_graph.pb

If you then want to use the resulting model with your own or pretrained
checkpoints as part of a mobile model, you can run freeze_graph to get a graph
def with the variables inlined as constants using:

bazel build tensorflow/python/tools:freeze_graph
bazel-bin/tensorflow/python/tools/freeze_graph \
--input_graph=/tmp/inception_v3_inf_graph.pb \
--input_checkpoint=/tmp/checkpoints/inception_v3.ckpt \
--input_binary=true --output_graph=/tmp/frozen_inception_v3.pb \
--output_node_names=InceptionV3/Predictions/Reshape_1

The output node names will vary depending on the model, but you can inspect and
estimate them using the summarize_graph tool:

bazel build tensorflow/tools/graph_transforms:summarize_graph
bazel-bin/tensorflow/tools/graph_transforms/summarize_graph \
--in_graph=/tmp/inception_v3_inf_graph.pb

To run the resulting graph in C++, you can look at the label_image sample code:

bazel build tensorflow/examples/label_image:label_image
bazel-bin/tensorflow/examples/label_image/label_image \
--image=${HOME}/Pictures/flowers.jpg \
--input_layer=input \
--output_layer=InceptionV3/Predictions/Reshape_1 \
--graph=/tmp/frozen_inception_v3.pb \
--labels=/tmp/imagenet_slim_labels.txt \
--input_mean=0 \
--input_std=255

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

import tensorflow as tf
from tensorflow.python.platform import gfile

import nets_factory

slim = tf.contrib.slim


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model_name", type=str, required=True,
                        help="network type")
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="network type")
    parser.add_argument("-s", "--image_size", type=int, default=224,
                        help="input image size")
    parser.add_argument("-n", "--num_classes", type=int, default=1001,
                        help="number of classification classes")
    parser.add_argument("-l", "--labels_offset", type=int, default=0,
                        help="An offset for the labels in the dataset. This flag is primarily used "
                             "to  evaluate the VGG and ResNet architectures which do not use a"
                             " background class for the ImageNet dataset.")
    parser.add_argument("-1", "--cust_arg_1", type=int, default=0,
                        help="Custom argument 1")
    parser.add_argument("-2", "--cust_arg_2", type=int, default=0,
                        help="Custom argument 2")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    if not args.output_file:
        raise ValueError('You must supply the path to save to with --output_file')
    # tf.logging.set_verbosity(tf.logging.INFO)
    model_name = args.model_name
    depth_multiplier_dict = {}
    with tf.Graph().as_default() as graph:
        # handle mobilenet depth multiplier from model name
        if model_name.startswith('mobilenet'):
            name_parts = model_name.split('_')
            depth = float(name_parts[-1])
            depth_multiplier_dict = {'depth_multiplier': depth}
            model_name = '_'.join(name_parts[:-1])
        print("generating inference graph for model:", model_name, "depth_multiplier:", depth_multiplier_dict)
        network_fn = nets_factory.get_network_fn(model_name,
                                                 num_classes=(args.num_classes - args.labels_offset),
                                                 is_training=False,
                                                 cust_arg_1=args.cust_arg_1,
                                                 cust_arg_2=args.cust_arg_2)
        image_size = args.image_size or network_fn.default_image_size
        placeholder = tf.placeholder(name='input', dtype=tf.float32,
                                     shape=[None, image_size, image_size, 3])

        logits, _ = network_fn(placeholder, **depth_multiplier_dict)
        tf.nn.softmax(logits, name='output')
        graph_def = graph.as_graph_def()
        inf_graph_def = tf.graph_util.extract_sub_graph(graph_def, ['output'])
        with gfile.GFile(args.output_file, 'wb') as f:
            f.write(inf_graph_def.SerializeToString())
        print("inference graph saved to: ", args.output_file)
