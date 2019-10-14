import os
import sys
import logging as log
from argparse import ArgumentParser, SUPPRESS
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K, datasets, layers, models

from openvino.inference_engine import IENetwork, IEPlugin

from ncs_util import *

slim = tf.contrib.slim

# def build_argparser():
#     parser = ArgumentParser(add_help=False)
#     args = parser.add_argument_group('Options')
#     args.add_argument('-h', '--help', action='help', default=SUPPRESS,
#         help='Show this help message and exit.')
#     args.add_argument("-o", '--dir', required=True, type=str)
#     args.add_argument("-k", '--kernel_sizes', type=int)
#     args.add_argument("-i", '--input_size', type=int)

#     return parser

# def create_model(input_h, input_w, kernel_h, kernel_w):
#     model = tf.keras.models.Sequential()
#     model.add(layers.Conv2D(32, (kernel_h, kernel_w),
#         input_shape=(input_h, input_w, 3)))

#     model.compile(optimizer=tf.keras.optimizers.Adam(),
#         loss=tf.keras.losses.sparse_categorical_crossentropy, metrics=['accuracy'])

#     return model

def generate_models(min, max, step):
    for kernel_size in range(min, max, step):
        model_name = 'model_input' + str(28) + 'x' + str(28) \
            + '_filter' + str(kernel_size) + 'x' + str(kernel_size) + '.pb'

        # model = create_model(args.input_size, args.input_size, kernel_size, kernel_size)
        # model = create_model(28, 28, kernel_size, kernel_size)



        frozen_graph = freeze_session(K.get_session(), output_names=[out.op.name
             for out in model.outputs])
        tf.train.write_graph(frozen_graph, output_dir, model_name, as_text=False)

def generate_model1():
    model = tf.keras.models.Sequential()
    model.add(layers.Conv2D(256, (3, 3), input_shape=(224, 224, 3)))

    model.compile(optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.sparse_categorical_crossentropy, metrics=['accuracy'])

    frozen_graph = freeze_session(K.get_session(), output_names=[out.op.name
            for out in model.outputs])

    tf.train.write_graph(frozen_graph, 'small_nets', 'model1.pb', as_text=False)
    convert_model('small_nets/model1.pb')

def main():
    # log.getLogger().setLevel(log.INFO)
    # log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
    # args = build_argparser().parse_args()
    # generate_models(2, 3, 1)
    generate_model1()

if __name__ == '__main__':
    sys.exit(main() or 0)