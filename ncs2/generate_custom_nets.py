import os
import sys
sys.path.append('../')

# from export_inference_graph import export_inference_graph

# export_inference_graph.export_inference_graph(model_name="inception_v3",
#                         output_file="inception_v3_77.inf.pb",
#                         cust_arg_1=128)

for i in range(0, 128, 64):
    file_name_stem = 'inception_v3_' + str(i)
    cust_arg_stem = '--cust_arg_1 ' + str(i)

    command = 'python ..\common\export_inference_graph.py --model_name inception_v3_custom --output_file ' + file_name_stem + '.inf.pb ' + cust_arg_stem
    os.system(command)
    command = 'python ..\common\gen_weights.py --model_name inception_v3_custom --output_file '+ file_name_stem + '.ckpt ' + cust_arg_stem
    os.system(command)
    # Freeze model