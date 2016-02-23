# -*- coding: utf-8 -*-
"""
Remove vessels from the thresholded lesion probability map.
@author: Maggie Kusano
@date: December 8, 2015
"""

import os
import subprocess
import fnmatch


def do_remove_vessels(exe_file, input_file, output_file):
    ''' Call thresholdImage executable.
    :param exe_file:
    :param input_file:
    :param output_file:
    :return:
    '''

    exe_path = os.path.dirname(exe_file)
    if exe_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + exe_path

    exe_cmd = '"' + exe_file + '"' + \
              ' -i ' + input_file + \
              ' -o ' + output_file

    print('doing: ' + exe_cmd)
    # cmd_result = subprocess.call(exe_cmd, stdout=FNULL, stderr=FNULL, shell=False)
    cmd_result = subprocess.call(exe_cmd)
    return cmd_result