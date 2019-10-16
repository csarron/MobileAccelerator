from net_values import *
import threading
import signal
import sys

running = True

def generate_models(depth_begin_local, depth_offset_local):
    if depth_offset_local == 0:
        return
    depth_end_local = depth_begin_local + depth_offset_local
    # print('threading.get_ident():' + str(threading.get_ident()) + ': depth_begin_local: ' + str(depth_begin_local) + ', depth_end_local:' + str(depth_end_local))
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
            # execute_command('rm  ' + experiments_dir + '/checkpoint')

            command = 'python ../common/export_inference_graph.py --model_name inception_v3_custom --output_file ' + inference_graph_file + ' ' + cust_arg_1 + ' ' + cust_arg_2 + ' ' + new_384_depth
            execute_command(command)

            command = 'python ../common/gen_weights.py --model_name inception_v3_custom --output_file '+ ckpt_file + ' ' + cust_arg_1 + ' ' + cust_arg_2 + ' ' + new_384_depth
            execute_command(command)

            command = 'python ../common/freeze_model.py --checkpoint_file ' + ckpt_file + ' --inference_graph ' + inference_graph_file
            execute_command(command)

            command = 'python "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\mo_tf.py" --input_model ' + frozen_file + ' --output_dir ' + experiments_dir + ' --data_type FP16 --input_shape (1,224,224,3)'
            execute_command(command)

# depth_begin = 0
# depth_offset = 1

def run_normally():
    generate_models(depth_begin, depth_offset)

def run_multithreaded():
    thread_count = 8
    work_chunks = int(depth_offset/thread_count)

    threads = []

    for thread_idx in range (0, thread_count):
        threads.append(threading.Thread(target = generate_models, \
            args = (depth_begin + thread_idx * work_chunks, work_chunks)))

    remaining_chunk = depth_offset - work_chunks * thread_count

    if remaining_chunk > 0:
        threads.append(threading.Thread(target = generate_models, \
            args = (depth_begin + depth_offset - remaining_chunk, remaining_chunk)))

    for x in threads:
        x.start()

    for x in threads:
        x.join()

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    running = False
    sys.exit(0)

# print('Press Ctrl+C')
# signal.pause()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    # run_normally()
    run_multithreaded()

if __name__ == '__main__':
    sys.exit(main() or 0)