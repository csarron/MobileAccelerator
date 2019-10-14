import os
import sys
sys.path.append('../')

from argparse import ArgumentParser, SUPPRESS

def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS,
        help='Show this help message and exit.')
    args.add_argument("-e", '--experiments_dir', required=True, type=str)
    parser.add_argument("-of", "--output_file", type=str, default=0,
                        help="Output file for results")
    # parser.add_argument("-1", "--cust_arg_1", type=int, default=0,
    #                     help="Custom argument 1")
    # parser.add_argument("-2", "--cust_arg_2", type=int, default=0,
    #                     help="Custom argument 2")
    return parser

def executeCommand(command):
    # print(command)
    os.system(command)

def executeModels(min, max, step):
    outputDir = args.experiments_dir
    for i in range(min, max, step):
        file_name_stem = outputDir + '/inception_v3_' + str(i).zfill(6)
        xml_file = file_name_stem + '.frozen.xml'

        command = 'echo NCS2:%TIME% & python classification_sample.py --model ' + xml_file \
            + ' --input car.jpg --device MYRIAD --perf_counts --number_iter 5' \
            + ' --output_file ' + str(args.output_file) \
            + ' --cust_arg_1 ' + str(i) \
            + ' --cust_arg_2 ' + str(5)
        executeCommand(command)

def main():
    # executeModels(16, 3504 + 1, 16)
    executeModels(16, 4096 + 1, 16)

if __name__ == '__main__':
    args = build_argparser().parse_args()
    sys.exit(main() or 0)