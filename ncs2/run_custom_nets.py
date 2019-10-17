from net_values import *

def main():
    output_file_name = experiments_dir + '_' + get_timestamp() + '.txt'
    output_file = open(output_file_name, 'w+')
    # output_file.write('kernel_size\tdepth\tspecific_layer_time(us)\ttime_without_injected(us)\tinference_total_time(ms)\ttotal_layer_time\n')
    # output_file.write('depth\tcalculated_total_time\taverage_total_time(ms)\n')
    output_file.write('layer\tlatency\n')
    output_file.close()

    for kernel_size in range(kernel_size_begin, kernel_size_end):
        for depth in range(depth_begin, depth_begin + depth_offset, depth_step):
            xml_file = get_model_file_name(kernel_size, depth) + '.frozen.xml'
            command = 'echo NCS2:%TIME% & python classification_sample.py --model ' + xml_file \
                + ' --input car.jpg --device MYRIAD --perf_counts --number_iter 1' \
                + ' --output_file ' + output_file_name \
                + ' --cust_arg_1 ' + str(depth) \
                + ' --cust_arg_2 ' + str(kernel_size) \
                + ' --new_384_depth ' + str(depth)
            execute_command(command)

if __name__ == '__main__':
    sys.exit(main() or 0)