# -*- coding: utf-8 -*-
"""
Convert DICOM-format breast MRI series to .mha format.
Based on YingLi's write_mha.py
Author: Maggie Kusano
Date: November 5, 2015
"""

import pipelineParams as params
import dicom
import fnmatch
import os
import subprocess
import os.path

FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess

# Path to patient DICOM data.
TOP_IN_DIR = "M:\\maggieData\\7199"

# Path to dcm23d.exe.
dcm23d_exe = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\dcm23d\\bin\\dcm23d.exe"

# .mha write path.
OUT_DIR = 'D:\\Work\\BreastCAD\\TestData'

# Series type to convert.
SERIES_DESC = "Sag VIBRANT"  # Sag VIBRANT wo FS, pre-contrast and post contrast series
DICOM_FILTER = "MR.*"

# Find all folders containing images with matching series descriptions.
matches = []
for path, dirnames, filenames in os.walk(TOP_IN_DIR):
    dicom_files = fnmatch.filter(filenames, DICOM_FILTER)
    if len(dicom_files) > 0:
         hdr = dicom.read_file(os.path.join(path, dicom_files[0]))
         series_description = hdr.get((0x0008, 0x103E), None).value
         if series_description.upper().find(SERIES_DESC.upper()) != -1:
             matches.append(path)

# Convert all matching series folders to .mha
for in_dir in matches:
    dcm23d_cmd = dcm23d_exe + ' -i ' + in_dir + ' -o ' + OUT_DIR
    print("Calling " + dcm23d_cmd)
    dcm23d_cmd_result = subprocess.call(dcm23d_cmd, stdout=FNULL, stderr=FNULL, shell=False)
