#coding=utf8
import os

from xxtea import decrypt_file
from parse import get_key_list
from decrypt import start_decrypt

start_decrypt("./libcocos2dcpp.so", "./src")
# print get_key_list("blsy", "./libcocos2dcpp.so")
# decrypt_file("./main.luac", "20160418blsyazNastuki", "./main.lua", "blsy")