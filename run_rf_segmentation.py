# -*- coding: utf-8 -*-
"""
Runs all steps of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os
import sys
import fnmatch

from BreastCAD import dcm2mha, rf_segmentation, elastix_registration, ann_segmentation
from BreastCAD.pipeline_params import *

def main():
    """ Runs the Breast CAD pipeline
    """

    # ======================================================================================================================
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
    if not os.path.isfile(RFSEGMENTATION_EXE):
        print "ERROR: invalid path to RF segmentation executable (" + RFSEGMENTATION_EXE + ")."
        return 1
    if not os.path.isfile(RFSEGMENTATION_TRAINING_FILE):
        print "ERROR: RF segmentation training file does not exist (" + RFSEGMENTATION_TRAINING_FILE + ")."
        return 1

    # ==================================================================================================================
    # And go...
    #
    # Open study list.
    print "Generating task list..."
    fileobj = open(TASK_FILE, "r")
    tasklist = []
    try:
        for line in fileobj:
            # Get the study and accession number.
            lineparts = line.split()
            tasklist.append(lineparts)
    finally:
        fileobj.close()

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
        # Calculate breast masks from non-fat suppressed images.
        #
        print "    Calculating breast masks for non-fat suppressed images..."
        return_value = 1
        for path, dirnames, filenames in os.walk(_outputDir):
            files = fnmatch.filter(filenames, RFSEGMENTATION_IMG_TYPE_FILTER)
            for f in files:
                input_file = os.path.join(path, f)
                basename = os.path.splitext(os.path.basename(f))[0]
                output_file = _outputDir + os.sep + basename + RFSEGMENTATION_OUTPUT_FILE_POSTFIX
                ret_val = rf_segmentation.do_rf_segmentation(RFSEGMENTATION_EXE,
                                                             input_file,
                                                             str(RFSEGMENTATION_OUTPUT_PIXDIMS[0]),
                                                             str(RFSEGMENTATION_OUTPUT_PIXDIMS[1]),
                                                             str(RFSEGMENTATION_OUTPUT_PIXDIMS[2]),
                                                             RFSEGMENTATION_TRAINING_FILE,
                                                             output_file)
                print ret_val

if __name__ == '__main__':
    main()
