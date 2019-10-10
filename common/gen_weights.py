#! /usr/bin/env python3
import argparse

import tensorflow as tf

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
                        help="Custom argument")
    parser.add_argument("-2", "--cust_arg_2", type=int, default=0,
                        help="Custom argument 2")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    model_name = args.model_name
    print("generating weights/checkpoint for model:", model_name)
    with tf.Session() as sess:
        network_fn = nets_factory.get_network_fn(model_name,
                                                 num_classes=(args.num_classes - args.labels_offset),
                                                 is_training=False,
                                                 cust_arg_1=args.cust_arg_1,
                                                 cust_arg_2=args.cust_arg_2)
        image_size = args.image_size or network_fn.default_image_size
        placeholder = tf.placeholder(name='input', dtype=tf.float32,
                                     shape=[None, image_size, image_size, 3])

        logits, _ = network_fn(placeholder)
        tf.nn.softmax(logits, name='output')
        sess.run(tf.global_variables_initializer())

        saver = tf.train.Saver()
        saver.save(sess, args.output_file)
        # graph_def = graph.as_graph_def()
        # inf_graph_def = tf.graph_util.extract_sub_graph(graph_def, ['output'])
        # with gfile.GFile(args.output_file, 'wb') as f:
        #     f.write(inf_graph_def.SerializeToString())
        print("model checkpoint saved to: ", args.output_file)
