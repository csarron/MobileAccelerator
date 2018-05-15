#! /usr/bin/env python3
import argparse

import tensorflow as tf

import nets_factory

slim = tf.contrib.slim


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model_name", type=str, required=True,
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
    model_name = args.model_name
    print("printing stats for model:", model_name)
    run_meta = tf.RunMetadata()

    with tf.Session() as sess:
        network_fn = nets_factory.get_network_fn(model_name,
                                                 num_classes=(args.num_classes - args.labels_offset),
                                                 is_training=False)
        image_size = args.image_size or network_fn.default_image_size
        placeholder = tf.placeholder(name='input', dtype=tf.float32,
                                     shape=[1, image_size, image_size, 3])

        logits, _ = network_fn(placeholder)
        tf.nn.softmax(logits, name='output')
        # sess.run(tf.global_variables_initializer())
        opts = tf.profiler.ProfileOptionBuilder.float_operation()
        flops = tf.profiler.profile(sess.graph, run_meta=run_meta, cmd='op', options=opts)

        opts = tf.profiler.ProfileOptionBuilder.trainable_variables_parameter()
        params = tf.profiler.profile(sess.graph, run_meta=run_meta, cmd='op', options=opts)

        print("\n\n")
        print("{:5.1f} million FLOPs, {:5.2f} million params".format(flops.total_float_ops/1e6, params.total_parameters/1e6))
        print("\n\n")
