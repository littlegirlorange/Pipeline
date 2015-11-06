
# -*- coding: utf-8 -*-
"""
This code do ants registration and compare landmarks distance after registration

@author: YingLi Lu
"""
import os
import subprocess
import numpy as np
import time

from utils import map_3d_pixel_to_physical_coordinates
from utils import get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder
from utils import get_registration_tasklist
from utils import antsApplyTransformsToPoints



def do_ants(ants_exe,fixed,moving,output_transform_prefix,ouput_warped_image_ants,fixed_mask='', moving_mask = ''):
    #Running multiple registrations in succession: affine first, the output of affine registration as input to the SyN:
    #' --masks ['+fixed_mask+','+moving_mask+']' \
    if not (fixed_mask and moving_mask): #fixed_mask is empty    
        ants_cmd = ants_exe + \
            ' -d 3 --float'\
            ' -m mi[' + fixed +' , ' + moving + ',1' + ',32]' \
            ' -t rigid[ 0.1 ]'  \
            ' -c [ 40x20x10,1.e-3,20 ]' \
            ' -s 2x2x1mm -f 2x2x1' \
            ' -m mi['+fixed+' , ' + moving + ',1' + ',32]' \
            ' -t SyN[1.0,2.0,0.05]' \
            ' -c 40x20x10' \
            ' -s 2x2x1mm' \
            ' -f 2x2x1' \
            ' -o [' + output_transform_prefix +','+ouput_warped_image_ants +']'
    else:
        ants_cmd = ants_exe + \
            ' -d 3 --float'\
            ' -m mi[' + fixed +' , ' + moving + ',1' + ',32]' \
            ' -t rigid[ 0.1 ]'  \
            ' -c [ 40x20x10,1.e-3,20 ]' \
            ' -s 2x2x1mm -f 2x2x1' \
            ' --masks ['+fixed_mask+','+moving_mask+']' \
            ' -m mi['+fixed+' , ' + moving + ',1' + ',32]' \
            ' -t SyN[1.0,2.0,0.05]' \
            ' -c 40x20x10' \
            ' -s 2x2x1mm -f 2x2x1' \
            ' --masks ['+fixed_mask+','+moving_mask+']' \
            ' -o [' + output_transform_prefix +','+ouput_warped_image_ants +']'
          
    #this txt paramters will be used by transformix
    basename_fixed_moving = os.path.basename(fixed)[:-4] + '_' +os.path.basename(moving)[:-4]
    output0GenericAffine_mat = output_directory+os.sep+basename_fixed_moving+'_ouput0GenericAffine.mat'
    ouput1Warp_nii_gz = output_directory+os.sep+basename_fixed_moving+'_ouput1Warp.nii.gz'
    ouput1InverseWarp_nii_gz = output_directory+os.sep+basename_fixed_moving+'_ouput1InverseWarp.nii.gz'
    output_warped_image_ants = output_directory+os.sep+basename_fixed_moving+'_warped_ants.mha'
#    
    if not os.path.exists(output_warped_image_ants):
        print('doing: '+ants_cmd)
        subprocess.call(ants_cmd, stdout=FNULL, stderr=FNULL, shell=True)    
        #rename result.1.mha, result.1.mha is the warped image name fixed in elastix executable
        os.rename(output_directory+os.sep+"ouput0GenericAffine.mat",output0GenericAffine_mat)
        os.rename(output_directory+os.sep+"ouput1Warp.nii.gz",ouput1Warp_nii_gz) 
        os.rename(output_directory+os.sep+"ouput1InverseWarp.nii.gz",ouput1InverseWarp_nii_gz)
        os.rename(output_directory+os.sep+"warped_ants.mha",output_warped_image_ants)


current_path = os.path.dirname(os.path.abspath(__file__))
FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess

#parameters

#do ants with masks?
with_mask = False 
#This folder contains the clearCanvas generated key image and the original dicom image
input_folder = r'C:\ProgramData\ClearCanvas_Inc\ClearCanvas Workstation General\filestore'#input_folder = r'D:\1'
mha_directory =  r'D:\15patienets30exames_landmark_registration_project\mha_data'
#results and intermediate results come to here
if with_mask:
    output_directory = r'D:\15patienets30exames_landmark_registration_project\results\ants_with_mask'
else:
    output_directory = r'D:\15patienets30exames_landmark_registration_project\results\ants'

###do ants registration
ants_exe = 'C:/ANTS_2.1_2015_02_17/bin/Release/ANTSregistration.exe'
output_transform_prefix = output_directory+os.sep+'ouput'
ouput_warped_image_ants = output_directory+os.sep+'warped_ants.mha'

antsApplyTransformsToPoints_exe = 'C:/ANTS_2.1_2015_02_17/bin/Release/antsApplyTransformsToPoints.exe'

