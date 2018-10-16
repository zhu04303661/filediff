# -*- coding:utf8 -*-

__author__ = 'cosyman'

import os
import filecmp
from os.path import join, splitext
import logging
import zipfile
import bsdiff4
import bsdiffcmd

import sys

import config
from fileutil import *

logger = logging.getLogger(__name__)

def diff_zip_V2(zf1, zf2, target,fullBundleMd5, release_version, ptach_enable=False):
    """
    tager= zf2 - zf1
    >>> diff_zip('/Users/cosyman/Downloads/bs2/car_original.zip',
    ... '/Users/cosyman/Downloads/bs2/car_new.zip','./.tmp/3.zip')
    ... None

    :param zf1:
    :param zf2:
    :param target:
    :return:
    """

    dir1 = splitext(zf1)[0]
    dir2 = splitext(zf2)[0]

    unzipand7z(zf1, dir1)
    unzipand7z(zf2, dir2)
    diff_dir2_V2(dir1, dir2, target,fullBundleMd5, release_version, ptach_enable)

def diff_zipand7z(zf1, zf2, target,ptach_enable=False):
    """
    tager= zf2 - zf1
    >>> diff_zip('/Users/cosyman/Downloads/bs2/car_original.zip',
    ... '/Users/cosyman/Downloads/bs2/car_new.zip','./.tmp/3.zip')
    ... None

    :param zf1:
    :param zf2:
    :param target:
    :return:
    """

    dir1 = splitext(zf1)[0]
    dir2 = splitext(zf2)[0]

    unzipand7z(zf1, dir1)
    unzipand7z(zf2, dir2)
    diff_dir2zip(dir1, dir2, target,ptach_enable)

def diff_zip(zf1, zf2, target,ptach_enable=False):
    """
    tager= zf2 - zf1
    >>> diff_zip('/Users/cosyman/Downloads/bs2/car_original.zip',
    ... '/Users/cosyman/Downloads/bs2/car_new.zip','./.tmp/3.zip')
    ... None

    :param zf1:
    :param zf2:
    :param target:
    :return:
    """

    dir1 = splitext(zf1)[0]
    dir2 = splitext(zf2)[0]

    unzip(zf1, dir1)
    unzip(zf2, dir2)
    diff_dir2zip(dir1, dir2, target,ptach_enable)

def diff_dir2_V2(dir1, dir2, target,fullBundleMd5, release_version, ptach_enable):
    """
    只差分添加和已存在的文件,并压缩至target文件 tager= dir2 - dir1
    >>> diff_dir2zip('/Users/cosyman/Downloads/bs2/car','/Users/cosyman/Downloads/bs2/car 2',
    ... '/Users/cosyman/Downloads/bs2/car.p.zip')
    ... None

    :param dir1:
    :param dir2:
    :param target:
    :return:
    """
    files1 = []
    files2 = []
    diff_files = []
    debug_files = []

    for root, dirs, files in os.walk(dir1):
        for name in files:
            files1.append(join(root, name))
            # logger.debug('diff old : %s',    name)
    for root, dirs, files in os.walk(dir2):
        for name in files:
            files2.append(join(root, name))
            # logger.debug('new old : %s', name)

    for file2 in files2:
        f2_f1 = file2.replace(dir2, dir1)
        if f2_f1.endswith('.DS_Store'):
            continue
        elif f2_f1 not in files1:
            # logger.debug('---not exist file in old ,  new is %s',  file2.split('/')[-1])
            diff_files.append(file2)
            debug_files.append(file2.replace(dir2, 'added '))
        elif not filecmp.cmp(f2_f1, file2, shallow=False):
            # logger.debug('---different file old %s : new %s', f2_f1.split('/')[-1],file2.split('/')[-1])
            if ptach_enable == True:
                pathc_name=file2 + '.diff'
                # bsdiff4.file_diff(f2_f1, file2, pathc_name)
                diff_file(f2_f1, file2, pathc_name)
                if verfiy_patch_file(f2_f1, file2, pathc_name) == False:
                    logger.error('[ERROR] %s revert patch verfiy have fail, please check package',pathc_name)
                    sys.exit(1)

                diff_files.append(pathc_name)

                #add diff file's md5 check
                md5value = file_md5(file2)
                md5filename=file2+'.hash'
                with open(md5filename, 'w') as f:
                    f.write(md5value)
                diff_files.append(md5filename)
                debug_files.append(md5filename.replace(dir2, 'added '))
                logger.debug("new file:%s md5 is %s",md5filename.split('/')[-1],md5value)

                debug_files.append((pathc_name).replace(dir2, 'diff '))
            else:
                diff_files.append(file2)
                debug_files.append(file2.replace(dir2, 'replaced'))
        # else:
            # logger.debug('---same file old:%s, new:%s ',f2_f1.split('/')[-1], file2.split('/')[-1])


    logger.debug('diff info summary: \nolddir:%s\nnewdir:%s\ndiff:\n%s',
                 dir1, dir2, '\n'.join(sorted(debug_files)))

    if(len(diff_files) == 0 ):
        rootfilelist = os.listdir(dir2)
        if(len(rootfilelist) == 1):
                flagefile = join(dir2,rootfilelist[0], "_nodiff_mcd.txt")
        else:
                flagefile = join(dir2, "_nodiff_mcd.txt")

        #flagefile = join(dir2, "_nodiff_mcd.txt")
        with open(flagefile, 'w') as f:
            f.write("nodiff found")
        diff_files.append(flagefile)
        debug_files.append(flagefile.replace(dir2, 'added '))
        logger.debug("_nodiff add")

    if(float(release_version) >= 713):
        fullbundlehashfile = join(dir2, "__fullbundleso.hash")
        with open(fullbundlehashfile, 'w') as f:
            f.write(fullBundleMd5)
        diff_files.append(fullbundlehashfile)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for tar in diff_files:
            arc_name = tar[len(dir2):]
            zf.write(tar, arc_name)



    traget_7z = target.split(".zip")[0] + ".7z"
    traget_dir = target.split(".zip")[0]
    zipTo7zv2(target, traget_7z)

    logger.debug('creat diff package: [[[ %s ]]]',traget_7z)


