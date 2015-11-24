# -*- coding: utf-8 -*-
"""
Perform ANN Segmentation on the input images.
@author: Maggie Kusano
@date: November 16, 2015
"""

import os
import subprocess
import fnmatch


def do_ANNSegmentation(exe_file, model_file, input_files, mask_file, output_file):
    '''
    Call ANN breast segmentation
    '''

    exe_path = os.path.dirname(exe_file)
    if exe_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + exe_path

    exe_cmd = '"' + exe_file + '"' + \
              ' -a ' + model_file + \
              ' -i ' + input_files[0] + ' ' + input_files[1] + ' ' + input_files[2] + ' ' + input_files[3] + ' ' + input_files[4] + \
              ' -m ' + mask_file + \
              ' -o ' + output_file
    print('doing: ' + exe_cmd)
    # cmd_result = subprocess.call(exe_cmd, stdout=FNULL, stderr=FNULL, shell=False)
    cmd_result = subprocess.call(exe_cmd)
    return cmd_result

# ======================================================================================================================
# Parameters
#

FNULL = open(os.devnull, 'w')  # use this if you want to suppress output to stdout from the subprocess

# Image input params.
INPUT_DIRECTORY = "D:\\Work\\BreastCAD\\TestData"
INPUT_STUDY = "7199"
INPUT_ACCESSION = "7709063"
INPUT_FILTER = ".MPH.mha"
MASK_FILTER = "_mask.mha"

# Image output params.
OUTPUT_DIRECTORY = "D:\\Work\\BreastCAD\\TestData"

# Path to Random Forest segmentation program.
EXE_DIRECTORY = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\ANN_Deep_Learning_prediction"
EXE_FILENAME = "ANNDeepLearningPrediction.exe"
MODEL_FILENAME = "deep_learning_trained_model.txt"

# Find pre and contrast-enhanced input files and mask file.
contents = os.listdir(INPUT_DIRECTORY)
inputFiles = fnmatch.filter(contents, INPUT_STUDY+"*"+INPUT_ACCESSION+"*"+INPUT_FILTER)
for i in range(len(inputFiles)):
    inputFiles[i] = os.path.join(INPUT_DIRECTORY, inputFiles[i])
maskFiles = fnmatch.filter(contents, INPUT_STUDY+"*"+INPUT_ACCESSION+"*"+MASK_FILTER)
maskFile = os.path.join(INPUT_DIRECTORY, maskFiles[0])

basename = os.path.basename(maskFile)
basename = basename[:-len(MASK_FILTER)]
outputFile = OUTPUT_DIRECTORY + os.sep + basename + "_LesionProbMap.mha"
modelFile = EXE_DIRECTORY + os.sep + MODEL_FILENAME
exeFile = EXE_DIRECTORY + os.sep + EXE_FILENAME
os.environ["PATH"] += os.pathsep + EXE_DIRECTORY

do_ANNSegmentation(exeFile, modelFile, inputFiles, maskFile, outputFile)

