# -*- coding: utf-8 -*-
"""
This program extract the arrow landmark coordinates and slice number from the clearCanvas generated "Grayscale Softcopy Presentation State Storage SOP Class"
dicom image.

the list_with_keyimages_sorted.txt was used to manually fill the unlabelled landmark of the key images(see 15patients_landmark_registration.txt for details).

@author: YingLi Lu
"""

import dicom
from dicom.filereader import InvalidDicomError
import fnmatch
import os

#parameters
#This folder contains the clearCanvas generated key image and the original dicom image
input_folder = r'C:\ProgramData\ClearCanvas_Inc\ClearCanvas Workstation General\filestore'
#input_folder = r'D:\1'

#1031531SHSC 7122489  has key image, but the match 1031531SHSC 7368076 has no key image
exclude_list=["1031531SHSC"]

match_criteria = '*.dcm'  #sometime mightbe *.dcm

#find match files with full path
matches = []
for path, dirnames, filenames in os.walk(input_folder):
  for filename in fnmatch.filter(filenames, match_criteria):
    matches.append(os.path.join(path, filename))

f=open(r'D:\15patienets30exames_landmark_registration_project\list_with_keyimages.txt','w+');

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
                    
                        x,y = h[0x0070,0x0001][i][0x0070,0x0008][0][0x0070,0x0014].value #(0070, 0014) Anchor Point  FL: [219.42855834960938, 277.7142333984375]
                        landmark_name = h[0x0070,0x0001][i][0x0070,0x0008][0][0x0070,0x0006].value
                        
                        #get which image is the landmark drawn on                
                        image_instance_uid = h[0x0070,0x0001][0][0x0008,0x1140][0][0x0008,0x1155].value                
                        image_full_path = os.path.dirname(item)+os.sep+image_instance_uid+'.dcm'
                                        
                        #get slice number
                        hh=dicom.read_file(image_full_path)
                        z = hh.get((0x0020,0x0013),None).value #instanceNumber
                        patient_id = hh.get((0x0010, 0x0020),None).value
                        accession_number= hh.get((0x0008, 0x0050),None).value
                        series_number =hh.get((0x0020,0x0011),None).value
                        series_description=hh.get((0x0008,0x103e),None).value
        
                        #map DICOM voxel coordiante to patient coordinate
                        if patient_id in exclude_list:
                            continue
                        
                        #print  image_instance_uid
                        print>>f, patient_id,accession_number,landmark_name, x,y,z,series_number,series_description,item,image_instance_uid+'.dcm'
                
    except IOError:
        print 'No such file: ' + image_full_path
    except InvalidDicomError:
        print 'Invalid Dicom file:' + item 

f.close()

#sort lines
f=open(r'D:\15patienets30exames_landmark_registration_project\list_with_keyimages.txt','r');
lines = f.readlines()
lines.sort()
f.close()
f_sorted = open(r'D:\15patienets30exames_landmark_registration_project\list_with_keyimages_sorted.txt', 'w')
f_sorted.writelines(lines) # Write a sequence of strings to a file
f_sorted.close()
