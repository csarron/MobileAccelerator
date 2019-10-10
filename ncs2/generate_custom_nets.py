import os
import sys
sys.path.append('../')

outputDir = "./many_5x5_filters"

def executeCommand(command):
    print(command)
    os.system(command)

def generateModels(min, max, step):
    for i in range(min, max, step):
        file_name_stem = outputDir + '/inception_v3_' + str(i).zfill(6)
        # file_name_stem = outputDir + '/inception_v3_' + str(i)
        inference_graph_file = file_name_stem + '.inf.pb'
        ckpt_file = file_name_stem + '.ckpt'
        frozen_file = file_name_stem + '.frozen.pb'
        cust_arg_1 = '--cust_arg_1 ' + str(i)
        cust_arg_2 = '--cust_arg_2 ' + str(3)
        executeCommand('rm checkpoint')

        command = 'python ../common/export_inference_graph.py --model_name inception_v3_custom --output_file ' + inference_graph_file + ' ' + cust_arg_1 + ' ' + cust_arg_2
        executeCommand(command)

        command = 'python ../common/gen_weights.py --model_name inception_v3_custom --output_file '+ ckpt_file + ' ' + cust_arg_1 + ' ' + cust_arg_2
        executeCommand(command)

        command = 'python ../common/freeze_model.py --checkpoint_file ' + ckpt_file + ' --inference_graph ' + inference_graph_file
        executeCommand(command)

        command = 'python "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\mo_tf.py" --input_model ' + frozen_file + ' --output_dir ' + outputDir + ' --data_type FP16 --input_shape (1,224,224,3)'
        executeCommand(command)

generateModels(1024 + 256, 2048, 64)