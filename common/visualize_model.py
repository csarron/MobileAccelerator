#! /usr/bin/env python3
import argparse
import os

import numpy as np
import tensorflow as tf
from IPython.display import HTML


def strip_consts(graph_def, max_const_size=32):
    """Strip large constant values from graph_def."""
    strip_def = tf.GraphDef()
    for n0 in graph_def.node:
        n = strip_def.node.add()
        n.MergeFrom(n0)
        if n.op == 'Const':
            tensor = n.attr['value'].tensor
            size = len(tensor.tensor_content)
            if size > max_const_size:
                tensor.tensor_content = "<stripped %d bytes>" % size
    return strip_def


def save_html(graph_def, html_file=None, max_const_size=32):
    """Visualize TensorFlow graph."""
    if hasattr(graph_def, 'as_graph_def'):
        graph_def = graph_def.as_graph_def()
    strip_def = strip_consts(graph_def, max_const_size=max_const_size)
    code = """
        <script>
          function load() {{
            document.getElementById("{id}").pbtxt = {data};
          }}
        </script>
        <link rel="import" href="https://tensorboard.appspot.com/tf-graph-basic.build.html" onload=load()>
        <div style="height:1200px">
          <tf-graph-basic id="{id}"></tf-graph-basic>
        </div>
    """.format(data=repr(str(strip_def)), id='graph' + str(np.random.rand()))

    iframe = """
        <iframe seamless style="overflow: hidden; height: 100%;
        width: 100%; position: absolute;" height="100%" width="100%" srcdoc="{}"></iframe>
    """.format(code.replace('"', '&quot;'))
    h = HTML(iframe)
    if html_file:
        with open("{}.html".format(html_file), 'w') as f:
            f.write(h.data)
        print("graph vis file saved to {}.html".format(html_file))


if __name__ == '__main__':
    graph_def = tf.GraphDef()
    parser = argparse.ArgumentParser()
    parser.add_argument("model_file", type=str,
                        help="a TensorFlow inference graph file")
    args = parser.parse_args()

    model_name = os.path.splitext(args.model_file)[0]
    with tf.gfile.FastGFile(args.model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    save_html(graph_def, model_name)
