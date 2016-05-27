# -*- coding: utf-8 -*-
"""
Extracts, renames, compresses and moves files for physician analysis.
@author: Maggie Kusano
@date: February 25, 2016
"""

import os
import fnmatch
from shutil import copy

import pipeline_utils as utils
from organize_data_params import *


def main():
    # ======================================================================================================================
    # Make sure everything exists before starting.
    #
    if not os.path.isfile(TASK_FILE):
        print "ERROR: TASK_FILE (" + TASK_FILE + ") does not exist."
        return 1
    if not os.path.exists(INPUT_DIRECTORY):
        print "ERROR: INPUT_DIRECTORY (" + INPUT_DIRECTORY + ") does not exist."
        return 1

    # ==================================================================================================================
    # And go...
    #
    # Open study list.
    print "Generating task list..."
    tasklist = utils.build_tasklist_Lara(TASK_FILE)

    for iItem, item in enumerate(tasklist):
        _study_id = item[0]
        _input_dir = INPUT_DIRECTORY + os.sep + _study_id
        _output_dir = OUTPUT_DIRECTORY + os.sep + _study_id
        if not os.path.exists(_output_dir):
            os.makedirs(_output_dir)
        if "CADPat" in _study_id:
            _study_no = _study_id.split("CADPat")[0]
        else:
            _study_no = _study_id

        print "======================================"
        print "Processing Patient: " + _study_id + "..."

        _accession_nos = item[1:]
        # Sort accession numbers so pre-biopsy scan is first.
        _accession_nos = sorted(_accession_nos, key=lambda x: int(x), reverse=True)
        if len(_accession_nos) != 3:
            print "ERROR: Too few accession numbers listed ({0}). Skipping.".format(str(len(_accession_nos)))
            continue
        _accession_no_fixed = _accession_nos[0]
        _accession_nos_moving = _accession_nos[1:]

        # --------------------------------------------------------------------------------------------------------------
        # Find 6 series for each patient (w/o fat sat, 4 subtraction images, mask image), all
        # registered to "fixed" (pre-biopsy study) space.
        #
        files_to_write = []
        contents = os.listdir(_input_dir)

        print "  Finding fixed ({0}) images...".format(_accession_no_fixed)
        print "    W/O fat sat"
        matches = fnmatch.filter(contents, _study_id+"*"+_accession_no_fixed+"*"+WO_FAT_SAT_FILTER+".mha")
        if len(matches) < 1:
            print "    W/O fat sat image not found"
            continue
        elif len(matches) > 1:
            print "    Too many W/O fat sat images found"
            continue
        wo_fat_sat_file_in = os.path.join(_input_dir, matches[0])
        fixed_basename_in = os.path.splitext(os.path.basename(wo_fat_sat_file_in))[0]
        parts = fixed_basename_in.split("_")
        parts[OUTPUT_FILENAME_INDICES["CADPatID"]] = _study_no  # Remove "CADPat" from patient ID
        del parts[INPUT_FILENAME_INDICES["DICOM_NO"]]           # Remove the DICOM number
        parts[OUTPUT_FILENAME_INDICES["SERIES_DESC"]] = "wo.FS" # Shorten the series description
        basename_out = ("_").join(parts)
        wo_fat_sat_file_out = os.path.join(_output_dir, basename_out+".mha")
        files_to_write.append([wo_fat_sat_file_in, wo_fat_sat_file_out])

        print "    Mask"
        matches = fnmatch.filter(contents, fixed_basename_in+MASK_FILTER+".mha")
        if len(matches) < 1:
            print "    Mask not found"
            continue
        elif len(matches) > 1:
            print "    Too many masks found"
            continue
        mask_file_in = os.path.join(_input_dir, matches[0])
        basename_in = os.path.splitext(os.path.basename(mask_file_in))[0]
        parts = basename_in.split("_")
        parts[OUTPUT_FILENAME_INDICES["CADPatID"]] = _study_no  # Remove "CADPat" from patient ID
        del parts[INPUT_FILENAME_INDICES["DICOM_NO"]]           # Remove the DICOM number
        del parts[OUTPUT_FILENAME_INDICES["SERIES_DESC"]]       # Remove the series description
        del parts[OUTPUT_FILENAME_INDICES["SERIES_NO"]]         # Remove the series number
        basename_out = ("_").join(parts)
        mask_file_out = os.path.join(_output_dir, basename_out+".mha")
        files_to_write.append([mask_file_in, mask_file_out])

        print "    Subtraction images"
        matches = fnmatch.filter(contents, _study_id+"*"+_accession_no_fixed+SUBTRACTION_FILTER+".mha")
        if len(matches) < 4:
            print "    Too few subtraction images found"
            continue
        elif len(matches) > 4:
            print "    Too many subtraction images found"
            continue
        for match in matches:
            file_in = os.path.join(_input_dir, match)
            basename_in = os.path.splitext(os.path.basename(file_in))[0]
            parts = basename_in.split("_")
            parts[OUTPUT_FILENAME_INDICES["CADPatID"]] = _study_no  # Remove "CADPat" from patient ID
            del parts[INPUT_FILENAME_INDICES["DICOM_NO"]]           # Remove the DICOM number
            basename_out = ("_").join(parts)
            file_out = os.path.join(_output_dir, basename_out+".mha")
            files_to_write.append([file_in, file_out])

        print "  Finding moving images..."
        for ano in _accession_nos_moving:
            print "    Finding {0}".format(ano)
            print "    W/O fat sat"
            matches = fnmatch.filter(contents, fixed_basename_in+"*"+ano+"*"+WO_FAT_SAT_FILTER+MOVING_FILTER+".mha")
            if len(matches) < 1:
                print "    W/O fat sat image not found"
                continue
            elif len(matches) > 1:
                print "    Too many W/O fat sat images found"
                continue
            wo_fat_sat_file_in = os.path.join(_input_dir, matches[0])
            moving_basename_in = os.path.splitext(os.path.basename(wo_fat_sat_file_in))[0]
            basename_in = moving_basename_in[len(fixed_basename_in)+1:]  # Remove fixed name from start of file name
            parts = basename_in.split("_")
            parts[OUTPUT_FILENAME_INDICES["CADPatID"]] = _study_no  # Remove "CADPat" from patient ID
            del parts[INPUT_FILENAME_INDICES["DICOM_NO"]]           # Remove the DICOM number
            parts[OUTPUT_FILENAME_INDICES["SERIES_DESC"]] = "wo.FS" # Shorten the series description
            del parts[-1]                                           # Remove _reg
            basename_out = ("_").join(parts)
            wo_fat_sat_file_out = os.path.join(_output_dir, basename_out+".mha")
            files_to_write.append([wo_fat_sat_file_in, wo_fat_sat_file_out])

            print "    Mask"
            matches = fnmatch.filter(contents, moving_basename_in[:-len(MOVING_FILTER)]+MASK_FILTER+MOVING_FILTER+".mha")
            if len(matches) < 1:
                print "    Mask not found"
                continue
            elif len(matches) > 1:
                print "    Too many masks found"
                continue
            mask_file_in = os.path.join(_input_dir, matches[0])
            basename_in = os.path.splitext(os.path.basename(mask_file_in))[0]
            basename_in = basename_in[len(fixed_basename_in)+1:]  # Remove fixed name from start of file name
            parts = basename_in.split("_")
            parts[OUTPUT_FILENAME_INDICES["CADPatID"]] = _study_no  # Remove "CADPat" from patient ID
            del parts[INPUT_FILENAME_INDICES["DICOM_NO"]]           # Remove the DICOM number
            del parts[OUTPUT_FILENAME_INDICES["SERIES_DESC"]]       # Remove the series description
            del parts[OUTPUT_FILENAME_INDICES["SERIES_NO"]]         # Remove the series number
            del parts[-1]  # Remove _reg
            basename_out = ("_").join(parts)
            mask_file_out = os.path.join(_output_dir, basename_out+".mha")
            files_to_write.append([mask_file_in, mask_file_out])

            print "    Subtraction images"
            matches = fnmatch.filter(contents, _study_id+"*"+ano+SUBTRACTION_FILTER+MOVING_FILTER+".mha")
            if len(matches) < 4:
                print "    Too few subtraction images found"
                continue
            elif len(matches) > 4:
                print "    Too many subtraction images found"
                continue
            for match in matches:
                file_in = os.path.join(_input_dir, match)
                basename_in = os.path.splitext(os.path.basename(file_in))[0]
                basename_in = basename_in[len(fixed_basename_in)+1:]  # Remove fixed name from start of file name
                parts = basename_in.split("_")
                parts[OUTPUT_FILENAME_INDICES["CADPatID"]] = _study_no  # Remove "CADPat" from patient ID
                del parts[INPUT_FILENAME_INDICES["DICOM_NO"]]           # Remove the DICOM number
                del parts[-1]  # Remove _reg
                basename_out = ("_").join(parts)
                file_out = os.path.join(_output_dir, basename_out+".mha")
                files_to_write.append([file_in, file_out])

        for files in files_to_write:
            copy(files[0], files[1])
            print files[1]

if __name__ == '__main__':
    main()
