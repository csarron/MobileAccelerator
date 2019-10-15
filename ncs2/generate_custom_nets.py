from net_values import *

def main():
    for kernel_size in range(kernel_size_begin, kernel_size_end):
        for depth in range(depth_begin, depth_end, depth_step):
            file_name_stem = get_model_file_name(kernel_size, depth)
            inference_graph_file = file_name_stem + '.inf.pb'
            ckpt_file = file_name_stem + '.ckpt'
            frozen_file = file_name_stem + '.frozen.pb'

            cust_arg_1 = '--cust_arg_1 ' + str(depth)
            cust_arg_2 = '--cust_arg_2 ' + str(kernel_size)
            execute_command('rm  ' + experiments_dir + '/checkpoint')

            command = 'python ../common/export_inference_graph.py --model_name inception_v3_custom --output_file ' + inference_graph_file + ' ' + cust_arg_1 + ' ' + cust_arg_2
            execute_command(command)

            command = 'python ../common/gen_weights.py --model_name inception_v3_custom --output_file '+ ckpt_file + ' ' + cust_arg_1 + ' ' + cust_arg_2
            execute_command(command)

            command = 'python ../common/freeze_model.py --checkpoint_file ' + ckpt_file + ' --inference_graph ' + inference_graph_file
            execute_command(command)

            command = 'python "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\mo_tf.py" --input_model ' + frozen_file + ' --output_dir ' + experiments_dir + ' --data_type FP16 --input_shape (1,224,224,3)'
            execute_command(command)

if __name__ == '__main__':
    sys.exit(main() or 0)