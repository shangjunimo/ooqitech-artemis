# coding: utf8
import hashlib
import logging
import os
from binascii import a2b_hex, b2a_hex

from Crypto.Cipher import AES

logger = logging.getLogger('deploy.app')


class Crypt_V2():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)

        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')


class Crypt():
    def __init__(self):
        self.key = 'aaaaaaaaaaaaaaaa'
        self.mode = AES.MODE_CBC

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)

        return b2a_hex(self.ciphertext)

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')


class Md5():

    @classmethod
    def md5sum(self, filepath):

        assert os.path.isfile(filepath)
        try:
            md5 = hashlib.md5()
            f = file(filepath, 'rb')
            while True:
                b = f.read(8096)
                if not b:
                    break
                md5.update(b)
            return md5.hexdigest()
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.info('{}md5sum计算失败'.format(filepath))
            return 'md5sudefaultsum'
