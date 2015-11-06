
# -*- coding: utf-8 -*-
"""
This program extract the arrow landmark coordinates and slice number from the clearCanvas generated "Grayscale Softcopy Presentation State Storage SOP Class"
dicom image.

use dcm23d.exe to write convert series with landmark to mha
1. get list: patientID_accession_number
2. sort it, the smaller accession_number was defined as fixed image for registration
3. the mha file was named: patientID_accessNumber_seriesNumber_fixed/moving.mha

Note: the reason to seriesNumber in mha filename is because the radiologist, for a patient, labled landmarks on different series .

Created on Mon Jun 22 13:21:46 2015

@author: YingLi Lu
"""

import dicom
from dicom.filereader import InvalidDicomError
import fnmatch
import os
import subprocess
import os.path

FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess

#parameters
dcm23d_exe=r'C:\dcm23d\dcm23d.exe'
#This folder contains the clearCanvas generated key image and the original dicom image
input_folder = r'C:\ProgramData\ClearCanvas_Inc\ClearCanvas Workstation General\filestore'
#output mha files
ouput_folder=r'D:\15patienets30exames_landmark_registration_project\mha_data'

#1031531SHSC 7122489  has key image, but the match 1031531SHSC 7368076 has no key image
exclude_list=["1031531SHSC"]

#find match files with full path
match_criteria = '*.dcm'  #sometime mightbe *.dcm
matches = []
for path, dirnames, filenames in os.walk(input_folder):
  for filename in fnmatch.filter(filenames, match_criteria):
    matches.append(os.path.join(path, filename))


patientID_accessionNumber=[]; #sort it, then use it to define fixed and moving image for registration
for item in matches:
    #print item
    try:
        filename = os.path.basename(item)
        if filename[0:5] == "2.25.": #key image filename start with 2.25.
            h=dicom.read_file(item)
            val = h.get((0x008,0x0016),None)
            if val:
                if val.value=="1.2.840.10008.5.1.4.1.1.11.1": #Grayscale Softcopy Presentation State Storage SOP Class
                    #get landmark coordinates in voxel index
                    for i in range(0,len(h[0x0070,0x0001].value)): #multiple sequence
                    
                        #get which image is the landmark drawn on                
                        image_instance_uid = h[0x0070,0x0001][0][0x0008,0x1140][0][0x0008,0x1155].value                
                        image_full_path = os.path.dirname(item)+os.sep+image_instance_uid+'.dcm'
                                        
                        #get slice number
                        hh=dicom.read_file(image_full_path)
                        patient_id = hh.get((0x0010, 0x0020),None).value
                        accession_number= hh.get((0x0008, 0x0050),None).value
                        
                        #map DICOM voxel coordiante to patient coordinate
                        if patient_id in exclude_list:
                            continue
                        
                        patientID_accessionNumber.append(patient_id+'_'+str(accession_number))
                
    except IOError:
        print 'No such file: ' + image_full_path
    except InvalidDicomError:
        print 'Invalid Dicom file:' + item 

#####get fixed moving: smaller accession number is fixed
patientID_accessionNumber_sorted = list(set(patientID_accessionNumber)) #remove duplicates and then sort it.
patientID_accessionNumber_sorted.sort()

fixed_moving = ['fixed'] * len(patientID_accessionNumber_sorted)
for i in range(len(patientID_accessionNumber_sorted)):
    if i%2: #smaller accession number is fixed, becasue of set()
        fixed_moving[i]='moving'


#write mha
for item in matches:
    try:
        filename = os.path.basename(item)
        if filename[0:5] == "2.25.": #key image filename start with 2.25.
            h=dicom.read_file(item)
            val = h.get((0x008,0x0016),None)
            if val:
                if val.value=="1.2.840.10008.5.1.4.1.1.11.1": #Grayscale Softcopy Presentation State Storage SOP Class
                    #get landmark coordinates in voxel index
                    for i in range(0,len(h[0x0070,0x0001].value)): #multiple sequence
                    
                        #get which image is the landmark drawn on                
                        image_instance_uid = h[0x0070,0x0001][0][0x0008,0x1140][0][0x0008,0x1155].value                
                        image_full_path = os.path.dirname(item)+os.sep+image_instance_uid+'.dcm'
                                        
                        #get slice number
                        hh=dicom.read_file(image_full_path)
                        patient_id = hh.get((0x0010, 0x0020),None).value
                        accession_number= hh.get((0x0008, 0x0050),None).value
                        series_number =hh.get((0x0020,0x0011),None).value
                        
                        #map DICOM voxel coordiante to patient coordinate
                        if patient_id in exclude_list:
                            continue
                        
                        #fixed or moving
                        fixed_or_moving = fixed_moving[patientID_accessionNumber_sorted.index(patient_id+'_'+str(accession_number))]
                        output_filename = patient_id+'_'+str(accession_number)+'_'+str(series_number)+'_'+fixed_or_moving
                        input_folder =  os.path.dirname(item); #dicom images folder
                        
                        if not os.path.exists(ouput_folder+os.sep+output_filename+'.mha'):
                            dcm23d_cmd = dcm23d_exe + \
                            ' -i "' + input_folder +'"' \
                            ' -o ' + ouput_folder + \
                            ' -s ' + str(series_number) + \
                            ' -n  ' + output_filename
                            print("doing " + dcm23d_cmd)
                            dcm23d_cmd_result = subprocess.call(dcm23d_cmd, stdout=FNULL, stderr=FNULL, shell=False)
                    
    except IOError:
        print 'No such file: ' + image_full_path
    except InvalidDicomError:
        print 'Invalid Dicom file:' + item 
