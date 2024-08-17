# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 16:28:42 2024

@author: Phatty
"""
from misc import generateHash, createDirectory, splitHashSalt, createFile, checkHashSalt, waitRandomTime
import os, json, time, random, configparser, copy
class LockedEventFile():
    _lockedDir : str = "MyMessageData"
    _configDirectory : str = _lockedDir + os.sep + "master.ini"
    _lockedFileExtention = ".dat"
    _saltSize : int = 64
    __configDict : dict = {"hashSalt" : None,
                           "size" : (None,None),
                           "endianness" : "",
                           "lockedCommands" : []}
    def __init__(self, commandName : str):
        """
        Used to access and change master password
        Used to lock a command and check if the command is locked

        Parameters
        ----------
        commandName : str
            the name of the command

        """
        self._commandName = commandName
        
    
    @staticmethod
    def initalizeConfigFile(password : str, textEncoding : str = "utf-8",
                            endianness : str = "big"):
        if createFile(LockedEventFile._configDirectory) is True:
            config = configparser.ConfigParser()
            salt : bytes = os.urandom(LockedEventFile._saltSize)
            setupDictionary : dict = copy.deepcopy(LockedEventFile.__configDict)
            hashSalt, saltSize = generateHash(password,salt, textEncoding)
            setupDictionary["hashSalt"] = int.from_bytes(hashSalt, endianness)
            setupDictionary["size"] = (len(hashSalt), saltSize)
            setupDictionary["endianness"] = endianness
            config["main"] = setupDictionary
            with open(LockedEventFile._configDirectory, 'w') as file:
                config.write(file)
            return True
        raise IOError("File already has been created")
        return False
    
    @staticmethod
    def changePassword(oldPassword : str, newPassword : str, textEncoding : str = "utf-8",
                       endianness : str ="big"):
        ...
    @staticmethod
    def _checkPassword(password : str, textEncoding : str = "utf-8"):
        config = configparser.ConfigParser()
        config.read(LockedEventFile())   
    
    # def createLock(self, password : str):
    #     """
    #     creates for a command

    #     Parameters
    #     ----------
    #     password : str

    #     Returns
    #     -------
    #     bool
    #         DESCRIPTION.

    #     """
    #     if self._checkMasterPassword(password) is not True:
    #         return None
    #     with open(self._configDirectory, 'r+') as file:
    #         try:
    #             fileData : dict = json.loads(file.read())
    #             if "lockedCommands" in fileData.keys():
    #                 fileData["lockedCommands"].append(self._commandName)
    #             else:
    #                 fileData["lockedCommands"] = [self._commandName]
    #             file.write(json.dumps(fileData))
    #         except json.JSONDecodeError:
    #             raise AttributeError("master config file has not been initalized please set a password by using the"\
    #                                  + "changeMasterPassword method")
    # def isLocked(self):
    #     isLockedFlag : bool | None = None
    #     with open(self._configDirectory, 'r') as file:
    #         try:
    #             fileData : dict = json.loads(file.read())
    #             if self._commandName in fileData["lockedCommands"]:
    #                 isLockedFlag = True
    #             else:
    #                 isLockedFlag = False
    #         except json.JSONDecodeError:
    #             isLockedFlag = None
    #     return isLockedFlag
            
            
    
    
    # @staticmethod
    # def _checkMasterPassword(password : str, timeToTake : float = 2.0,):
    #     start : float = time.time()
    #     createDirectory(LockedEventFile._lockedDir)
    #     if createFile(LockedEventFile._configDirectory):
    #         return None
    #     fileData : dict = {}
    #     with open(LockedEventFile._configDirectory, 'r') as file:
    #         fileData = file.read()
    #     try:
    #         fileData = json.loads(fileData)
    #     except json.JSONDecodeError:
    #         return None
    #     hashSalt = fileData["hash"].to_bytes(fileData["size"][0], fileData["endienness"])
    #     timeElapsed : float = time.time() - start
    #     if timeElapsed < timeToTake:
    #         time.sleep(timeToTake-timeElapsed)
    #     waitRandomTime(1)
    #     return checkHashSalt(password,hashSalt, fileData["size"][1])
    # @staticmethod
    # def changeMasterPassword(currentMasterPassword : str, newMasterPassword : str,
    #                          passwordEndienness = "big"):
    #     passwordStatus : bool | None = LockedEventFile._checkMasterPassword(currentMasterPassword)
    #     if passwordStatus is False:
    #         return False
    #     fileData : dict = {}
    #     if passwordStatus == True:
    #         with open(LockedEventFile._configDirectory, 'r') as file:
    #             fileData = file.read()
    #             fileData = json.loads(fileData)
    #     salt = os.urandom(LockedEventFile._saltSize)
    #     hashSalt, saltSize = generateHash(newMasterPassword, salt)
    #     fileData["hash"] = int.from_bytes(hashSalt, passwordEndienness)
    #     fileData["size"] = (len(hashSalt), saltSize)
    #     fileData["endienness"] = passwordEndienness
    #     with open(LockedEventFile._configDirectory, 'w') as file:
    #         file.write(json.dumps(fileData))
    
# def createLock(commandName : str, password, salt : bytes | None = None, endienness = "big"):
#     hashSalt : bytes = None; saltSize : int = None;
#     if salt is None:
#         hashSalt, saltSize = generateHash(password)
#     else:
#         hashSalt, saltSize = generateHash(password, salt)
#     data : dict = {"hash" : int.from_bytes(hashSalt, endienness),
#                    "size" : (len(hashSalt), saltSize),
#                    "endienness" : endienness}
#     createDirectory("lockedFunctions")
#     with open("lockedFunctions" + os.sep + f"__{commandName}__.event", "wt") as file:
#         file.write(json.dumps(data))
#     return None
# def readLock(commandName: str):
#     data : dict = {}
#     with open("lockedFunctions" + os.sep + f"__{commandName}__.event", "rt") as file:
#         data = json.loads(file.read())
#     hashSalt= (data["hash"]).to_bytes(data["size"][0], data["endienness"])
#     hashedText, salt = splitHashSalt(hashSalt, data["size"][1])
#     return hashedText, salt