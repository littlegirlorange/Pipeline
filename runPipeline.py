# -*- coding: utf-8 -*-
"""
Runs all steps of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os
import fnmatch
import string

import pipeline_utils as utils
from BreastCAD import dcm2mha, rf_segmentation, ann_segmentation, elastix_registration, transformix_registration, \
                      motion_correction, threshold_image, remove_vessels
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
    if not os.path.exists(DCM_INPUT_DIRECTORY):
        print "ERROR: INPUT_DIRECTORY (" + DCM_INPUT_DIRECTORY + ") does not exist."
        return 1
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    if not os.path.isfile(DCM23D_EXE):
        print "ERROR: invalid path to DCM23D.exe (" + DCM23D_EXE + ")."
        return 1
    if not os.path.isfile(MOTIONCORRECTION_EXE):
        print "ERROR: invalid path to motion correction executable (" + MOTIONCORRECTION_EXE + ")."
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
    if not os.path.isfile(TRANSFORMIX_EXE):
        print "ERROR: invalid path to transformix.exe (" + TRANSFORMIX_EXE + ")."
        return 1
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
        if int(_accession_no_moving) > int(_accession_no_fixed):
            _accession_no_fixed, _accession_no_moving = _accession_no_moving, _accession_no_fixed
        print "    Study: " + _study_no + ", Fixed: " + _accession_no_fixed + ", Moving: " + _accession_no_moving
        _inputDir = DCM_INPUT_DIRECTORY + os.sep + _study_no
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
            bOutdirExists = False
            os.makedirs(_outputDir)
        else:
            bOutdirExists = True

        print "======================================"
        print "Processing Study: " + _study_no + "..."

        # --------------------------------------------------------------------------------------------------------------
        # Convert DICOM to MHA.
        #
        print "    Converting DICOM to MHA..."
        bDoConversion = True
        if bOutdirExists:
            # Check to see if all required series have already been converted.
            contents = os.listdir(_outputDir)
            matches = fnmatch.filter(contents, _study_no+"*"+MOTIONCORRECTION_FIXED_IMG_TYPE_FILTER)
            if len(matches) == 2:
                matches = fnmatch.filter(contents, _study_no+"*"+MOTIONCORRECTION_MOVING_IMG_TYPE_FILTER)
                if len(matches) == 8:
                    matches = fnmatch.filter(contents, _study_no+"*"+RFSEGMENTATION_IMG_TYPE_FILTER)
                    if len(matches) == 2:
                        print "      Existing MHA format non-fat suppressed, precontrast fat suppressed and postcontrast images found."
                        print "      Skipping DICOM to MHA conversion."
                        bDoConversion = False

        if bDoConversion:
            for ano in [_accession_no_fixed, _accession_no_moving]:
                indir = _inputDir + os.sep + ano
                ret_val = dcm2mha.do_dcm2mha(DCM23D_EXE, indir, _outputDir, DCM23D_DICOM_FILE_FILTER, DCM23D_SERIES_DESC_FILTER)
                if ret_val > 0:
                    print "       ERROR: In dcm2mha. Skipping."
                continue

        # Check for required series.
        contents = os.listdir(_outputDir)
        matches = fnmatch.filter(contents, _study_no+"*"+MOTIONCORRECTION_FIXED_IMG_TYPE_FILTER)
        if len(matches) != 2:
            print "      ERROR: Missing preconstrast fat suppressed image(s). Skipping."
            continue
        matches = fnmatch.filter(contents, _study_no+"*"+MOTIONCORRECTION_MOVING_IMG_TYPE_FILTER)
        if len(matches) != 8:
            print "      ERROR: Missing postcontrast image(s). Skipping."
            continue
        matches = fnmatch.filter(contents, _study_no+"*"+RFSEGMENTATION_IMG_TYPE_FILTER)
        if len(matches) != 2:
            print "      ERROR: Missing non-fat suppressed image(s). Skipping."
            continue

        # --------------------------------------------------------------------------------------------------------------
        #  Perform optical flow motion correction on post-contrast images (align post-contrast to pre-contrast fat
        #  suppressed image).
        #
        print "    Motion correcting post-contrast images..."
        # Find pre and contrast-enhanced input files and mask file.
        for accession_no in (_accession_no_fixed, _accession_no_moving):
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+MOTIONCORRECTION_FIXED_IMG_TYPE_FILTER)
            fixed_file = os.path.join(_outputDir, matches[0])
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+MOTIONCORRECTION_MOVING_IMG_TYPE_FILTER)
            moving_files = []
            for match in matches:
                moving_files.append(os.path.join(_outputDir, match))

            motion_correction.do_motion_correction(MOTIONCORRECTION_EXE, fixed_file, moving_files)

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
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+ANN_PRECONTRAST_IMG_TYPE_FILTER)
            input_files = []
            if len(matches) != 1:
                print "ERROR: Incorrect number of precontrast images found. Exiting."
                return 1
            input_files.append(os.path.join(_outputDir, matches[0]))
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+ANN_POSTCONTRAST_IMG_TYPE_FILTER)
            if len(matches) != 4:
                print "ERROR: Incorrect number of postcontrast images found. Exiting."
                return 1
            for match in matches:
                input_files.append(os.path.join(_outputDir, match))
            matches = fnmatch.filter(contents, _study_no+"*"+accession_no+"*"+RFSEGMENTATION_OUTPUT_FILE_POSTFIX)
            if len(matches) != 1:
                print "ERROR: Incorrect number of breast masks found. Exiting."
                return 1
            mask_file = os.path.join(_outputDir, matches[0])
            basename = os.path.basename(mask_file)
            basename = basename[:-len(RFSEGMENTATION_OUTPUT_FILE_POSTFIX)]  # Strip mask postfix
            output_file = _outputDir + os.sep + basename + "_LesionProbMap.mha"

            ann_segmentation.do_ann_segmentation(ANN_EXE, ANN_TRAINING_MODEL, input_files, mask_file, output_file)

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

        # --------------------------------------------------------------------------------------------------------------
        #  Transform moving images.
        #
        print "    Transforming moving images..."
        # Find transformation parameters.
        contents = os.listdir(_outputDir)
        matches = fnmatch.filter(contents, _study_no+"*"+_accession_no_fixed+"*"+_accession_no_moving+"*"+TRANSFORMIX_PARAM_FILE_FILTER)
        if len(matches) != 1:
            print "ERROR: Transformation parameter file file not found in " + _outputDir
            continue
        else:
            param_file = os.path.join(_outputDir, matches[0])

        # Get basename of fixed image.
        param_file_basename = os.path.basename(param_file)[:-4]
        index = string.rfind(param_file_basename, "_" + _study_no + "CAD")
        fixed_basename = param_file_basename[0:index]
        # Find moving images.
        for filter in TRANSFORMIX_IMG_TYPE_FILTER:
            matches = fnmatch.filter(contents, _study_no+"*"+_accession_no_moving+"*"+filter)
            for match in matches:
                # Run Transformix.
                print "   Transforming moving images..."
                input_file = os.path.join(_outputDir, match)
                output_basename = fixed_basename + '_' + os.path.basename(match)[:-4]
                output_file = os.path.join(_outputDir, output_basename + "_reg.mha")
                transformix_registration.do_transformix(TRANSFORMIX_EXE, input_file, param_file, output_file)

        # --------------------------------------------------------------------------------------------------------------
        #  Remove vessels from lesion probability map images.
        #
        print "    Removing vessels from lesion probability map images..."
        # Find input lesion probability maps.
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
