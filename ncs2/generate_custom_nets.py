import os
import sys
sys.path.append('../')

def executeCommand(command):
    print(command)
    os.system(command)

def generateModels(min, max, step):
    for i in range(min, max, step):
        file_name_stem = 'inception_v3_' + str(i)
        inference_graph_file = file_name_stem + '.inf.pb'
        ckpt_file = file_name_stem + '.ckpt'
        frozen_file = file_name_stem + '.frozen.pb'
        cust_arg = '--cust_arg_1 ' + str(i)
        executeCommand('rm checkpoint')

        command = 'python ../common/export_inference_graph.py --model_name inception_v3_custom --output_file ' + inference_graph_file + ' ' + cust_arg
        executeCommand(command)

        command = 'python ../common/gen_weights.py --model_name inception_v3_custom --output_file '+ ckpt_file + ' ' + cust_arg
        executeCommand(command)

        command = 'python ../common/freeze_model.py --checkpoint_file ' + ckpt_file + ' --inference_graph ' + inference_graph_file
        executeCommand(command)

        command = 'python "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\mo_tf.py" --input_model ' + frozen_file + ' --output_dir ./ --data_type FP16 --input_shape (1,224,224,3)'
        executeCommand(command)

def executeModels(min, max, step):
    for i in range(min, max, step):
        file_name_stem = 'inception_v3_' + str(i)
        xml_file = file_name_stem + '.frozen.xml'

        command = 'echo NCS2:%TIME% & python classification_sample.py --model ' + xml_file + ' --input car.jpg --device MYRIAD --perf_counts'
        executeCommand(command)

generateModels(256, 256+3*8, 8)
# executeModels(min, max, step)