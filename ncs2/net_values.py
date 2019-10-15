import os
from datetime import datetime
import sys
sys.path.append('../')

kernel_size_begin = 3
kernel_size_end = 6
depth_begin = 256
depth_end = 257
depth_step = 1

experiments_dir = './generated'
# experiments_dir = experiments_dir + '_kernel' + str(kernel_size) + '_depthstep' + str(depth_step)
os.makedirs(experiments_dir, exist_ok=True)

model_file_pattern = experiments_dir + '/model'

def get_timestamp():
    return datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

def execute_command(command):
    print('\n############################################\n' + command)
    os.system(command)

def get_model_file_name(kernel_size, depth):
    return model_file_pattern + '_k' + str(kernel_size) + '_d' + str(depth).zfill(6)