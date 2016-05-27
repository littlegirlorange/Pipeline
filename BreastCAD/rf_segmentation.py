# -*- coding: utf-8 -*-
"""
Perform Random Forest Segmentation on the input images.
@author: Maggie Kusano
@date: November 16, 2015
"""

import subprocess
import os


FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess

def do_rf_segmentation(RFSegmentation_exe,
                       input_file,
                       resampled_pixel_spacing_X, resampled_pixel_spacing_Y, resampled_pixel_spacing_Z,
                       random_forest_trained_file,
                       output_file):
    '''
    Call Random Forest breast segmentation
    '''

    exe_path = os.path.dirname(RFSegmentation_exe)
    if exe_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + exe_path

    RFSegmentation_cmd = '"' + RFSegmentation_exe + '"' + \
                         " -i " + input_file + \
                         " -x " + resampled_pixel_spacing_X + \
                         " -y " + resampled_pixel_spacing_Y + \
                         " -z " + resampled_pixel_spacing_Z + \
                         " -r " + random_forest_trained_file + \
                         " -o " + output_file

    #print('doing: ' + RFSegmentation_cmd)
    cmd_result = subprocess.call(RFSegmentation_cmd, stdout=FNULL, stderr=FNULL, shell=False)
    #cmd_result = subprocess.call(RFSegmentation_cmd)
    return cmd_result

"""
import os
import fnmatch
FNULL = open(os.devnull, 'w')  # use this if you want to suppress output to stdout from the subprocess

# ======================================================================================================================
# Parameters
#
# Image input params.
INPUT_DIRECTORY = "D:\\Work\\BreastCAD\\TestData"
FILTER = "*.wo.FS.mha"

# Image output params.
OUTPUT_DIRECTORY = "D:\\Work\\BreastCAD\\TestData"
OUTPUT_PIXDIMS = [1.0, 1.0, 3.0]

# Path to Random Forest segmentation program.
RFSEGMENTATION_DIRECTORY = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\breastSegmentationRandomForest"
RFSEGMENTATION_EXE_FILENAME = "breastSegmentationRandomForest.exe"
RFSEGMENTATION_TRAINING_FILENAME = "opencv3.0_trained_training_15July_every_30_23_features_depth_50.xml"

trainingFile = RFSEGMENTATION_DIRECTORY + os.sep + RFSEGMENTATION_TRAINING_FILENAME
RFSegmentation_exe = RFSEGMENTATION_DIRECTORY + os.sep + RFSEGMENTATION_EXE_FILENAME
randomForestTrainedFile = RFSEGMENTATION_DIRECTORY + os.sep + RFSEGMENTATION_TRAINING_FILENAME
os.environ["PATH"] += os.pathsep + RFSEGMENTATION_DIRECTORY

# Create breast masks from non-fat suppressed images.
matches = []
for path, dirnames, filenames in os.walk(INPUT_DIRECTORY):
    files = fnmatch.filter(filenames, FILTER)
    for f in files:
        matches.append(os.path.join(path, f))

for inputFile in matches:
    basename = os.path.splitext(os.path.basename(inputFile))[0]
    outputFile = OUTPUT_DIRECTORY + os.sep + basename + "_mask.mha"
    doRFSegmentation(RFSegmentation_exe, inputFile,
                      str(OUTPUT_PIXDIMS[0]), str(OUTPUT_PIXDIMS[1]), str(OUTPUT_PIXDIMS[2]),
                      trainingFile, outputFile)

"""