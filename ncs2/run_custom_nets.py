from net_values import *

def main():
    output_log_file = experiments_dir + '_' + get_timestamp() + '.txt'
    for kernel_size in range(kernel_size_begin, kernel_size_end):
        for depth in range(depth_begin, depth_end, depth_step):
            xml_file = get_model_file_name(kernel_size, depth) + '.frozen.xml'
            command = 'echo NCS2:%TIME% & python classification_sample.py --model ' + xml_file \
                + ' --input car.jpg --device MYRIAD --perf_counts --number_iter 10' \
                + ' --output_file ' + output_log_file \
                + ' --cust_arg_1 ' + str(depth) \
                + ' --cust_arg_2 ' + str(kernel_size)
            execute_command(command)

if __name__ == '__main__':
    sys.exit(main() or 0)