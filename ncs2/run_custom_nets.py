import os
import sys
sys.path.append('../')

def executeCommand(command):
    print(command)
    os.system(command)

def executeModels(min, max, step):
    for i in range(min, max, step):
        file_name_stem = 'inception_v3_' + str(i)
        xml_file = file_name_stem + '.frozen.xml'

        command = 'echo NCS2:%TIME% & python classification_sample.py --model ' + xml_file + ' --input car.jpg --device MYRIAD --perf_counts --number_iter 5'
        executeCommand(command)

executeModels(4, 384, 4)