import csv
import os
import tensorflow as tf
from tensorflow.keras import backend as K

def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = tf.graph_util.convert_variables_to_constants(
            session, input_graph_def, output_names, freeze_var_names)
        return frozen_graph

def export_model(model, path, name):
    frozen_graph = freeze_session(K.get_session(), output_names=[out.op.name
        for out in model.outputs])
    tf.train.write_graph(frozen_graph, path, name, as_text=False)

def convert_model(model_path):
    os.system('python "C:/Program Files (x86)/IntelSWTools/openvino_2019.1.148/deployment_tools/model_optimizer/mo_tf.py" --input_model ' + model_path + ' --input_shape (1,224,224,3) --data_type FP16')

def get_myriad_xhwop_time(perf_counts):

    # print("{:<70} {:<15} {:<15} {:<15} {:<10}".format('name', 'layer_type',
    #     'exec_type', 'status', 'real_time, us'))

    # for layer, stats in perf_counts.items():
    #     print("{:<70} {:<15} {:<15} {:<15} {:<10}".format(layer, stats['layer_type'],
    #         stats['exec_type'], stats['status'], stats['real_time']))

    xhwop_total_time = 0

    for layer, stats in perf_counts.items():
        if(stats['exec_type'] == 'MyriadXHwOp'):
            xhwop_total_time += stats['real_time']

    return xhwop_total_time

def create_csv(csv_path):
    csv.register_dialect('myDialect', quoting=csv.QUOTE_ALL, skipinitialspace=True)
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f, dialect='myDialect')
        writer.writerow(['input_size', 'kernel_size', 'elapsed_time_us'])

def append_row_to_csv(csv_path, row):
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f, dialect='myDialect')
        writer.writerow(row)