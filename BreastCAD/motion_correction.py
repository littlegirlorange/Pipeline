# -*- coding: utf-8 -*-
"""
Perform optical flow motion correction on post-contrast MR images using the fat suppressed pre-contrast image.
@author: Maggie Kusano
@date: November 26, 2015
"""

import os
import subprocess
import fnmatch


def do_motion_correction(exe_file, fixed_file, moving_files):
    '''
    Call motion correction executable.
    '''

    exe_path = os.path.dirname(exe_file)
    if exe_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + exe_path

    exe_cmd = '"' + exe_file + '"' + \
              ' -f ' + fixed_file + \
              ' -m ' + moving_files[0] + ' ' + moving_files[1] + ' ' + moving_files[2] + ' ' + moving_files[3]

    print('doing: ' + exe_cmd)
    # cmd_result = subprocess.call(exe_cmd, stdout=FNULL, stderr=FNULL, shell=False)
    cmd_result = subprocess.call(exe_cmd)
    return cmd_result