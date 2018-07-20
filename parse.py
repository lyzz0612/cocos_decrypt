#coding=utf8
import os
import sys
import re

SystemTextSimple = ["AppDelegate", "package", "preload", "main", "ENTER", "BACKGROUND", "EVENT", "FOREGROUND",
                    "cocos", "android", "core", "cancel", "touch", "armature", "Bone", "path", "error",
                    "module", "loading", "from", "file", "loaders", "strlogpath", "vector", "login", "insert",
                    "game", "update", "share", "directory", "clean"]


def get_sign(folder_path):
    first_file, second_file = None, None
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)
        if os.path.isfile(full_path):
            if not first_file:
                first_file = full_path
            elif not second_file:
                second_file = full_path
            else:
                break
    
    print "use file %s and %s to get sign." %(first_file.replace(folder_path, ""), 
                                              second_file.replace(folder_path, ""))

    guess_sign1 = ""
    with open(first_file, "rb") as file_obj:
        guess_sign1 = file_obj.read(20)
        file_obj.close()
        
    guess_sign2 = ""
    with open(second_file, "rb") as file_obj:
        guess_sign2 = file_obj.read(20)
        file_obj.close()
    sign = ""
    for i in range(20):
        if guess_sign1[i] == guess_sign2[i]:
            sign = sign + guess_sign1[i]
        else:
            break
    return sign

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
    global SystemText
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
    print "sign: " + sign

    may_contain = get_key_contain(so_path, sign)
    if not may_contain:
        print "not found plain sign."
        return []
    
    print "here is the text may contain key: \n%s\n" %(may_contain)

    key_list = get_guess_key_list(may_contain)
    key_list.remove(sign)
    return key_list

if __name__ == "__main__":
    pass