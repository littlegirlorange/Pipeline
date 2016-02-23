# -*- coding: utf-8 -*-
"""
Perform Elastix registration on the input images.
@author: Maggie Kusano
@date: November 12, 2015
"""

import os
import glob
import subprocess
from shutil import move
import \
    fileinput  # repalce TransformParameters.0.txt with  patient_id1+'_TransformParameters.0.txt' in TransformParameters.1.txt'

def clean_elastix(output_directory):
    '''
    remove elatsix's registration intermediate files
    '''

    try:
        os.remove(output_directory + os.sep + "result.0.mha")
        os.remove(output_directory + os.sep + "elastix.log")
        for f_temp in glob.glob(output_directory + os.sep + "IterationInfo.*"):
            # Do what you want with the file
            os.remove(f_temp)
    except:
        pass


def do_elastix(elastix_exe, fixed, moving, output_directory, elastix_affine_pars, elastix_bspline_pars,
               fixed_mask='', moving_mask=''):
    '''
    1. do elastix registration
    2. rename
        1. TransformParameters.0.txt
        2. TransformParameters.1.txt
        3. result.1.mha
    3.  replace the "TransformParameters.0.txt" in TransformParameters.1.txt to new name
    '''

    elastix_cmd_result = 0
    elastix_path = os.path.dirname(elastix_exe)
    if elastix_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + elastix_path

    # Running multiple registrations in succession: affine first, the output of affine registration as input to the Bspline:
    # affine registered result: result.0.mha
    # Bspline registered result: result.1.mha

    # From elastix manual: A fixed image mask is sufficient to focus the registration on a ROI, since samples are drawn
    # from the fixed image. You only want to use a mask for the moving image when your moving image contains nonsense
    # grey values near the ROI.

    # Find fixed mask.
    if not fixed_mask:  # fixed_mask is empty
        elastix_cmd = '"' + elastix_exe + '"' + \
                      ' -f ' + fixed + \
                      ' -m ' + moving + \
                      ' -out ' + output_directory + \
                      ' -p ' + elastix_affine_pars + \
                      ' -p ' + elastix_bspline_pars

    else:
        elastix_cmd = '"' + elastix_exe + '"' + \
                      ' -f ' + fixed + \
                      ' -m ' + moving + \
                      ' -fMask ' + fixed_mask + \
                      ' -mMask ' + moving_mask + \
                      ' -out ' + output_directory + \
                      ' -p ' + elastix_affine_pars + \
                      ' -p ' + elastix_bspline_pars


    # this txt paramters will be used by transformix
    basename_fixed_moving = os.path.basename(fixed)[:-4] + '_' + os.path.basename(moving)[:-4]
    output_TransformParameters_0_txt = output_directory + os.sep + basename_fixed_moving + '_TransformParameters.0.txt'
    output_TransformParameters_1_txt = output_directory + os.sep + basename_fixed_moving + '_TransformParameters.1.txt'
    output_warped_image_elastix = output_directory + os.sep + basename_fixed_moving + '_reg.mha'

    print('doing: ' + elastix_cmd)
    # elastix_cmd_result = subprocess.call(elastix_cmd, stdout=FNULL, stderr=FNULL, shell=False)
    elastix_cmd_result = subprocess.call(elastix_cmd)

    # rename
    move(output_directory + os.sep + "TransformParameters.0.txt", output_TransformParameters_0_txt)
    move(output_directory + os.sep + "TransformParameters.1.txt", output_TransformParameters_1_txt)
    move(output_directory + os.sep + "result.1.mha", output_warped_image_elastix)
    # replace "TransformParameters.0.txt" to basename_fixed_moving+'_TransformParameters.0.txt',
    # since TransformParameters.1.txt will read basename_fixed_moving+'_TransformParameters.0.txt
    for line in fileinput.input(output_TransformParameters_1_txt, inplace=True):
        print(line.replace("TransformParameters.0.txt", basename_fixed_moving + '_TransformParameters.0.txt'))

    return elastix_cmd_result
