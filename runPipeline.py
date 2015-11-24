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

def doPipeline():
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
    if not os.path.isfile(DCM23D_EXE):
        print "ERROR: invalid path to DCM23D.exe (" + DCM23D_EXE + ")."
        return 1
    if not os.path.isfile(RFSEGMENTATION_EXE):
        print "ERROR: invalid path to RF segmentation executable (" + RFSEGMENTATION_EXE + ")."
        return 1
    if not os.path.isfile(RFSEGMENTATION_TRAINING_FILE):
        print "ERROR: RF segmentation training file does not exist (" + RFSEGMENTATION_TRAINING_FILE + ")."
        return 1
    if not os.path.isfile(ANN_EXE):
        print "ERROR: invalid path to ANN lesion segmentation executable (" + ANN_EXE + ")."
        return 1
    if not os.path.isfile(ANN_TRAINING_MODEL):
        print "ERROR: invalid path to ANN lesion segmentation executable (" + ANN_TRAINING_MODEL + ")."
        return 1
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
        # Convert DICOM to MHA.
        #
        print "    Converting DICOM to MHA..."
        ret_val = dcm2mha.do_dcm2mha(DCM23D_EXE, _inputDir, _outputDir, DCM23D_DICOM_FILE_FILTER, DCM23D_SERIES_DESC_FILTER)

        if ret_val > 0:
            print "       ERROR: skipping."
            continue

        # --------------------------------------------------------------------------------------------------------------
        # Calculate breast masks from non-fat suppressed images.
        #
        print "    Calculating breast masks for non-fat suppressed images..."
        for path, dirnames, filenames in os.walk(_outputDir):
            files = fnmatch.filter(filenames, RFSEGMENTATION_IMG_TYPE_FILTER)
            for f in files:
                inputFile = os.path.join(path, f)
                basename = os.path.splitext(os.path.basename(f))[0]
                outputFile = _outputDir + os.sep + basename + RFSEGMENTATION_OUTPUT_FILE_POSTFIX
                rf_segmentation.do_rf_segmentation(RFSEGMENTATION_EXE,
                                                   inputFile,
                                                   str(RFSEGMENTATION_OUTPUT_PIXDIMS[0]),
                                                   str(RFSEGMENTATION_OUTPUT_PIXDIMS[1]),
                                                   str(RFSEGMENTATION_OUTPUT_PIXDIMS[2]),
                                                   RFSEGMENTATION_TRAINING_FILE,
                                                   outputFile)

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

            ann_segmentation.do_ANNSegmentation(ANN_EXE, ANN_TRAINING_MODEL, input_files, mask_file, output_file)

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

        # Move all moving images into fixed space.
        print "   Transforming moving images..."


