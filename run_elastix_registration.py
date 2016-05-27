# -*- coding: utf-8 -*-
"""
Runs the elastix registration step of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os
import fnmatch

import pipeline_utils as utils
from BreastCAD import elastix_registration
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
    if not os.path.exists(INPUT_DIRECTORY):
        print "ERROR: INPUT_DIRECTORY (" + INPUT_DIRECTORY + ") does not exist."
        return 1
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    if not os.path.isfile(ELASTIX_EXE):
        print "ERROR: invalid path to elastix.exe (" + ELASTIX_EXE + ")."
        return 1
    if not os.path.isfile(ELASTIX_AFFINE_PAR_FILE):
        print "ERROR: invalid path to Elastix affine parameter file (" + ELASTIX_AFFINE_PAR_FILE + ")."
        return 1
    if not os.path.isfile(ELASTIX_BSPLINE_PAR_FILE):
        print "ERROR: invalid path to Elastix B-spline parameter file (" + ELASTIX_BSPLINE_PAR_FILE + ")."
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
        #  Perform Elastix registration of prior and current non-fat suppressed images.
        #
        print "    Registering fixed and moving images..."
        # Find fixed a moving files.
        contents = os.listdir(_outputDir)
        matches = fnmatch.filter(contents, _study_no+"*"+_accession_no_fixed+"*"+ELASTIX_IMG_TYPE_FILTER)
        if len(matches) != 1:
            print "ERROR: Fixed file not found in " + _outputDir
            continue
        else:
            fixedFile = os.path.join(_outputDir, matches[0])
        matches = fnmatch.filter(contents, _study_no+"*"+_accession_no_moving+"*"+ELASTIX_IMG_TYPE_FILTER)
        if len(matches) != 1:
            print "ERROR: Moving file not found in " + _outputDir
            continue
        else:
            movingFile = os.path.join(_outputDir, matches[0])

        # Find masks if required.
        if ELASTIX_WITH_MASK:
            matches = fnmatch.filter(contents, _study_no+"*"+_accession_no_fixed+"*"+ELASTIX_MASK_FILTER)
            if len(matches) != 1:
                print "Fixed mask not found in " + _outputDir
                continue
            else:
                fixedMaskFile = os.path.join(_outputDir, matches[0])
            matches = fnmatch.filter(contents, _study_no+"*"+_accession_no_fixed+"*"+ELASTIX_MASK_FILTER)
            if len(matches) != 1:
                print "Moving mask not found in " + _outputDir
                continue
            else:
                movingMaskFile = os.path.join(_outputDir, matches[0])
        else:
            fixedMaskFile = ''
            movingMaskFile = ''

        # Run Elastix.
        print "   Performing Elastix registration of fixed and moving images..."
        elastix_registration.do_elastix(ELASTIX_EXE, fixedFile, movingFile, _outputDir,
                                        ELASTIX_AFFINE_PAR_FILE, ELASTIX_BSPLINE_PAR_FILE,
                                        fixedMaskFile, movingMaskFile)

        # Remove intermediate files.
        elastix_registration.clean_elastix(_outputDir)


if __name__ == '__main__':
    main()
