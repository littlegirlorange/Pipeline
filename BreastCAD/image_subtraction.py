# -*- coding: utf-8 -*-
"""
@author: Maggie Kusano
@date: December 29, 2015
"""

import os
import SimpleITK as sitk
from pipeline_params_Lara import *


def do_image_subtraction(precontrast_file, postcontrast_files):
    '''
    Calculate subtraction images from DCE MR data in .mha format.
    Results are saved to same folder as the pre-contrast image file.
    :rtype : signed int
    Files are named:
        <pre-cont basename>_<post-cont series no>-<pre-cont series no>.mha
        E.g., 7184CADPat_31623_20130405_7420191_601-600.mha
    :param precontrast_file: Full path to .mha format pre-contrast series.
    :param postcontrast_files: List of full paths to .mha format post-contrast series (should be 4).
    :return: Status: 0-ok, -1-failure.
    '''
    reader = sitk.ImageFileReader()
    reader.SetFileName(precontrast_file)
    precontrast_image = reader.Execute()
    caster = sitk.CastImageFilter()  # Post-contrast images are doubles due to motion correction.
    basename = os.path.splitext(os.path.basename(precontrast_file))[0]
    dirname = os.path.dirname(precontrast_file)
    parts = basename.split("_")
    precontrast_basename = ("_").join(parts[0:FILENAME_INDICES["SERIES_NO"]])
    precontrast_series_no = parts[FILENAME_INDICES["SERIES_NO"]]
    subtraction_filter = sitk.SubtractImageFilter()

    for postcontrast_file in postcontrast_files:
        reader.SetFileName(postcontrast_file)
        postcontrast_image = reader.Execute()
        if not postcontrast_image:
            return -1

        caster.SetOutputPixelType(postcontrast_image.GetPixelIDValue())
        subtraction_image = subtraction_filter.Execute(postcontrast_image,
                                                       caster.Execute(precontrast_image))
        if not subtraction_image:
            return -1

        basename = os.path.splitext(os.path.basename(postcontrast_file))[0]
        parts = basename.split("_")
        postcontrast_series_no = parts[FILENAME_INDICES["SERIES_NO"]]
        output_file = os.path.join(dirname, precontrast_basename + "_" + postcontrast_series_no +
                                   "-" + precontrast_series_no + ".mha")
        writer = sitk.ImageFileWriter()
        writer.SetFileName(output_file)
        writer.Execute(subtraction_image)
    
    return 0




