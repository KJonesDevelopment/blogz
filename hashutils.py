import hashlib
import random
import string


def makeSalt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])


def makePWH(password, salt=None):
    if not salt:
        salt = makeSalt()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash, salt)


def verifyPWH(password, hash):
    salt = hash.split(',')[1]
    if makePWH(password, salt) == hash:
        return True

    return False