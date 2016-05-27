# -*- coding: utf-8 -*-
"""
Lesion map thresholding and vessel removal step of the Breast CAD pipeline.
@author: Maggie Kusano
@date: November 26, 2015
"""

import os
import fnmatch

import pipeline_utils as utils
from BreastCAD import threshold_image, remove_vessels
from pipeline_params import *


def main():

    # ==================================================================================================================
    # Make sure everything exists before starting pipeline
    #
    if not os.path.isfile(TASK_FILE):
        print "ERROR: TASK_FILE (" + TASK_FILE + ") does not exist."
        return 1
    if not os.path.exists(INPUT_DIRECTORY):
        print "ERROR: INPUT_DIRECTORY (" + INPUT_DIRECTORY + ") does not exist."
        return 1
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    if not os.path.isfile(THRESHOLD_EXE):
        print "ERROR: invalid path to thresholdImage.exe (" + THRESHOLD_EXE + ")."
        return 1
    if not os.path.isfile(REMOVEVESSEL_EXE):
        print "ERROR: invalid path to removeVessel.exe (" + REMOVEVESSEL_EXE + ")."
        return 1

    # ==================================================================================================================
    # And go...
    #
    # Open study list.
    print "Generating task list..."
    tasklist = utils.build_tasklist()

    for iItem, item in enumerate(tasklist):

        _study_no = item[0]
        _accession_no_fixed = item[1]
        _accession_no_moving = item[2]
        print "    Study: " + _study_no + ", Fixed: " + _accession_no_fixed + ", Moving: " + _accession_no_moving
        _inputDir = INPUT_DIRECTORY + os.sep + _study_no
        if not os.path.exists(_inputDir):
            print "Study not found (" + _inputDir + "). Skipping."
            continue
        if not os.path.exists(_inputDir + os.sep + _accession_no_fixed):
            print "Fixed accession number not found (" + _accession_no_fixed + "). Skipping."
            continue
        if not os.path.exists(_inputDir + os.sep + _accession_no_moving):
            print "Moving accession number not found (" + _accession_no_moving + "). Skipping."
            continue
        _outputDir = OUTPUT_DIRECTORY + os.sep + _study_no + "_" + _accession_no_fixed + "_" + _accession_no_moving
        if not os.path.exists(_outputDir):
            os.makedirs(_outputDir)
        print "Processing Study: " + _study_no + "..."

        # --------------------------------------------------------------------------------------------------------------
        #  Remove vessels from lesion probability map images.
        #
        print "    Removing vessels from lesion probability map images..."
        # Find input lesion probablity maps.
        contents = os.listdir(_outputDir)
        for accession_no in (_accession_no_fixed, _accession_no_moving):
            for filter in THRESHOLD_IMG_TYPE_FILTER:
                matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+filter)
                input_file = os.path.join(_outputDir, matches[0])
                threshold_output_file = os.path.join(_outputDir, matches[0][:-4] + THRESHOLD_OUTPUT_IMG_POSTFIX)
                removevessel_output_file = os.path.join(_outputDir, os.path.basename(threshold_output_file)[:-4] +
                                                        REMOVEVESSEL_OUTPUT_IMG_POSTFIX)

                retVal = threshold_image.do_threshold_image(THRESHOLD_EXE, input_file, threshold_output_file,
                                                            THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_FOREGROUND)
                retVal = remove_vessels.do_remove_vessels(REMOVEVESSEL_EXE, threshold_output_file, removevessel_output_file)

if __name__ == '__main__':
    main()

