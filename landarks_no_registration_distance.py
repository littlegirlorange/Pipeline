# -*- coding: utf-8 -*-
"""
measure the landmarks root mean square distance before registration

algorithm:
1. get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder
2. registration_tasklist
3. for e in range(0,len(registration_tasklist)):    
    fixed_coords: map_3d_pixel_to_physical_coordinates
    moving_coords: map_3d_pixel_to_physical_coordinates
    calc root mean square distance

@author: YingLi Lu
"""
import numpy as np

from utils import map_3d_pixel_to_physical_coordinates
from utils import get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder
from utils import get_registration_tasklist

#parameters
#This folder contains the clearCanvas generated key image and the original dicom image
input_folder = r'C:\ProgramData\ClearCanvas_Inc\ClearCanvas Workstation General\filestore'#input_folder = r'D:\1'
#fixed and moving mha images
mha_directory =  r'D:\15patienets30exames_landmark_registration_project\mha_data'

#patient categories
normal = ['133CADPat', '331CADPat', '388CADPat', '510CADPat', '3004CADPat']
benign = ['66CADPat','121CADPat','207CADPat','252CADPat','357CADPat']
malignant = ['114CADPat','171CADPat','619CADPat','651CADPat','0967CADPat']

patientID_accessNumber_seriesNumber_landmarkName_coords = get_patientID_accessNumber_seriesNumber_landmarkName_coords_from_dicom_folder(input_folder)
registration_tasklist = get_registration_tasklist(patientID_accessNumber_seriesNumber_landmarkName_coords,mha_directory)

dists=[]
benign_dists=[]
normal_dists=[]
malignant_dists=[]

for e in range(0,len(registration_tasklist)):    

    patient_id = registration_tasklist[e][0]
    fixed = registration_tasklist[e][2]
    fixed_coords = registration_tasklist[e][3]
    moving = registration_tasklist[e][4]
    moving_coords = registration_tasklist[e][5]

    mapped_fixed_coords = map_3d_pixel_to_physical_coordinates(fixed,fixed_coords)
    mapped_moving_coords = map_3d_pixel_to_physical_coordinates(moving,moving_coords)

    #compute distance
    dist = np.linalg.norm(np.array(mapped_fixed_coords) - np.array(mapped_moving_coords))
    dists.append(round(dist,2))
    
    if patient_id in normal:
        normal_dists.append(round(dist,2))
        
    if patient_id in benign:
        benign_dists.append(round(dist,2))
        
    if patient_id in malignant:
        malignant_dists.append(round(dist,2))
    
    print(dists)

np_dists = np.array(dists)
np_normal_dists = np.array(normal_dists)
np_benign_dists = np.array(benign_dists)
np_malignant_dists = np.array(malignant_dists)
   
print('all mean', round(np.mean(np_dists),2),'std',round(np.std(np_dists),2),'median',round(np.median(np_dists),2))
print('normal mean:', round(np.mean(np_normal_dists),2),'std',round(np.std(np_normal_dists),2),'median',round(np.median(np_normal_dists),2))
print('benign mean:', round(np.mean(np_benign_dists),2),'std',round(np.std(np_benign_dists),2),'median',round(np.median(np_benign_dists),2))
print('malignant mean:', round(np.mean(np_malignant_dists),2),'std',round(np.std(np_malignant_dists),2),'median',round(np.median(np_malignant_dists),2))

