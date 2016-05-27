__author__ = 'maggie'
"""
Calculate and save subtraction images for the input list.
@author: Maggie Kusano
@date: January 16, 2015
"""
import os
import fnmatch
import string

from BreastCAD import image_subtraction
import pipeline_utils as utils
from pipeline_params_Lara import *

def main():
    # ======================================================================================================================
    # Make sure everything exists before starting pipeline
    #
    if not os.path.isfile(TASK_FILE):
        print "ERROR: TASK_FILE (" + TASK_FILE + ") does not exist."
        return 1

    # ==================================================================================================================
    # And go...
    #
    # Open study list.
    print "Generating task list..."
    tasklist = utils.build_tasklist_Lara()

    for iItem, item in enumerate(tasklist):
        _study_no = item[0]
        _accession_nos = item[1:]
        # Sort accession numbers so pre-biopsy scan is first.
        _accession_nos = sorted(_accession_nos, key=lambda x: int(x), reverse=True)

        # Make sure input data exists.
        _outputDir = OUTPUT_DIRECTORY + os.sep + _study_no
        if not os.path.exists(_outputDir):
            print "Study not found (" + _outputDir + "). Skipping."
            continue

        # --------------------------------------------------------------------------------------------------------------
        #  Perform optical flow motion correction on post-contrast images (align post-contrast to pre-contrast fat
        #  suppressed image).
        #
        print "Calculating subtraction images..."
        # Find pre and contrast-enhanced input files and mask file.
        contents = os.listdir(_outputDir)
        for ano in _accession_nos:
            matches = fnmatch.filter(contents, _study_no+"*"+ano+"*"+SUBTRACTION_PRECONTRAST_IMG_TYPE_FILTER)
            precontrast_file = os.path.join(_outputDir, matches[0])
            matches = fnmatch.filter(contents, _study_no+"*"+ano+"*"+SUBTRACTION_POSTCONTRAST_IMG_TYPE_FILTER)
            postcontrast_files = []
            for match in matches:
                postcontrast_files.append(os.path.join(_outputDir, match))

            ret_val = image_subtraction.do_image_subtraction(precontrast_file, postcontrast_files)
            if ret_val != 0:
                print "    ERROR calculating subtraction images. Skipping patient."
                continue


if __name__ == '__main__':
    main()