def diff_dir2zip(dir1, dir2, target,ptach_enable):
    """
    只差分添加和已存在的文件,并压缩至target文件 tager= dir2 - dir1
    >>> diff_dir2zip('/Users/cosyman/Downloads/bs2/car','/Users/cosyman/Downloads/bs2/car 2',
    ... '/Users/cosyman/Downloads/bs2/car.p.zip')
    ... None

    :param dir1:
    :param dir2:
    :param target:
    :return:
    """
    files1 = []
    files2 = []
    diff_files = []
    debug_files = []

    for root, dirs, files in os.walk(dir1):
        for name in files:
            files1.append(join(root, name))
            # logger.debug('diff old : %s',    name)
    for root, dirs, files in os.walk(dir2):
        for name in files:
            files2.append(join(root, name))
            # logger.debug('new old : %s', name)

    for file2 in files2:
        f2_f1 = file2.replace(dir2, dir1)
        if f2_f1.endswith('.DS_Store'):
            continue
        elif f2_f1 not in files1:
            # logger.debug('---not exist file in old ,  new is %s',  file2.split('/')[-1])
            diff_files.append(file2)
            debug_files.append(file2.replace(dir2, 'added '))
        elif not filecmp.cmp(f2_f1, file2, shallow=False):
            # logger.debug('---different file old %s : new %s', f2_f1.split('/')[-1],file2.split('/')[-1])
            if ptach_enable == True:
                pathc_name=file2 + '.diff'
                # bsdiff4.file_diff(f2_f1, file2, pathc_name)
                diff_file(f2_f1, file2, pathc_name)
                if verfiy_patch_file(f2_f1, file2, pathc_name) == False:
                    logger.error('[ERROR] %s revert patch verfiy have fail, please check package',pathc_name)
                    sys.exit(1)

                diff_files.append(pathc_name)

                #add diff file's md5 check
                md5value = file_md5(file2)
                md5filename=file2+'.hash'
                with open(md5filename, 'w') as f:
                    f.write(md5value)
                diff_files.append(md5filename)
                debug_files.append(md5filename.replace(dir2, 'added '))
                logger.debug("new file:%s md5 is %s",md5filename.split('/')[-1],md5value)

                debug_files.append((pathc_name).replace(dir2, 'diff '))
            else:
                diff_files.append(file2)
                debug_files.append(file2.replace(dir2, 'replaced'))
        # else:
            # logger.debug('---same file old:%s, new:%s ',f2_f1.split('/')[-1], file2.split('/')[-1])


    logger.debug('diff info summary: \nolddir:%s\nnewdir:%s\ndiff:\n%s',
                 dir1, dir2, '\n'.join(sorted(debug_files)))

    if(len(diff_files) == 0 ):
        rootfilelist = os.listdir(dir2)
        if(len(rootfilelist) == 1):
                flagefile = join(dir2,rootfilelist[0], "_nodiff_mcd.txt")
        else:
                flagefile = join(dir2, "_nodiff_mcd.txt")

        #flagefile = join(dir2, "_nodiff_mcd.txt")
        with open(flagefile, 'w') as f:
            f.write("nodiff found")
        diff_files.append(flagefile)
        debug_files.append(flagefile.replace(dir2, 'added '))
        logger.debug("_nodiff add")

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for tar in diff_files:
            arc_name = tar[len(dir2):]
            zf.write(tar, arc_name)
    logger.debug('creat diff package: [[[ %s ]]]',target)


def diff_file(src_path, dst_path, patch_path ):
    """
    patch_path = dst_path - src_path

    >>> diff_dir2zip('/Users/cosyman/Downloads/bs2/car','/Users/cosyman/Downloads/bs2/car 2',
    ... '/Users/cosyman/Downloads/bs2/car.p.zip')
    ... None

    :param file1:
    :param file2:
    :param target:
    :return:
    """

    bsdiff4.file_diff(src_path, dst_path, patch_path )
    #bsdiffcmd.file_diff(src_path, dst_path, patch_path )


def patch_file(src_path, dst_path,patch_path):
    """
    dst_path = src_path + patch_path

    >>> diff_dir2zip('/Users/cosyman/Downloads/bs2/car','/Users/cosyman/Downloads/bs2/car 2',
    ... '/Users/cosyman/Downloads/bs2/car.p.zip')
    ... None

    :param file1:
    :param file2:
    :param target:
    :return:
    """

    bsdiff4.file_patch(src_path, dst_path, patch_path)
    #bsdiffcmd.file_patch(src_path, dst_path, patch_path)

def verfiy_patch_file(src_path, dst_path,patch_path):
    patched_new_packge = src_path + ".new"
    patch_file(src_path, patched_new_packge, patch_path)

    if filecmp.cmp(patched_new_packge, dst_path, shallow=1):
        logger.debug('revert verfiy have successed')
        os.remove(patched_new_packge)
        return True
    else:
        logger.error('[ERROR] %s revert verfiy have fail, please check package', src_path)
        return  False

if __name__ == '__main__':
    config.init_log()
