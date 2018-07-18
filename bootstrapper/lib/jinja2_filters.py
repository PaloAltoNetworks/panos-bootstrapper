from passlib.hash import md5_crypt
from passlib.hash import des_crypt
from passlib.hash import sha512_crypt


defined_filters = ['md5_hash', 'des_hash', 'sha512_hash']


def md5_hash(txt):
    return md5_crypt.hash(txt)


def des_hash(txt):
    return des_crypt.hash(txt)


def sha512_hash(txt):
    return sha512_crypt.hash(txt)