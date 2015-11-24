# -*- coding: utf-8 -*-
"""
Runs all steps of the BreastCAD pipeline.
@author: Maggie Kusano
@date: November 19, 2015
"""

import os

from BreastCAD import dcm2mha
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
    if not os.path.isfile(DCM23D_EXE):
        print "ERROR: invalid path to DCM23D.exe (" + DCM23D_EXE + ")."
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
            # Get the study and accession numbers.
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
        #_inputDir = _inputDir + os.sep + _accession_no_moving
        dcm2mha.do_dcm2mha(DCM23D_EXE, _inputDir, _outputDir, DCM23D_DICOM_FILE_FILTER, DCM23D_SERIES_DESC_FILTER)


if __name__ == '__main__':
    main()



