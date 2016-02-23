# -*- coding: utf-8 -*-
"""
Perform optical flow motion correction on post-contrast MR images using the fat suppressed pre-contrast image.
@author: Maggie Kusano
@date: November 26, 2015
"""

import os
import subprocess
import fnmatch


def do_threshold_image(exe_file, input_file, output_file, lower_threshold, upper_threshold, foreground_value):
    ''' Call thresholdImage executable.
    :param exe_file:
    :param input_file:
    :param output_file:
    :param lower_threshold:
    :param upper_threshold:
    :param foreground_value:
    :return:
    '''

    exe_path = os.path.dirname(exe_file)
    if exe_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + exe_path

    exe_cmd = '"' + exe_file + '"' + " " + '"' + input_file + '"' + " " + str(lower_threshold) + " " + str(upper_threshold) + " " + str(foreground_value) + " " + '"' + output_file

    print('doing: ' + exe_cmd)
    # cmd_result = subprocess.call(exe_cmd, stdout=FNULL, stderr=FNULL, shell=False)
    cmd_result = subprocess.call(exe_cmd)
    return cmd_result