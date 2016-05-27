__author__ = 'maggie'

# ======================================================================================================================
# Parameters
#

# General parameters
# ------------------
# Input study/accession number text file.
TASK_FILE = "D:\\Work\\BreastCAD\\TestData\\TestPipeline\\InSitu\\InSituList.txt"
DCM_INPUT_DIRECTORY = "M:\\maggieData\\InSitu"
# Output location.
OUTPUT_DIRECTORY = "D:\\Work\\BreastCAD\\TestData\\TestPipeline\\InSitu"

# DICOM to MHA conversion parameters
# ----------------------------------
# Skip conversion if re-running the pipeline.

# Path to dcm23d.exe.
DCM23D_EXE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\dcm23d.exe"
DCM23D_SERIES_DESC_FILTER = "Sag VIBRANT"  # Sag VIBRANT wo FS, pre-contrast and post contrast series
DCM23D_DICOM_FILE_FILTER = "MR.*"

# Optical flow motion correction parameters.
# --------------------------------------------
# Input image parameters.
MOTIONCORRECTION_FIXED_IMG_TYPE_FILTER = "_Sag.VIBRANT.MPH.mha"
MOTIONCORRECTION_MOVING_IMG_TYPE_FILTER = "_Ph*Sag.VIBRANT.MPH.mha"

# Path to motion correction program.
MOTIONCORRECTION_EXE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\motionCorrection.exe"

# Random forest breast segmentation parameters
# --------------------------------------------
# Input image parameters.
RFSEGMENTATION_IMG_TYPE_FILTER = "*.wo.FS.mha"

# Output image parameters.
RFSEGMENTATION_OUTPUT_FILE_POSTFIX = "_mask.mha"
RFSEGMENTATION_OUTPUT_PIXDIMS = [1.0, 1.0, 1.0]

# Path to Random Forest segmentation program.
RFSEGMENTATION_EXE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\breastSegmentation.exe"
RFSEGMENTATION_TRAINING_FILE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\opencv3.0_trained_training_15July_every_30_23_features_depth_50.xml"

# ANN lesion segmentation parameters
# ----------------------------------
# Input image parameters.
ANN_PRECONTRAST_IMG_TYPE_FILTER = "_Sag.VIBRANT.MPH.mha"
ANN_POSTCONTRAST_IMG_TYPE_FILTER = "_Ph*Sag.VIBRANT.MPH_mc.mha"
ANN_MASK_FILTER = RFSEGMENTATION_OUTPUT_FILE_POSTFIX

# Path to ANN lesion segmentation program.
ANN_EXE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\lesionSegmentation.exe"
ANN_TRAINING_MODEL = "D:\\Work\\BreastCAD\\Pipeline\\bin\\2_1_NS_NF.txt"

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

# Transformix registration parameters
# -------------------------------
TRANSFORMIX_EXE = "C:\\Program Files (x86)\\elastix\\transformix.exe"
TRANSFORMIX_PARAM_FILE_FILTER = "TransformParameters.1.txt"
TRANSFORMIX_IMG_TYPE_FILTER = [ANN_PRECONTRAST_IMG_TYPE_FILTER, ANN_POSTCONTRAST_IMG_TYPE_FILTER, "LesionProbMap.mha", RFSEGMENTATION_OUTPUT_FILE_POSTFIX]

# thresholdImage parameters
# -------------------------
THRESHOLD_EXE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\thresholdImage.exe"
THRESHOLD_IMG_TYPE_FILTER = ["LesionProbMap.mha", "LesionProbMap_reg.mha"]
THRESHOLD_OUTPUT_IMG_POSTFIX = "_thresh.mha"
THRESHOLD_MIN = 0.71
THRESHOLD_MAX = 1.0
THRESHOLD_FOREGROUND = 1

# removeVessel parameters
# -------------------------
REMOVEVESSEL_EXE = "D:\\Work\\BreastCAD\\Pipeline\\bin\\removeVessel.exe"
REMOVEVESSEL_IMG_TYPE_FILTER = THRESHOLD_OUTPUT_IMG_POSTFIX
REMOVEVESSEL_OUTPUT_IMG_POSTFIX = "_vr.mha"