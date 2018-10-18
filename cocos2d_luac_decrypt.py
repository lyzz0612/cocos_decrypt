# /usr/bin/env python
# -*-coding:utf-8 -*-
# @Author  : c4bbage
# @Link    : http://xxxxx.ooooo
# @Version :$ID$
# @Date    : 2018-10-17 13:26:46
# @Last Modified by:   c4bbage
# @Last Modified time: 2018-10-17 13:26:46

"""
unzip apk
提取sign 提取key 解密luac
"""

import os
import sys
import re
import binascii

import argparse
import zipfile
import xxtea


def extract_apk(apkPath, outputDir="output", sign=None, key=None):
    luacFiles = soFiles = []
    soluaFiles = ['libcocos2dcpp.so', 'libcocos2dlua.so', 'libhellolua.so']
    if os.path.exists(apkPath):
        fileName = os.path.splitext(os.path.basename(apkPath))[0]
        outputDir = os.path.join(outputDir, fileName)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
        zipFile = zipfile.ZipFile(apkPath)
        for names in zipFile.namelist():
            zipFile.extract(names, outputDir)
            if os.path.splitext(names)[-1] == '.luac':
                if sign and key:
                    xxtea.decrypt_file(src_file=os.path.join(
                        outputDir, names), key=key, target_file=os.path.join(outputDir, names), sign=sign)
                luacFiles.append(os.path.join(outputDir, names))
            for i in soluaFiles:
                if i in names:
                    soFiles.append(os.path.join(outputDir, names))
        zipFile.close()
    else:
        exit(u'apk file not found')
    return luacFiles, soFiles


def decrypt_dir(dir, sign, key):
    for root, dirs, files in os.walk(dir):
        for f in files:
            if os.path.splitext(f)[-1] == ".luac":
                xxtea.decrypt_file(src_file=os.path.join(
                    root, f), key=key, target_file=os.path.join(root, f), sign=sign)


def get_key_contain(so_path, sign):
    may_contain = None
    with open(so_path, "rb") as file_obj:
        buffer_cache = file_obj.read(1024*1024)
        while buffer_cache:
            index = buffer_cache.find(sign)
            if index != -1:
                may_contain = buffer_cache[index-100:index+110]
                break
            buffer_cache = file_obj.read(1024*1024)
    return may_contain


def parse_key_simple(key):
    if len(key) <= 3:
        return False
    SystemTextSimple = ["AppDelegate", "package", "preload", "main", "ENTER", "BACKGROUND", "EVENT", "FOREGROUND",
                        "cocos", "android", "core", "cancel", "touch", "armature", "Bone", "path", "error",
                        "module", "loading", "from", "file", "loaders", "strlogpath", "vector", "login", "insert",
                        "game", "update", "share", "directory", "clean"]
    for text in SystemTextSimple:
        if key.upper().find(text.upper()) != -1:
            return False
    return True


def get_guess_key_list(may_contain):
    may_contain = re.sub(r"[^a-zA-Z0-9 ]", " ", may_contain)
    may_contain = re.sub(r" [ ]+", " ", may_contain)

    may_list = may_contain.split(" ")
    may_list = filter(parse_key_simple, may_list)
    return may_list


def get_key_list(sign, so_path):
    may_contain = get_key_contain(so_path, sign)
    if not may_contain:
        return []
    key_list = get_guess_key_list(may_contain)
    if sign in key_list:
        key_list.remove(sign)
    return key_list


def guess_sign(luacFiles):
    length = 2 if luacFiles.__len__() < 3 else 3
    fileHeader = []
    sign = ''
    mix_length = 101
    for f in list(set(luacFiles))[0:length]:
        x = open(f).read(100)
        x = binascii.b2a_hex(x)
        fileHeader.append(x.strip())
        if mix_length > x.__len__():
            mix_length = x.__len__()
    for i in range(mix_length):
        s = fileHeader[0][i]
        yes = True
        for c in range(1, length):
            if not s == fileHeader[c][i]:
                yes = False
        if yes:
            sign += s
    return binascii.a2b_hex(sign)


def main():
    parser = argparse.ArgumentParser(
        add_help=True, description="cocos2d luac decrypt tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
example:
    {prog} -f 1.apk -o output                       # Y auto parse apk
    {prog} -f 1.apk -s aaaaaaa -k bbbbbbb           # Y
    {prog} -f 1.apk -o output -s aaaaaaa -k bbbbbbb # Y
    {prog} -d dir -s aaaaaaa -k bbbbbbb             # Y""".format(prog=sys.argv[0]))
    parser.add_argument('-f', dest="apkFile",
                        help='apk file')
    parser.add_argument('-o', dest="output", default="output",
                        help="output dir")
    parser.add_argument('-d', dest="dir",
                        help="luac dir")
    parser.add_argument('-s', dest="sign", default="",
                        help="xxtea sign")
    parser.add_argument('-k', dest="key", default="",
                        help="xxtea key")
    args = parser.parse_args()
    import pprint
    if args.sign and args.key and args.apkFile:
        extract_apk(args.apkFile, args.output, sign=args.sign, key=args.key)
    elif args.sign and args.key and args.dir:
        pprint.pprint(decrypt_dir(args.dir, args.sign, args.key))
    elif args.apkFile and (args.sign == ''):
        sign = ''
        key = ''
        luacFiles, soFiles = extract_apk(args.apkFile, args.output)
        if luacFiles.__len__() > 1:
            sign = guess_sign(luacFiles)
        else:
            exit('not found Luac file')
        if soFiles.__len__() > 0:
            for soFile in soFiles:
                # 一般情况是存在于 strings soFile|grep -i key -A 3 -B 3
                key = get_key_list(sign, soFile)
                for k in key:
                    if xxtea.decrypt_file(luacFiles[0], k, luacFiles[0], sign):
                        pprint.pprint("sign:{} ,key:{}".format(sign, k))
                        for luac in luacFiles[1:]:
                            xxtea.decrypt_file(luac, k, luac, sign)
        else:
            exit('not found so file')


if __name__ == '__main__':
    main()
