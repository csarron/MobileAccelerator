import os
from datetime import datetime
import sys
sys.path.append('../')

kernel_size_begin = 3
kernel_size_end = 4

# depth_begin = 1312
# depth_offset = 1344 - 1312
# depth_begin = 120
# depth_offset = 16
depth_begin = 1
depth_offset = 1
depth_step = 1

experiments_dir = 'custom_inception_v3_decrease_16_filters'
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