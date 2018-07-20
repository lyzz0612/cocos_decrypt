#coding=utf8
import os
import shutil
import argparse
import zipfile

from decrypt import start_decrypt

APK_UNZIP_FOLDER = "./unzip"

def unzip_apk(apk_path, unzip_root):
    if os.path.exists(unzip_root):
        shutil.rmtree(unzip_root)
    os.mkdir(unzip_root)
    
    zip_file = zipfile.ZipFile(apk_path)
    for names in zip_file.namelist():  
        zip_file.extract(names, unzip_root)  
    zip_file.close()  
    

def choose_sofile(root_path):
    lib_path = os.path.join(root_path, "lib")
    so_list = []
    for parent, folders, files in os.walk(lib_path):
        for file in files:
            if file.endswith(".so"):
                so_list.append(os.path.join(parent, file))
    index = 0
    for so_file in so_list:
        print "%d: %s" %(index, so_file.replace(root_path, ""))
        index = index + 1
    index = input("choose so file: ")
    return so_list[index]

def choose_src_path(root_path):
    assets_path = os.path.join(root_path, "assets")
    folder_list = []
    for parent, folders, files in os.walk(assets_path):
        releative_path = parent.replace(root_path, "")
        if releative_path.count(os.path.sep) > 3:
            continue
        for folder in folders:
            folder_list.append(os.path.join(parent, folder))
    index = 0
    for folder_path in folder_list:
        print "%d: %s" %(index, folder_path.replace(root_path, ""))
        index = index + 1
    index = input("choose src folder: ")
    return folder_list[index]

    
#解析参数       
def parse_args():
    parser = argparse.ArgumentParser(description='cocos安卓游戏xxtea解密工具.')
    parser.add_argument('--apkfile', dest='apkfile', type=str, required=False, help='apk文件路径')
    parser.add_argument('--srcpath', dest='srcpath', type=str, required=False, help='luac目录')
    parser.add_argument('--sofile', dest='sofile', type=str, required=False, help='so文件路径')

    args = parser.parse_args()
    return args

def main():
    app_args = parse_args()
    if app_args.apkfile:
        global APK_UNZIP_FOLDER
        unzip_apk(app_args.apkfile, APK_UNZIP_FOLDER)
        sofile = choose_sofile(APK_UNZIP_FOLDER)
        srcpath = choose_src_path(APK_UNZIP_FOLDER)
        
        start_decrypt(sofile, srcpath)
    elif app_args.srcpath and app_args.sofile:
        if not os.path.exists(app.sofile):
            print "error: sofile is not exists."
            exit(0)
        if not os.path.exists(app.srcpath):
            print "error: srcpath is not exists."
            exit(0)
        
        start_decrypt(app_args.sofile, app_args.srcpath)
    else:
        print "error params. use --help to see more."
    
if __name__ == "__main__":
    main()