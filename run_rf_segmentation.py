# -*- coding: utf-8 -*-
"""
Runs the breast segmentation step of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os
import fnmatch

import pipeline_utils as utils
from BreastCAD import rf_segmentation
from BreastCAD.pipeline_params import *


def main():

    # ======================================================================================================================
    # Make sure everything exists before starting pipeline
    #
    if not os.path.isfile(TASK_FILE):
        print "ERROR: TASK_FILE (" + TASK_FILE + ") does not exist."
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
    tasklist = utils.build_tasklist()

    for iItem, item in enumerate(tasklist):

        _study_no = item[0]
        _accession_no_fixed = item[1]
        _accession_no_moving = item[2]
        print "    Study: " + _study_no + ", Fixed: " + _accession_no_fixed + ", Moving: " + _accession_no_moving
        _outputDir = OUTPUT_DIRECTORY + os.sep + _study_no + "_" + _accession_no_fixed + "_" + _accession_no_moving
        if not os.path.exists(_outputDir):
            os.makedirs(_outputDir)
        print "Processing Study: " + _study_no + "..."

        # --------------------------------------------------------------------------------------------------------------
        # Calculate breast masks from non-fat suppressed images.
        #
        print "    Calculating breast masks for non-fat suppressed images..."
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
