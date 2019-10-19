from ncs_util import *
import threading
import signal
import sys
from argparse import ArgumentParser, SUPPRESS

running_ = True
thread_count_ = 4
kernel_sizes_ = [1]#[2, 4, 5, 6, 7]
depth_begin_ = 1831
depth_offset_ = 2048 - 1831 + 1
depth_step_ = 1
experiments_dir_ = 'one_layer_depth_' + str(depth_begin_) + '_' + str(depth_offset_) + '_step_' + str(depth_step_)
log_dir_ = 'outputs'

def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument("-r", "--run_models", help="Run models", default=False, action='store_true')

	# p = argparse.ArgumentParser()

	# # accept two lists of arguments
	# # like -a 1 2 3 4 -b 1 2 3
	# p.add_argument('-a', nargs="+", type=int)
	# p.add_argument('-b', nargs="+", type=int)
	# args = p.parse_args()

	# # check if input is valid
	# set_a = set(args.a)
	# set_b = set(args.b)
    return parser

def run_model(experiments_dir, output_log_name, kernel_size, depth):
    xml_file = experiments_dir + '/' + get_model_file_name(kernel_size, depth) + '.frozen.xml'
    command = 'python classification_sample.py --model ' + xml_file \
        + ' --input car.jpg --device MYRIAD --perf_counts --number_iter 1' \
        + ' --output_file ' + output_log_name \
        + ' --cust_arg_1 ' + str(depth) \
        + ' --cust_arg_2 ' + str(kernel_size) \
        + ' --new_384_depth ' + str(depth)
    execute_command(command)

def run_models(experiments_dir, depth_begin, depth_offset, depth_step):
    print('Run models from ' + experiments_dir + '\n')
    # return
    create_dir(log_dir_)
    output_log_name = log_dir_ + '/' + experiments_dir + '_' + get_timestamp() + '.txt'
    output_log = open(output_log_name, 'w+')

    output_log.write('kernel_size\t'
        + 'depth\t'
        + 'specific_layer_time(ms)\t'
        + 'time_without_injected(ms)\t'
        + 'inference_total_time(ms)\t'
        + 'total_layer_time'
        + '\n')

    # output_file.write('depth\tcalculated_total_time\taverage_total_time(ms)\n')
    # output_file.write('layer\tlatency\n')
    output_log.close()

    for kernel_size in kernel_sizes_:
        curr_depth = depth_begin
        depth_end = depth_begin + depth_offset

        while curr_depth < depth_end:
            run_model(experiments_dir, output_log_name, kernel_size, curr_depth)
            curr_depth += depth_step

def generate_model(experiments_dir, kernel_size, depth):
    print('----------- Generating model' + ', kernel_size: ' \
        + str(kernel_size) + ', depth: ' + str(depth) + ', thread ID: ' + str(threading.get_ident()))

    if running_ == False:
        print('!!! Exiting !!!')
        return

    file_name_stem = experiments_dir + '/' + get_model_file_name(kernel_size, depth)
    inference_graph_file = file_name_stem + '.inf.pb'
    ckpt_file = file_name_stem + '.ckpt'
    frozen_file = file_name_stem + '.frozen.pb'

    cust_arg_1 = '--cust_arg_1 ' + str(depth)
    cust_arg_2 = '--cust_arg_2 ' + str(kernel_size)
    new_384_depth = '--new_384_depth ' + str(depth)

    command = 'python ../common/export_inference_graph.py --model_name inception_v3_custom --output_file ' + inference_graph_file + ' ' + cust_arg_1 + ' ' + cust_arg_2 + ' ' + new_384_depth
    execute_command(command)

    command = 'python ../common/gen_weights.py --model_name inception_v3_custom --output_file '+ ckpt_file + ' ' + cust_arg_1 + ' ' + cust_arg_2 + ' ' + new_384_depth
    execute_command(command)

    command = 'python ../common/freeze_model.py --checkpoint_file ' + ckpt_file + ' --inference_graph ' + inference_graph_file
    execute_command(command)

    command = 'python "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\mo_tf.py" --input_model ' + frozen_file + ' --output_dir ' + experiments_dir + ' --data_type FP16 --input_shape (1,224,224,3)'
    execute_command(command)

    # Otherwise we run out of disk space pretty quickly
    remove_file(inference_graph_file)
    remove_file(ckpt_file + '.data-00000-of-00001')
    remove_file(ckpt_file + '.latest')
    remove_file(ckpt_file + '.index')
    remove_file(ckpt_file + '.meta')
    remove_file(frozen_file)

def generate_models(experiments_dir, depth_begin, depth_offset, depth_step):
    print('Generate models\n')
    for kernel_size in kernel_sizes_:
        curr_depth = depth_begin
        depth_end = depth_begin + depth_offset

        while curr_depth < depth_end:
            threads = []

            for thread_idx in range (0, thread_count_):
                if curr_depth >= depth_end:
                    break
                threads.append(threading.Thread(target = generate_model, \
                    args = (experiments_dir, kernel_size, curr_depth)))
                curr_depth += depth_step

            for x in threads:
                x.start()

            for x in threads:
                x.join()

def main():
    create_dir(experiments_dir_)
    signal.signal(signal.SIGINT, signal_handler)

    if args.run_models:
        run_models(experiments_dir_, depth_begin_, depth_offset_, depth_step_)
    else:
        generate_models(experiments_dir_, depth_begin_, depth_offset_, depth_step_)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    running_ = False
    sys.exit(0)

if __name__ == '__main__':
    args = build_argparser().parse_args()
    sys.exit(main() or 0)