# -*- coding=utf-8-*-
import base64
import os

from Crypto.Cipher import AES


class AESUtil:
    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size

    @staticmethod
    def encryt(str, key):
        cipher = AES.new(key, AES.MODE_ECB)
        x = AESUtil.__BLOCK_SIZE_16 - (len(str) % AESUtil.__BLOCK_SIZE_16)
        if x != 0:
            str = str + chr(x) * x
        msg = cipher.encrypt(str)
        msg = base64.urlsafe_b64encode(msg)
        return msg

    @staticmethod
    def decrypt(enStr, key):
        cipher = AES.new(key, AES.MODE_ECB)
        enStr += (len(enStr) % 4) * "="
        decryptByts = base64.urlsafe_b64decode(enStr)
        msg = cipher.decrypt(decryptByts)
        paddingLen = ord(msg[len(msg) - 1])

        return msg[0:-paddingLen]


def aseDecode(s,k):
    bb = os.popen("echo " + s + " |xxd -r -ps | openssl base64")
    cc = bb.read()
    return AESUtil.decrypt(cc, k)

