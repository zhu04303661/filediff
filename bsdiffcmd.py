
# -*- coding:utf8 -*-

__author__ = 'eqzhu'

import os
import pdb

cmd_diff='~/build/bsdiff-4.3/bsdiff'
cmd_patch='~/build/bsdiff-4.3/bspatch'


def file_diff(src_path, dst_path, patch_path):
    """file_diff(src_path, dst_path, patch_path)

    Write a BSDIFF4-format patch (from the file src_path to the file dst_path)
    to the file patch_path.
    """

    cmd=cmd_diff+' '+ src_path+' '+dst_path+' '+patch_path
    print cmd
    os.system(cmd)


def file_patch(src_path, dst_path, patch_path):
    """file_patch(src_path, dst_path, patch_path)

    Apply the BSDIFF4-format file patch_path to the file src_path and
    write the result to the file dst_path.
    """

    cmd=cmd_patch+' '+ src_path+' '+dst_path+' '+patch_path
    print cmd
    os.system(cmd)
