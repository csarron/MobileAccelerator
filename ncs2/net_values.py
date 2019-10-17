import os
from datetime import datetime
import sys
sys.path.append('../')

kernel_size_begin = 5
kernel_size_end = 6

depth_begin = 0
depth_offset = 1
depth_step = 1

experiments_dir = 'inception_v3_custom_close_to_power_two'
model_file_pattern = experiments_dir + '/inception_v3_custom'

# experiments_dir = experiments_dir + '_kernel' + str(kernel_size) + '_depthstep' + str(depth_step)
os.makedirs(experiments_dir, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

def execute_command(command):
    print('\n############################################\n' + command)
    os.system(command)

def get_model_file_name(kernel_size, depth):
    return model_file_pattern + '_k' + str(kernel_size) + '_d' + str(depth).zfill(6)

def remove_file(file_name):
    print('Removing file: ' + file_name)
    try:
        os.remove(file_name)
    except OSError:
        pass