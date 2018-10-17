############################################################  
#                                                          #  
# The implementation of PHPRPC Protocol 3.0                #  
#                                                          #  
# xxtea.py                                                 #  
#                                                          #  
# Release 3.0.0                                            #  
# Copyright (c) 2005-2008 by Team-PHPRPC                   #  
#                                                          #  
# WebSite:  http://www.phprpc.org/                         #  
#           http://www.phprpc.net/                         #  
#           http://www.phprpc.com/                         #  
#           http://sourceforge.net/projects/php-rpc/       #  
#                                                          #  
# Authors:  Ma Bingyao <andot@ujn.edu.cn>                  #  
#                                                          #  
# This file may be distributed and/or modified under the   #  
# terms of the GNU Lesser General Public License (LGPL)    #  
# version 3.0 as published by the Free Software Foundation #  
# and appearing in the included file LICENSE.              #  
#                                                          #  
############################################################  
#  
# XXTEA encryption arithmetic library.  
#  
# Copyright (C) 2005-2008 Ma Bingyao <andot@ujn.edu.cn>  
# Version: 1.0  
# LastModified: Oct 5, 2008  
# This library is free.  You can redistribute it and/or modify it.  
  
import struct  
  
_DELTA = 0x9E3779B9  
  
def _long2str(v, w):  
    n = (len(v) - 1) << 2  
    if w:  
        m = v[-1]  
        if (m < n - 3) or (m > n): return ''  
        n = m  
    s = struct.pack('<%iL' % len(v), *v)  
    return s[0:n] if w else s  
  
def _str2long(s, w):  
    n = len(s)  
    m = (4 - (n & 3) & 3) + n  
    s = s.ljust(m, "\0")  
    v = list(struct.unpack('<%iL' % (m >> 2), s))  
    if w: v.append(n)  
    return v  
  
def encrypt(str, key):  
    if str == '': return str  
    v = _str2long(str, True)  
    k = _str2long(key.ljust(16, "\0"), False)  
    n = len(v) - 1  
    z = v[n]  
    y = v[0]  
    sum = 0  
    q = 6 + 52 // (n + 1)  
    while q > 0:  
        sum = (sum + _DELTA) & 0xffffffff  
        e = sum >> 2 & 3  
        for p in xrange(n):  
            y = v[p + 1]  
            v[p] = (v[p] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff  
            z = v[p]  
        y = v[0]  
        v[n] = (v[n] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[n & 3 ^ e] ^ z))) & 0xffffffff  
        z = v[n]  
        q -= 1  
    return _long2str(v, False)  
  
def decrypt(str, key):  
    if str == '': return str  
    v = _str2long(str, False)  
    k = _str2long(key.ljust(16, "\0"), False)  
    n = len(v) - 1  
    z = v[n]  
    y = v[0]  
    q = 6 + 52 // (n + 1)  
    sum = (q * _DELTA) & 0xffffffff  
    while (sum != 0):  
        e = sum >> 2 & 3  
        for p in xrange(n, 0, -1):  
            z = v[p - 1]  
            v[p] = (v[p] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff  
            y = v[p]  
        z = v[n]  
        v[0] = (v[0] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[0 & 3 ^ e] ^ z))) & 0xffffffff  
        y = v[0]  
        sum = (sum - _DELTA) & 0xffffffff  
    return _long2str(v, True)  

def decrypt_file(src_file, key, target_file=None, sign=""):
    with open(src_file, "rb") as file_obj:
        cipher_text = file_obj.read()
        plain_text = cipher_text

        sign_text = cipher_text[0:len(sign)]
        if sign_text == sign:
            cipher_text = cipher_text[len(sign):]
            plain_text = decrypt(cipher_text, key)

        if len(plain_text) == 0 and len(cipher_text) > 0:
            return False
        if target_file:
            with open(target_file, "w") as write_obj:
                write_obj.write(plain_text.replace("\r\n","\n"))
                write_obj.close()
        return True
    return False

if __name__ == "__main__":  
    print decrypt(encrypt('Hello XXTEA!', '16bytelongstring'), '16bytelongstring')  