from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

slim = tf.contrib.slim
from nets import squeezenet

two_squeezenet_arg_scope = squeezenet.squeezenet_arg_scope


def two_squeezenet(inputs,
                   num_classes=1000,
                   is_training=True,
                   dropout_keep_prob=0.5,
                   spatial_squeeze=True,
                   scope='TwoNet'):
    with tf.variable_scope(scope) as sc:
        end_points_collection = sc.original_name_scope + '_end_points'
        end_points = slim.utils.convert_collection_to_dict(
            end_points_collection)
        net1, end_points1 = squeezenet.squeezenet(inputs, num_classes, is_training,
                                                  dropout_keep_prob, spatial_squeeze,
                                                  'net1')
        end_points[sc.name + '/net1'] = net1

        net2, end_points2 = squeezenet.squeezenet(inputs, num_classes, is_training,
                                                  dropout_keep_prob, spatial_squeeze,
                                                  'net2')
        end_points[sc.name + '/net2'] = net2
        net = (net1 + net2) / 2
        end_points[sc.name + '/final'] = net
        return net, end_points


two_squeezenet.default_image_size = 224
