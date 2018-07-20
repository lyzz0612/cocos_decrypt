#coding=utf8
import os
import shutil

from parse import get_sign
from parse import get_key_list
from xxtea import decrypt_file

OUTPUT_PATH = "./output"

def start_decrypt(so_file, src_path):
    sign = get_sign(src_path)
    if sign == "":
        print "error: src_path contains plain text files."
        return
    key_list = get_key_list(sign, so_file)
    if len(key_list) == 0:
        print "error: no valid key, check it manual."
        return
    global OUTPUT_PATH
    for key in key_list:
        print "try use key %s to decrypt" %(key)
        if os.path.exists(OUTPUT_PATH):
            shutil.rmtree(OUTPUT_PATH)
        os.mkdir(OUTPUT_PATH)

        is_right_key = False
        for parent, folders, files in os.walk(src_path):
            target_folder = parent.replace(src_path, OUTPUT_PATH)
            if not os.path.exists(target_folder):
                os.mkdir(target_folder)
            
            for file in files:
                full_path = os.path.join(parent, file)
                target_path = full_path.replace(src_path, OUTPUT_PATH)
                target_path = target_path.replace("luac", "lua")
                is_right_key = decrypt_file(full_path, key, target_path, sign)
                if not is_right_key:
                    print "invalid key %s on file %s" %(key, full_path)
                    break
            if not is_right_key:
                break
        if is_right_key:
            print "success"
            break

