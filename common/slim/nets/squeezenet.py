from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

slim = tf.contrib.slim
trunc_normal = lambda stddev: tf.truncated_normal_initializer(0.0, stddev)


def squeezenet_arg_scope(weight_decay=0.0005):
    with slim.arg_scope([slim.conv2d, slim.fully_connected],
                        activation_fn=tf.nn.relu,
                        biases_initializer=tf.constant_initializer(0.1),
                        weights_regularizer=slim.l2_regularizer(weight_decay)):
        with slim.arg_scope([slim.conv2d], padding='SAME'):
            with slim.arg_scope([slim.max_pool2d], padding='VALID') as arg_sc:
                return arg_sc


def squeeze(inputs, num_outputs):
    return slim.conv2d(inputs, num_outputs, [1, 1], stride=1, scope='squeeze')


def expand(inputs, num_outputs):
    with tf.variable_scope('expand'):
        e1x1 = slim.conv2d(inputs, num_outputs, [1, 1], stride=1, scope='1x1')
        e3x3 = slim.conv2d(inputs, num_outputs, [3, 3], scope='3x3')
    return tf.concat([e1x1, e3x3], 3)


def fire_module(inputs,
                squeeze_depth,
                expand_depth,
                reuse=None,
                scope=None):
    with tf.variable_scope(scope, 'fire', [inputs], reuse=reuse):
        with slim.arg_scope([slim.conv2d, slim.max_pool2d],
                            outputs_collections=None):
            net = squeeze(inputs, squeeze_depth)
            outputs = expand(net, expand_depth)
            return outputs


def squeezenet(inputs,
               num_classes=1000,
               is_training=True,
               dropout_keep_prob=0.5,
               spatial_squeeze=True,
               scope='SqueezeNet'):
    """SqueezeNet.

    Args:
      inputs: a tensor of size [batch_size, height, width, channels].
      num_classes: the number of predicted classes. If 0 or None, the logits layer
      is omitted and the input features to the logits layer are returned instead.
      is_training: whether or not the model is being trained.
      dropout_keep_prob: the probability that activations are kept in the dropout
        layers during training.
      spatial_squeeze: whether or not should squeeze the spatial dimensions of the
        logits. Useful to remove unnecessary dimensions for classification.
      scope: Optional scope for the variables.

    Returns:
      net: the output of the logits layer (if num_classes is a non-zero integer),
        or the non-dropped-out input to the logits layer (if num_classes is 0
        or None).
      end_points: a dict of tensors with intermediate activations.
    """
    with tf.variable_scope(scope, 'SqueezeNet', [inputs]) as sc:
        end_points_collection = sc.original_name_scope + '_end_points'
        # Collect outputs for conv2d, fully_connected and max_pool2d.
        with slim.arg_scope([slim.conv2d, slim.max_pool2d],
                            outputs_collections=[end_points_collection]):
            net = slim.conv2d(inputs, 96, [7, 7], stride=2, scope='conv1')
            net = slim.max_pool2d(net, [3, 3], stride=2, scope='max_pool1')
            net = fire_module(net, 16, 64, scope='fire2')
            net = fire_module(net, 16, 64, scope='fire3')
            net = fire_module(net, 32, 128, scope='fire4')
            net = slim.max_pool2d(net, [2, 2], stride=2, scope='max_pool4')
            net = fire_module(net, 32, 128, scope='fire5')
            net = fire_module(net, 48, 192, scope='fire6')
            net = fire_module(net, 48, 192, scope='fire7')
            net = fire_module(net, 64, 256, scope='fire8')
            net = slim.max_pool2d(net, [3, 3], stride=2, scope='max_pool8')
            net = fire_module(net, 64, 256, scope='fire9')

            # Use conv2d instead of fully_connected layers.
            with slim.arg_scope([slim.conv2d],
                                weights_initializer=trunc_normal(0.005),
                                biases_initializer=tf.constant_initializer(0.1)):
                net = slim.dropout(net, dropout_keep_prob, is_training=is_training,
                                   scope='dropout6')

                # Convert end_points_collection into a end_point dict.
                end_points = slim.utils.convert_collection_to_dict(
                    end_points_collection)
                if num_classes:
                    net = slim.conv2d(net, num_classes, [1, 1], activation_fn=None, normalizer_fn=None, scope='conv10')
                    net = slim.avg_pool2d(net, net.get_shape()[1:3], scope='avg_pool10')
                    if spatial_squeeze:
                        net = tf.squeeze(net, [1, 2], name='logits')
                    end_points[sc.name + '/logits'] = net
            return net, end_points


squeezenet.default_image_size = 224
