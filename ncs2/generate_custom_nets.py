from net_values import *
import threading
import signal
import sys

running = True

def generate_models(depth_begin_local, depth_offset_local):
    if depth_offset_local == 0:
        return

    depth_end_local = depth_begin_local + depth_offset_local
    print('threading.get_ident():' + str(threading.get_ident()) + ': depth_begin_local: ' + str(depth_begin_local) + ', depth_end_local:' + str(depth_end_local))

    for kernel_size in range(kernel_size_begin, kernel_size_end):
        for depth in range(depth_begin_local, depth_begin_local + depth_offset_local, depth_step):
            if running==False:
                print('##### Exiting #####')
                return
            file_name_stem = get_model_file_name(kernel_size, depth)
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

def run_normally(depth_begin_local, depth_offset_local):
    generate_models(depth_begin_local, depth_offset_local)

def run_multithreaded(depth_begin_local, depth_offset_local):
    thread_count = 8
    progress = 0

    while progress < depth_offset_local:
        threads = []

        for thread_idx in range (0, thread_count):
            if progress >= depth_offset_local:
                return
            threads.append(threading.Thread(target = generate_models, \
                args = (depth_begin_local + progress, 1)))
            progress += 1

        for x in threads:
            x.start()

        for x in threads:
            x.join()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    running = False
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    #run_multithreaded(depth_begin, depth_offset)

    run_normally(depth_begin, depth_offset)

if __name__ == '__main__':
    sys.exit(main() or 0)