# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 23:00:21 2024

@author: Phatty
"""

import random, string, os, hashlib, time

_SALTSIZE = 32

def checkTypeHard(obj : object, class_or_tuple : object | tuple):
    if isinstance(obj, class_or_tuple):
        return True
    raise TypeError(f"object {id(object)} is type {type(obj)} and must be {type(class_or_tuple)}" )
def checkTypeSoft(obj : object, class_or_tuple : object | tuple):
    if isinstance(obj, class_or_tuple):
        return True
    return False

def checkTypesHard(obj : object, classes_or_tuples : tuple | list):
    if any([isinstance(obj, theType) for theType in classes_or_tuples]):
        return True
    raise TypeError(f"object {id(object)} is type {type(obj)} and must be {classes_or_tuples}" )
    return False
def checkTypesSoft(obj : object, classes_or_tuples : tuple | list):
    if any([isinstance(obj, theType) for theType in classes_or_tuples]):
        return True
    return False

def getRandomString(size : int):
    if size < 1 or not checkTypeSoft(size, int):
        raise TypeError("size parameter must be a positive integer value")
        return None
    randomString : str = ""
    for i in range(size):
        randomString += random.choice(string.printable)
    return randomString

def splitString(string : str, maxSubStringSize : int):
    if maxSubStringSize < 1 or not checkTypeSoft(maxSubStringSize, int):
        raise TypeError("maxSubStringSize parameter must be a positive integer value")
        return None
    if not checkTypeSoft(string, str):
        raise TypeError("string parameter must be type <str>")
        return None
    substrings : list = [''] * (int(len(string) / maxSubStringSize)+1)
    for index, char in enumerate(string):
        substrings[int(index/maxSubStringSize)] +=char
    return substrings

def generateHash(textToHash: str, salt : bytes | None = None, textToHashEncoding : str = "utf-8"):
    checkTypeHard(salt, bytes)
    if salt is None:
        salt = os.urandom(_SALTSIZE*2)
    saltSize : int = len(salt)
    firstHash = hashlib.sha256(textToHash.encode(textToHashEncoding) + salt[:int(saltSize/2)])
    secondHash = hashlib.sha512(firstHash.digest() + salt[int(saltSize/2):])
    return secondHash.digest() + salt, saltSize

def splitHashSalt(hashSalt:bytes, saltSize):
    hashTextSize : int = len(hashSalt) - saltSize
    return hashSalt[:hashTextSize], hashSalt[hashTextSize:]

def checkHashSalt(textToCheck : str, hashSalt : bytes, 
              saltSize : int, textEncoding : str = "utf-8"):
    _, salt = splitHashSalt(hashSalt, saltSize)
    generatedHash, _ = generateHash(textToCheck, salt, textEncoding)
    return generatedHash == hashSalt

def checkGeneratedHashTuple(textToCheck : str, generateHashReturns : tuple, 
                            textEncoding : str = "utf-8"):
    _, salt = splitHashSalt(generateHashReturns[0], generateHashReturns[1])
    generatedHash , _ = generateHash(textToCheck, salt)
    return generatedHash == generateHashReturns[0]




def createDirectory(path : str) -> bool:
    if os.path.exists(path):
        return False
    os.makedirs(path)
    return True
def createFile(path : str) -> bool:
    if os.path.exists(path):
        return False
    open(path, 'w').close()
    return True


def waitRandomTime(maxTime : float):
    try:
        maxTime = float(maxTime)
    except:
        checkTypesHard(maxTime, [int, float])
    timeToWait : float = random.random()*maxTime
    time.sleep(timeToWait)
    return None