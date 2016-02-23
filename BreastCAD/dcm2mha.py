# -*- coding: utf-8 -*-
"""
Convert DICOM-format breast MRI series to .mha format.
Based on YingLi's write_mha.py
Author: Maggie Kusano
Date: November 5, 2015
"""

import dicom
import fnmatch
import os
import subprocess

FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess

def do_dcm2mha(dcm23d_exe, input_directory, output_directory, dicom_filter="MR.*", series_description_filter=""):

    # Find all folders containing images with matching series descriptions.
    matchingSeriesPaths = []
    for path, dirnames, filenames in os.walk(input_directory):
        dicomFiles = fnmatch.filter(filenames, dicom_filter)
        if len(dicomFiles) > 0:
            hdr = dicom.read_file(os.path.join(path, dicomFiles[0]))
            seriesDescription = hdr.get((0x0008, 0x103E), None).value
            if seriesDescription.upper().find(series_description_filter.upper()) != -1:
                matchingSeriesPaths.append(path)

    # Convert all matching series folders to .mha
    for path in matchingSeriesPaths:
        dcm23d_cmd = dcm23d_exe + ' -i ' + path + ' -o ' + output_directory
        print("Calling " + dcm23d_cmd)
        try:
            dcm23d_cmd_result = subprocess.call(dcm23d_cmd, stdout=FNULL, stderr=FNULL, shell=False)
        except OSError:
            print "OSError: " + dcm23d_cmd + " not found."

