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
    if not os.path.isfile(ANN_EXE):
        print "ERROR: invalid path to ANN lesion segmentation executable (" + ANN_EXE + ")."
        return 1
    if not os.path.isfile(ANN_TRAINING_MODEL):
        print "ERROR: invalid path to ANN lesion segmentation executable (" + ANN_TRAINING_MODEL + ")."
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
        #  Perform ANN lesion segmentation of fixed and moving data sets.
        #
        print "    Finding lesions..."
        # Find pre and contrast-enhanced input files and mask file.
        contents = os.listdir(_outputDir)
        for accession_no in (_accession_no_fixed, _accession_no_moving):
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+ANN_IMG_TYPE_FILTER)
            input_files = []
            for match in matches:
                input_files.append(os.path.join(_outputDir, match))
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+RFSEGMENTATION_OUTPUT_FILE_POSTFIX)
            mask_file = os.path.join(_outputDir, matches[0])
            basename = os.path.basename(mask_file)
            basename = basename[:-len(RFSEGMENTATION_OUTPUT_FILE_POSTFIX)]  # Strip mask postfix
            output_file = _outputDir + os.sep + basename + "_LesionProbMap.mha"

            ann_segmentation.do_ann_segmentation(ANN_EXE, ANN_TRAINING_MODEL, input_files, mask_file, output_file)


if __name__ == '__main__':
    main()

