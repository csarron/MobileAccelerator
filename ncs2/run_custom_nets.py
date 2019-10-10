import os
import sys
sys.path.append('../')

outputDir = "./large_filters"

def executeCommand(command):
    #print(command)
    os.system(command)

def executeModels(min, max, step):
    for i in range(min, max, step):
        # index = str(i).zfill(6)
        # file_name_stem = outputDir + '/inception_v3_' + index
        file_name_stem = outputDir + '/inception_v3_' + str(i)
        xml_file = file_name_stem + '.frozen.xml'

        command = 'echo NCS2:%TIME% & python classification_sample.py --model ' + xml_file + ' --input car.jpg --device MYRIAD --perf_counts --number_iter 5'
        executeCommand(command)

executeModels(384 + 256, 4096, 256)