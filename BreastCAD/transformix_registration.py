# -*- coding: utf-8 -*-
"""
Transformix wrapper
@author: Maggie Kusano
@date: November 22, 2015
"""


def do_transformix(transformix_exe, input_file, transform_parameters_file, output_file):
    '''

    '''
    import os
    import subprocess
    from shutil import move
    
    transformix_path = os.path.dirname(transformix_exe)
    if transformix_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + transformix_path

    output_directory = os.path.dirname(output_file)

    transformix_cmd = '"' + transformix_exe + '"' \
                      + ' -in ' + input_file \
                      + ' -out ' + output_directory \
                      + ' -tp ' + transform_parameters_file
    
    transformix_result = subprocess.call(transformix_cmd)

    # Use shutil.move instead of os.rename for cases when result.mha already exists.
    move(output_directory + os.sep + "result.mha", output_file)
    os.remove(output_directory + os.sep + "transformix.log")

    return transformix_result
