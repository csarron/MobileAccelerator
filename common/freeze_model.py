import argparse
import os
import tensorflow as tf
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import tensor_util
from tensorflow.python.tools.optimize_for_inference_lib import optimize_for_inference
from tensorflow.python.training import saver as saver_lib
from tensorflow.python import pywrap_tensorflow


def freeze_graph(checkpoint_file_, input_node_names, output_node_names, inference_graph=None):
    """
    freeze model from TensorFlow checkpoint file
    :param checkpoint_file_: TensorFlow checkpoint file
    :param input_node_names: specify model input node names, separated by comma
    :param output_node_names: specify model output node names, separated by comma
    :param inference_graph: optional inference graph file, if not given, automatically use meta graph
    :return: an optimized inference graph def object, which can be saved to disk
    or for further processing (e.g., removing weights or inspecting nodes)
    """
    if not saver_lib.checkpoint_exists(checkpoint_file_):
        print("Checkpoint file '" + checkpoint_file_ + "' doesn't exist!")
        exit(-1)

    sess = tf.Session()
    if not inference_graph:
        meta_graph_file = "{}.meta".format(checkpoint_file_)
        if not os.path.exists(meta_graph_file):
            print("meta graph def:{} must exist if not given inference graph def".format(meta_graph_file))
            exit(-1)
        saver = tf.train.import_meta_graph(checkpoint_file_ + '.meta', clear_devices=True)
    else:
        if not os.path.exists(inference_graph):
            print("inference graph def:{} not exists".format(inference_graph))
            exit(-1)

        input_graph_def = tf.GraphDef()
        with tf.gfile.FastGFile(inference_graph, "rb") as f:
            input_graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(input_graph_def, name="")
        var_list = {}
        reader = pywrap_tensorflow.NewCheckpointReader(checkpoint_file_)
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

    model = os.path.splitext(os.path.basename(checkpoint_file_))[0]

    graph = tf.get_default_graph()
    input_graph_def = graph.as_graph_def()
    # for node in input_graph_def.node:
    #     print("node:{}, op:{}, input:{}".format(node.name, node.op, node.input))
    saver.restore(sess, checkpoint_file_)
    print("{} model restored".format(model))
    output_graph_def = graph_util.convert_variables_to_constants(
        sess,  # The session is used to retrieve the weights
        input_graph_def,  # The graph_def is used to retrieve the nodes
        output_node_names=output_node_names.split(",")  # The output node names are used to select the useful nodes
    )

    # optimize graph
    output_graph_def = optimize_for_inference(output_graph_def, input_node_names.split(","),
                                              output_node_names.split(","),
                                              dtypes.float32.as_datatype_enum)
    print("%d ops in the final graph." % len(output_graph_def.node))
    return output_graph_def


def save_graph(graph_def, output_path, as_text):
    with tf.gfile.GFile(output_path, "wb") as f:
        if as_text:
            out_graph_def = convert_weights(graph_def)
            f.write(str(out_graph_def))
        else:
            f.write(graph_def.SerializeToString())


def save_weights(graph_def_, output_file_):
    import numpy as np
    converted_count = 0
    weights_dict = dict()
    for node in graph_def_.node:
        tensor_proto = node.attr["value"].tensor
        if tensor_proto.tensor_content:
            np_array = tensor_util.MakeNdarray(tensor_proto)
            weights_dict[node.name] = np_array
            converted_count += 1
    np.savez_compressed(output_file_, **weights_dict)


def convert_weights(inf_graph):
    how_many_converted = 0
    out_graph_def = tf.GraphDef()
    for input_node in inf_graph.node:
        output_node = out_graph_def.node.add()
        output_node.MergeFrom(input_node)
        if output_node.op == 'Const':
            tensor_proto = output_node.attr['value'].tensor
            if tensor_proto.tensor_content:
                np_array = tensor_util.MakeNdarray(tensor_proto)
                tensor_proto.tensor_content = str(np_array)
                how_many_converted += 1

    print("set %d weights to numpy format." % how_many_converted)
    return out_graph_def


def check_inference_graph(inf_graph_file):
    script = "python common/export_inference_graph.py  --model_name mobilenet_v2_1.0 "
    params = "--image_size 224 --output_file data/mobilenet_v2_1.0_224/mobilenet_v2_1.0_224.inf.pb"
    usage = script + params

    if not os.path.exists(inf_graph_file):
        print(inf_graph_file, "does not exist! example for generating mobilenet_v1 inference graph is:")
        print(usage)
        exit(0)
    else:
        return inf_graph_file


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--checkpoint_file", type=str,
                        default="data/mobilenet_v2_1.0/mobilenet_v2_1.0_224.ckpt",
                        help="model checkpoint file")
    parser.add_argument('-g', "--inference_graph", type=check_inference_graph,
                        default="data/mobilenet_v2_1.0/mobilenet_v2_1.0_inf.pb",
                        help="model inference graph")
    parser.add_argument('-i', "--input_names", type=str, default="input",
                        help="Input node names, comma separated")
    parser.add_argument('-o', "--output_names", type=str, default="output",
                        help="The name of the output nodes, comma separated")
    parser.add_argument('-t', "--text", action='store_true',
                        help="save frozen graph in text format")
    parser.add_argument('-w', "--save_weights", action='store_true',
                        help="default not to save model weights to numpy npz file")

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    checkpoint_file = args.checkpoint_file
    inference_graph = args.inference_graph

    input_names = args.input_names
    output_names = args.output_names

    model_name = os.path.splitext(os.path.basename(checkpoint_file))[0]
    model_dir = os.path.dirname(checkpoint_file)
    output_file_name = os.path.join(model_dir, model_name)
    output_text_file = "{}.pb.txt".format(output_file_name)

    opt_graph_def = freeze_graph(checkpoint_file, input_names, output_names, inference_graph)

    format_str = "binary"
    output_frozen_file = "{}.frozen.pb".format(output_file_name)

    if args.text:
        format_str = "text"
        output_frozen_file += ".txt"
    save_graph(opt_graph_def, output_frozen_file, as_text=args.text)
    print("frozen graph {} saved to: {}".format(format_str, os.path.abspath(output_frozen_file)))
    if args.save_weights:
        save_weights(opt_graph_def, output_file_name)
        print("model weights saved to: {}.npz".format(os.path.abspath(output_file_name)))
