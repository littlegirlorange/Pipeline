# -*- coding: utf-8 -*-
"""
Perform Elastix registration on the input images.
@author: Maggie Kusano
@date: November 12, 2015
"""

import os
import subprocess
import numpy as np

import \
    fileinput  # repalce TransformParameters.0.txt with  patient_id1+'_TransformParameters.0.txt' in TransformParameters.1.txt'
import time

from utils import map_3d_pixel_to_physical_coordinates
from utils import get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder
from utils import get_registration_tasklist
from utils import elastix_transformix_points_by_indices


def clean_elastix(output_directory):
    '''
    remove elatsix's registration intermediate files
    '''
    import os
    import glob

    try:
        # elastix.exe
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

    from breastSegmentation import applyBreastSegmentation
    import pickle

    # Load the breastSegmentation classifier.
    # if 'breastSegmentationModeldict' not in globals():
    #     pfile = open(os.path.dirname(applyBreastSegmentation.__file__) + os.sep + 'bin' + os.sep + 'hessian100texw_24July.pkl', 'rb')
    #     global breastSegmentationModeldict
    #     applyBreastSegmentation.breastSegmentationModeldict = pickle.load(pfile)
    #     pfile.close

    elastix_cmd_result = 0

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
    output_warped_image_elastix = output_directory + os.sep + basename_fixed_moving + '_warped_elastix.mha'

    if not os.path.exists(output_warped_image_elastix):
        print('doing: ' + elastix_cmd)
        # elastix_cmd_result = subprocess.call(elastix_cmd, stdout=FNULL, stderr=FNULL, shell=False)
        elastix_cmd_result = subprocess.call(elastix_cmd)

        # rename
        os.rename(output_directory + os.sep + "TransformParameters.0.txt", output_TransformParameters_0_txt)
        os.rename(output_directory + os.sep + "TransformParameters.1.txt", output_TransformParameters_1_txt)
        os.rename(output_directory + os.sep + "result.1.mha", output_warped_image_elastix)

        # replace "TransformParameters.0.txt" to basename_fixed_moving+'_TransformParameters.0.txt',
        # since TransformParameters.1.txt will read basename_fixed_moving+'_TransformParameters.0.txt
        for line in fileinput.input(output_TransformParameters_1_txt, inplace=True):
            print(line.replace("TransformParameters.0.txt", basename_fixed_moving + '_TransformParameters.0.txt'))

    return elastix_cmd_result


current_path = os.path.dirname(os.path.abspath(__file__))
FNULL = open(os.devnull, 'w')  # use this if you want to suppress output to stdout from the subprocess

# parameters
with_mask = False  # False

# fixed and moving mha images
input_directory = r'D:\Work\Breast\MHA\Test'
output_directory = r'D:\Work\Breast\MHA\Test\Output'
fixed = input_directory + os.sep + "4086CADPat_34197_20130810_7575799_5_Sag.VIBRANT.wo.FS.mha"
moving = input_directory + os.sep + "4086CADPat_10952_20120519_7142554_5_Sag.VIBRANT.wo.FS.mha"

# elastix registration
elastix_exe = 'C:/Program Files (x86)/elastix/elastix.exe'
elastix_affine_pars = current_path + os.sep + 'elastix_pars_affine.txt'
elastix_bspline_pars = current_path + os.sep + 'elastix_pars_bspline.txt'
transformix_exe = 'C:/Program Files (x86)/elastix/transformix.exe'

do_elastix(elastix_exe, fixed, moving, output_directory, elastix_affine_pars, elastix_bspline_pars)


