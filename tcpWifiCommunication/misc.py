# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 23:00:21 2024

@author: Phatty
"""
#✓
# To do:  
import random, string, os, hashlib, time, socket

_SALTSIZE = 32

def docstring(docstr : str, sep : str ='\n'):
    def _decorator(callableObject):
        if callableObject.__doc__ is None:
            callableObject.__doc__ == docstr
            return docstr
        callableObject = sep.join([callableObject.__doc__, docstr])
        return callableObject
    return _decorator

def classDocstring(docstr : str, sep : str ='\n'):
    def _decorator(callableObject):
        if super(callableObject).__doc__ is None:
            callableObject.__doc__ == docstr
            return docstr
        callableObject = sep.join([docstr, super(callableObject).__doc__])
        return callableObject

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

def convertBytesToList(theBytes : bytes) -> list:
    return [theBytes[i] for i in range(len(theBytes))]

def convertListToBytes(theByteList : list) -> list:
    return bytes(theByteList)

def convertBytesToStr(theBytes : bytes) -> str:
    return " ".join([str(theBytes[i]) for i in range(len(theBytes))])

def convertStrToBytes(theBytesString : bytes) -> str:
    return bytes([int(value) for value in theBytesString.split(" ")])



def getRandomString(size : int):
    if size < 1 or not checkTypeSoft(size, int):
        raise TypeError("size parameter must be a positive integer value")
        return None
    return ''.join(random.choice(string.printable) for i in range(size))

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

def generateHash(textToHash: str, salt : bytes | None = None, textToHashEncoding : str = "utf-8") -> tuple:
    """
    

    Parameters
    ----------
    textToHash : str
        Text you want to hash
    salt : bytes | None, optional
        The salt you want to add. The default is None.
    textToHashEncoding : str, optional
        encoding of the text. The default is "utf-8".

    Returns
    -------
    hash and salt : bytes
        hash and salt as single bytes object
    saltSize : int
        the size of the salt

    """
    if salt is not None and not checkTypeSoft(salt, bytes):
        raise TypeError("Salt must be type <class 'NoneType'> or <class 'bytes'>")
    if salt is None:
        salt = os.urandom(_SALTSIZE*2)
    saltSize : int = len(salt)
    firstHash : bytes = hashlib.sha256(textToHash.encode(textToHashEncoding) + salt[:int(saltSize/2)])
    secondHash : bytes = hashlib.sha512(firstHash.digest() + salt[int(saltSize/2):])
    return secondHash.digest() + salt, saltSize

def splitHashSalt(hashSalt:bytes, saltSize : int) -> tuple:
    """
    

    Parameters
    ----------
    hashSalt : bytes
        DESCRIPTION.
    saltSize : int
        DESCRIPTION.

    Returns
    -------
    bytes
        DESCRIPTION.
    bytes
        DESCRIPTION.

    """
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

def dumpStuff(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

#socket stuff

def findDevice(device_IPOrName : str, isLocal : bool = True, numberIntervals : int = 5, intervalWaitTime : float = 1) -> tuple:
    """
    Find the name and ip of host by using name or ip

    Parameters
    ----------
    host_IPOrName : str
        IP example: 64.233.160.5
        the system name of device you want to find
    isLocal : bool, optional
        Binary value to determine weither to look for
        the device on the local area network, or on the internet
        this value only matters if using a name to search for device
        The default is True.
    numberIntervals : int, optional
        How many times the function will try to look for the device. 
        The default is 5.
    intervalWaitTime : float, optional
        Wait period in between search cycles.
        The measurement is in seconds The default is 1 for 1 second

    Raises
    ------
    ConnectionError
        if device cannot be located

    Returns
    -------
    tuple(str, str)
        tuple(host name, hostIP).

    """
    deviceIP : str = device_IPOrName * int((device_IPOrName[0]).isnumeric())
    deviceName : str =  device_IPOrName * int(deviceIP=="") 
    print(f"device name {deviceName}")
    print(f"device IP {deviceIP}")
    for count in range(numberIntervals):
        try:
            if deviceIP != "":
                deviceName = socket.gethostbyaddr(deviceIP)[0]
            #this block will never get ran if the the first if statement ran
            elif deviceName != "":
                deviceIP = socket.gethostbyname(deviceName + (".local" * isLocal))
            return deviceName, deviceIP
        except socket.gaierror or socket.herror:
            time.sleep(intervalWaitTime)
    error : str = ""
    if deviceName == "":
        error = "host"
    else:
        error = "local" * int(isLocal)
        error += f"host named \"{deviceName}\""
    if deviceIP != "":
        error += " with IP \"{deviceIP}\""
    error += " cannot be found"
    raise ConnectionError(error)
    return "", ""

def getConnected(serverIP : str, clientsocket,  port : int = 5050, numberIntervals : int = 5,  intervalWaitTime : float = 1):
    for _ in range(numberIntervals):
        if _ == numberIntervals -1:
            print("Last try before giving up")
        else:
            print("Server has refused to connect. Trying again")
        try:
            clientsocket.connect((serverIP,5050))
            print("Connected to server")
            return clientsocket
        except ConnectionRefusedError:
            time.sleep(intervalWaitTime)
            
    print("System has failed to connect with the server.")
    return None

