# -*- coding: utf-8 -*-
"""
Runs the transformix step of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os
import fnmatch
import string

import pipeline_utils as utils
from BreastCAD import transformix_registration
from BreastCAD.pipeline_params import *


def check_params():
    # Make sure everything exists before starting pipeline
    if not os.path.isfile(TASK_FILE):
        print "ERROR: TASK_FILE (" + TASK_FILE + ") does not exist."
        return 1
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
    if not os.path.isfile(TRANSFORMIX_EXE):
        print "ERROR: invalid path to transformix.exe (" + TRANSFORMIX_EXE + ")."
        return 1


def run():
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


if __name__ == '__main__':
    check_params()
    run()
