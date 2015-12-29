
# -*- coding: utf-8 -*-
"""
This code generate breast masks using ant's applyBreastSegmentation.py

@author: YingLi Lu

"""
import os
import pickle

import sys
from applyBreastSegmentation import *

mha_directory = r'D:\15patienets30exames_landmark_registration_project\mha_data'
#results and intermediate results come to here
output_directory = r'D:\15patienets30exames_landmark_registration_project\temp' 

##load the classifier - just do this once
#if 'breastSegmentationModeldict' not in globals():
#    pfile = open(r'D:\PythonCode\Anne_Breast_segmentation\breastSegmentation\bin\hessian100texw_24July.pkl','rb')
#    breastSegmentationModeldict = pickle.load(pfile)
#    pfile.close
    

task_list = ['0967CADPat_6917974_6_fixed.mha',
'0967CADPat_6938015_6_moving.mha',
'114CADPat_6734489_7_fixed.mha',
'114CADPat_6896014_5_moving.mha',
'121CADPat_6714524_7_fixed.mha',
'121CADPat_7091267_5_moving.mha',
'121CADPat_7091267_601_moving.mha',
'207CADPat_4842067_5_fixed.mha',
'207CADPat_4982884_5_moving.mha',
'252CADPat_6700964_5_fixed.mha',
'252CADPat_7050431_6_moving.mha',
'331CADPat_5175225_7_fixed.mha',
'331CADPat_6705315_7_moving.mha',
'357CADPat_4888079_5_fixed.mha',
'357CADPat_5137030_6_moving.mha',
'388CADPat_4733182_5_fixed.mha',
'388CADPat_5417838_7_moving.mha',
'619CADPat_6886996_5_fixed.mha',
'619CADPat_7250777_6_moving.mha',
'651CADPat_4695822_5_fixed.mha',
'651CADPat_5139220_7_moving.mha']

#These subtract images can not be apply to Anne's breast segmentation algorithm directly(there are some holes in the breast mask).
#use same patient's access#'s "Sag VIBRANT wo FS" (or "Sag VIBRANT MPH" if no "Sag VIBRANT wo FS" ) series, convert to mha file, then rename it.	
mha_directory = r'D:\15patienets30exames_landmark_registration_project\renamed_mha_data'
task_list = [
'121CADPat_6714524_10801_fixed.mha',
'121CADPat_7091267_10601_moving.mha',
'133CADPat_4733206_10601_fixed.mha',
'133CADPat_4928930_10601_moving.mha',
'171CADPat_4337379_10601_fixed.mha',
'171CADPat_4746431_10601_moving.mha']

    
for e in task_list:
    
    input_file = mha_directory+ os.sep + e
    output_file = output_directory+ os.sep + e[:-4] + "_mask.mha"  
    
    print("segmenting: ", input_file)
    segmentBreast(input_file,output_file,6)    