#patient categories
normal = ['133CADPat', '331CADPat', '388CADPat', '510CADPat', '3004CADPat']
benign = ['66CADPat','121CADPat','207CADPat','252CADPat','357CADPat']
malignant = ['114CADPat','171CADPat','619CADPat','651CADPat','0967CADPat']

#get [ [patient_id,accession_number,series_number,landmark_name,[x,y,z]] ] 
patientID_accessNumber_seriesNumber_landmarkName_coords = get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder(input_folder)
#get [ [patient_id,landmark_name,fixed,fixed_coords,moving,moving_coords] ] to use by registration
registration_tasklist = get_registration_tasklist(patientID_accessNumber_seriesNumber_landmarkName_coords,mha_directory)

normal = ['133CADPat', '331CADPat', '388CADPat', '510CADPat', '3004CADPat']
benign = ['66CADPat','121CADPat','207CADPat','252CADPat','357CADPat']
malignant = ['114CADPat','171CADPat','619CADPat','651CADPat','0967CADPat']

dists=[]
benign_dists=[]
normal_dists=[]
malignant_dists=[]
registration_tasklist_with_dist=[]
ants_time=[]        
    
for e in range(0,len(registration_tasklist)):    
    patient_id = registration_tasklist[e][0]
    fixed = registration_tasklist[e][2]
    fixed_coords = registration_tasklist[e][3]
    moving = registration_tasklist[e][4]
    moving_coords = registration_tasklist[e][5]

    start_time = time.time()

    if with_mask: #do ants with mask
        fixed_mask=fixed[:-4]+'_mask.mha'
        moving_mask=moving[:-4]+'_mask.mha'
    else:
        fixed_mask=''
        moving_mask=''
    
    #fixed_mask = output_directory+os.path.sep+os.path.basename(fixed)+"_mask.mha" #breast mask image filename
    #moving_mask = output_directory+os.path.sep+os.path.basename(moving)+"_mask.mha"
    do_ants(ants_exe,fixed,moving,output_transform_prefix,ouput_warped_image_ants,fixed_mask, moving_mask)
    if (time.time()-start_time > 0.1): #if do elastix registration
        ants_time.append(time.time()-start_time)
        print(ants_time)
        
    
    #####measure landmark coords distance, steps
        #1. map moving coordinates to physical coords
        #2. write ants_inputPoints.csv
        #3. antsApplyTransformsToPoints -d 3 -i ants_inputPoints.csv -o ants_outputPoints.csv -t [output0GenericAffine_mat ,1 ] -t ouput1InverseWarp_nii_gz
        #4. read ants_outputPoints.csv
        #5. map fixed coordinates to physical coords
        #6. calc distance
    #map moving coordinates from pixel to physical coords   
    mapped_moving_coords = map_3d_pixel_to_physical_coordinates(moving,moving_coords)

    #apply transform to mapped moving coords
    basename_fixed_moving = os.path.basename(fixed)[:-4] + '_' +os.path.basename(moving)[:-4]
    output0GenericAffine_mat = output_directory+os.sep+basename_fixed_moving+'_ouput0GenericAffine.mat'
    ouput1InverseWarp_nii_gz = output_directory+os.sep+basename_fixed_moving+'_ouput1InverseWarp.nii.gz'
    
    transformed_moving_coords = antsApplyTransformsToPoints(antsApplyTransformsToPoints_exe,mapped_moving_coords,output_directory,output0GenericAffine_mat,ouput1InverseWarp_nii_gz)
    
    #map fixed coords from pixel to physical coords
    mapped_fixed_coords = map_3d_pixel_to_physical_coordinates(fixed,fixed_coords)
    
    #compute distance
    dist = np.linalg.norm(np.array(transformed_moving_coords) - np.array(mapped_fixed_coords))
    dists.append(round(dist,2))
    registration_tasklist_with_dist.append([round(dist,2),registration_tasklist[e]])
    
    if patient_id in normal:
        normal_dists.append(round(dist,2))
        
    if patient_id in benign:
        benign_dists.append(round(dist,2))
        
    if patient_id in malignant:
        malignant_dists.append(round(dist,2))
        
    print(dists)
    
    print(dists)

np_dists = np.array(dists)
np_normal_dists = np.array(normal_dists)
np_benign_dists = np.array(benign_dists)
np_malignant_dists = np.array(malignant_dists)
   
print('all mean: %.1f, std: %.1f, median: %.1f' %(np.mean(np_dists),np.std(np_dists),np.median(np_dists)))
print('normal mean: %.1f, std: %.1f, median: %.1f' %(np.mean(np_normal_dists),np.std(np_normal_dists),np.median(np_normal_dists)))
print('normal mean: %.1f, std: %.1f, median: %.1f' %(np.mean(np_benign_dists),np.std(np_benign_dists),np.median(np_benign_dists)))
print('malignant mean: %.1f, std: %.1f, median: %.1f' %(np.mean(np_malignant_dists),np.std(np_malignant_dists),np.median(np_malignant_dists)))
print('time: %.1f' %(np.mean(np.array(elastix_time))))