'''# # patient categories
# normal = ['133CADPat', '331CADPat', '388CADPat', '510CADPat', '3004CADPat']
# benign = ['66CADPat', '121CADPat', '207CADPat', '252CADPat', '357CADPat']
# malignant = ['114CADPat', '171CADPat', '619CADPat', '651CADPat', '0967CADPat']
#
# # get [ [patient_id,accession_number,series_number,landmark_name,[x,y,z]] ]
# patientID_accessNumber_seriesNumber_landmarkName_coords = get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder(
#     input_folder)
# # get [ [patient_id,landmark_name,fixed,fixed_coords,moving,moving_coords] ] to use by registration
# registration_tasklist = get_registration_tasklist(patientID_accessNumber_seriesNumber_landmarkName_coords,
#                                                   mha_directory)

# f = open( registration_tasklist_no_fs, 'w')
# for item in registration_tasklist:
#    f.write(str(item))
#    f.write(str('\n'))
# f.close()
benign_dists = []
normal_dists = []
malignant_dists = []
registration_tasklist_with_dist = []
elastix_time = []

dists = []
for e in range(0, len(registration_tasklist)):
    patient_id = registration_tasklist[e][0]
    fixed = registration_tasklist[e][2]
    fixed_coords = registration_tasklist[e][3]
    moving = registration_tasklist[e][4]
    moving_coords = registration_tasklist[e][5]

    ##do elastix registration
    start_time = time.time()
    if with_mask:  # do ants with mask
        fixed_mask = fixed[:-4] + '_mask.mha'
        moving_mask = moving[:-4] + '_mask.mha'
    else:
        fixed_mask = ''
        moving_mask = ''

    # fixed_mask = output_directory+os.path.sep+os.path.basename(fixed)+"_mask.mha" #breast mask image filename
    # moving_mask = output_directory+os.path.sep+os.path.basename(moving)+"_mask.mha"
    do_elastix(elastix_exe, fixed, moving, output_directory, elastix_affine_pars, elastix_bspline_pars, fixed_mask,
               moving_mask)
    if (time.time() - start_time > 0.1):  # if do elastix registration
        elastix_time.append(time.time() - start_time)
        print(elastix_time)

    # apply transformation to fixed coords and map to physical coordinates
    basename_fixed_moving = os.path.basename(fixed)[:-4] + '_' + os.path.basename(moving)[:-4]
    TransformParameters_last_txt = output_directory + os.sep + basename_fixed_moving + '_TransformParameters.1.txt'
    transformed_fixed_coords = elastix_transformix_points_by_indices(transformix_exe, fixed_coords,
                                                                     TransformParameters_last_txt, output_directory)

    # map the moving coordinates from pixel to physical
    mapped_moving_coords = map_3d_pixel_to_physical_coordinates(moving, moving_coords)

    # compute distance
    dist = np.linalg.norm(np.array(transformed_fixed_coords) - np.array(mapped_moving_coords))
    dists.append(round(dist, 2))
    registration_tasklist_with_dist.append([round(dist, 2), registration_tasklist[e]])

    if patient_id in normal:
        normal_dists.append(round(dist, 2))

    if patient_id in benign:
        benign_dists.append(round(dist, 2))

    if patient_id in malignant:
        malignant_dists.append(round(dist, 2))

    print(dists)

np_dists = np.array(dists)
np_normal_dists = np.array(normal_dists)
np_benign_dists = np.array(benign_dists)
np_malignant_dists = np.array(malignant_dists)

print('all mean: %.1f, std: %.1f, median: %.1f' % (np.mean(np_dists), np.std(np_dists), np.median(np_dists)))
print('normal mean: %.1f, std: %.1f, median: %.1f' % (
np.mean(np_normal_dists), np.std(np_normal_dists), np.median(np_normal_dists)))
print('normal mean: %.1f, std: %.1f, median: %.1f' % (
np.mean(np_benign_dists), np.std(np_benign_dists), np.median(np_benign_dists)))
print('malignant mean: %.1f, std: %.1f, median: %.1f' % (
np.mean(np_malignant_dists), np.std(np_malignant_dists), np.median(np_malignant_dists)))
print('time: %.1f' % (np.mean(np.array(elastix_time))))
'''
# remove intermediate files
clean_elastix(output_directory)
