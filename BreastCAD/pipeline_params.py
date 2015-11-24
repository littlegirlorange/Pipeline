__author__ = 'maggie'

# ======================================================================================================================
# Parameters
#

# General parameters
# ------------------
# Input study/accession number text file.
TASK_FILE = "D:\\Work\\BreastCAD\\TestData\\TestPipeline\\testPipeline.txt"
INPUT_DIRECTORY = "M:\\maggieData"
# Output location.
OUTPUT_DIRECTORY = "D:\\Work\\BreastCAD\\TestData\\TestPipeline"

# DICOM to MHA conversion parameters
# ----------------------------------
# Path to dcm23d.exe.
DCM23D_EXE = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\dcm23d\\bin\\dcm23d.exe"
DCM23D_SERIES_DESC_FILTER = "Sag VIBRANT"  # Sag VIBRANT wo FS, pre-contrast and post contrast series
DCM23D_DICOM_FILE_FILTER = "MR.*"

# Random forest breast segmentation parameters
# --------------------------------------------
# Input image parameters.
RFSEGMENTATION_IMG_TYPE_FILTER = "*.wo.FS.mha"

# Output image parameters.
RFSEGMENTATION_OUTPUT_FILE_POSTFIX = "_mask.mha"
RFSEGMENTATION_OUTPUT_PIXDIMS = [1.0, 1.0, 3.0]

# Path to Random Forest segmentation program.
RFSEGMENTATION_EXE = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\breastSegmentationRandomForest\\breastSegmentationRandomForest.exe"
RFSEGMENTATION_TRAINING_FILE = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\breastSegmentationRandomForest\\opencv3.0_trained_training_15July_every_30_23_features_depth_50.xml"

# Elastix registration parameters
# -------------------------------
# Use mask for registration?
ELASTIX_WITH_MASK = False  # False
ELASTIX_MASK_FILTER = RFSEGMENTATION_OUTPUT_FILE_POSTFIX

# Input image parameters.
ELASTIX_IMG_TYPE_FILTER = "*.wo.FS.mha"

# Path to Elastix and parameter files.
ELASTIX_EXE = "C:\\Program Files (x86)\\elastix\\elastix.exe"
ELASTIX_AFFINE_PAR_FILE = "elastix_pars_affine.txt"
ELASTIX_BSPLINE_PAR_FILE = "elastix_pars_bspline.txt"
TRANSFORMIX_EXE = "C:\\Program Files (x86)\\elastix\\transformix.exe"

# ANN lesion segmentation parameters
# ----------------------------------
# Input image parameters.
#INPUT_STUDY = "7199"
#INPUT_ACCESSION = "7709063"
ANN_IMG_TYPE_FILTER = ".MPH.mha"
ANN_MASK_FILTER = "_mask.mha"

# Output parameters.

# Path to ANN lesion segmentation program.
ANN_EXE = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\ANN_Deep_Learning_prediction\\ANNDeepLearningPrediction.exe"
ANN_TRAINING_MODEL = "D:\\Work\\BreastCAD\\Pipeline\\Bin\\ANN_Deep_Learning_prediction\\deep_learning_trained_model.txt"