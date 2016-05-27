__author__ = 'maggie'

# ======================================================================================================================
# Parameters
#

# General parameters
# ------------------
# Input study/accession number text file.
TASK_FILE = "M:\\Maggie\\LongitudinalStudy\\Data\\LaraInSituList.txt"
INPUT_DIRECTORY = "M:\\maggieData\\Lara\\InSitu"
# Output location.
OUTPUT_DIRECTORY = "M:\\maggieData\\Lara\\ToContour\\InSitu"
# File name indices.
INPUT_FILENAME_INDICES = {"CADPatID":0, "DICOM_NO":1, "SERIES_DATE":2, "ACCESSION_NO":3, "SERIES_NO":4, "SERIES_DESC":5}
OUTPUT_FILENAME_INDICES = {"CADPatID":0, "SERIES_DATE":1, "ACCESSION_NO":2, "SERIES_NO":3, "SERIES_DESC":4}

# W/O fat sat
WO_FAT_SAT_FILTER = "_Sag.VIBRANT.wo.FS"
MASK_FILTER = "_mask"
SUBTRACTION_FILTER = "_???-???"
MOVING_FILTER = "_reg"
