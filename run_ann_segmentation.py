# -*- coding: utf-8 -*-
"""
Runs the ANN segmentation step of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os
import fnmatch

import pipeline_utils as utils
from BreastCAD import ann_segmentation
from pipeline_params import *


def main():
    """ Runs the Breast CAD pipeline
    """

    # ======================================================================================================================
    # Make sure everything exists before starting pipeline
    #
    if not os.path.isfile(TASK_FILE):
        print "ERROR: TASK_FILE (" + TASK_FILE + ") does not exist."
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
        #  Perform ANN lesion segmentation of fixed and moving data sets.
        #
        print "    Finding lesions..."
        # Find pre and contrast-enhanced input files and mask file.
        contents = os.listdir(_outputDir)
        for accession_no in (_accession_no_fixed, _accession_no_moving):
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+ANN_PRECONTRAST_IMG_TYPE_FILTER)
            input_files = []
            if len(matches) != 1:
                print "ERROR: Incorrect number of precontrast images found (" + len(matches) + "). Exiting."
                return 1
            input_files.append(os.path.join(_outputDir, matches[0]))
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+ANN_POSTCONTRAST_IMG_TYPE_FILTER)
            if len(matches) != 4:
                print "ERROR: Incorrect number of postcontrast images found (" + len(matches) + "). Exiting."
                return 1
            for match in matches:
                input_files.append(os.path.join(_outputDir, match))
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+RFSEGMENTATION_OUTPUT_FILE_POSTFIX)
            if len(matches) != 1:
                print "ERROR: Incorrect number of breast masks found (" + len(matches) + "). Exiting."
                return 1
            mask_file = os.path.join(_outputDir, matches[0])
            basename = os.path.basename(mask_file)
            basename = basename[:-len(RFSEGMENTATION_OUTPUT_FILE_POSTFIX)]  # Strip mask postfix
            output_file = _outputDir + os.sep + basename + "_LesionProbMap.mha"

            ann_segmentation.do_ann_segmentation(ANN_EXE, ANN_TRAINING_MODEL, input_files, mask_file, output_file)


if __name__ == '__main__':
    main()

