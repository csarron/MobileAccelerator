#! /usr/bin/env python3
from __future__ import absolute_import
from __future__ import print_function

import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'common', 'slim'))
from nets import nets_factory
import tensorflow as tf


def run(args_):
    tf.logging.set_verbosity(tf.logging.INFO)
    checkpoint_file = args_.checkpoint_file
    model_dir = os.path.dirname(checkpoint_file)
    model_name = args_.model
    with tf.Graph().as_default() as graph:
        network_fn = nets_factory.get_network_fn(
            model_name,
            num_classes=(args_.num_classes - args_.labels_offset),
            is_training=False)
        image_size = args_.image_size or network_fn.default_image_size
        placeholder = tf.placeholder(name="input", dtype=tf.float32,
                                     shape=[1, image_size, image_size, 3])
        logits, _ = network_fn(placeholder)
        tf.nn.softmax(logits, name='output')
        sess = tf.Session(graph=graph)
        saver = tf.train.Saver(tf.global_variables())
        saver.restore(sess, checkpoint_file)
        model_path = os.path.join(model_dir, 'ncs_{}'.format(model_name))
        saver.save(sess, model_path)
        print('{} model meta file saved to: {}.meta'.format(model_name, os.path.abspath(model_path)))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--checkpoint_file", type=str,
                        help="a TensorFlow model checkpoint file")
    parser.add_argument("-m", "--model", type=str, default="mobilenet_v2",
                        help="network type")
    parser.add_argument("-s", "--image_size", type=int, default=224,
                        help="input image size")
    parser.add_argument("-n", "--num_classes", type=int, default=1001,
                        help="number of classification classes")
    parser.add_argument("-l", "--labels_offset", type=int, default=0,
                        help="An offset for the labels in the dataset. This flag is primarily used "
                             "to  evaluate the VGG and ResNet architectures which do not use a"
                             " background class for the ImageNet dataset.")

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    run(args)
