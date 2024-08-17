# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 11:35:08 2024

@author: Phatty
"""
from misc import generateHash, createDirectory, createFile, checkHashSalt, waitRandomTime
import os, configparser, logging, time
class LockedDir:
    _saltSize : int = 64
    __configDict : dict = {"hashSalt" : "",
                           "size" : 0,
                           "endienness" : ""}
    def __init__(self, path : str):
        createDirectory(path)
        self._directoryName = path.split(os.sep)[-1]
        self._path = path
        self._configFile : str = self._path + os.sep + f"{self._directoryName}_config.ini"
        self._logger : logging.Logger = logging.getLogger(f"LockedDirectory{self._directoryName}")
        self.__createLockFile()
    
    def __createLockFile(self):
        if createFile(self._configFile) is True:
            with open(self._configFile, 'w') as file:
                config = configparser.ConfigParser()
                config["main"] = self.__configDict
                config.write(file)
                self._logger.debug("config file has now been created")
                return True
        else:
            self._logger.debug("config file has already been created")
            return False
    
    def newPassword(self, newPassword : str, oldPassword:str | None = None,
                    encoding = "utf-8", endienness : str = "big"):
        
        config = configparser.ConfigParser()
        config.read(self._configFile)
        passwordFlag : bool | None = self._checkPassword(newPassword)
        if passwordFlag is False:
            self._logger.debug("old password is incorrect. The current password will not be changed")
            return False
        if passwordFlag is None:
            self._logger.debug("there was no password to begin with, setting new password...")
        else:
            self._logger.debug("the old password was current password, changing to new password...")
        salt = os.urandom(self._saltSize)
        hashSalt, saltSize = generateHash(newPassword, salt, encoding)
        config["main"]["hashSalt"] = str(int.from_bytes(hashSalt, endienness))
        config["main"]["size"] = str((len(hashSalt), saltSize))
        config["main"]["endienness"] = endienness
        with open(self._configFile, 'w') as file:
            config.write(file)
        return True
                 
            
    def _checkPassword(self, password : str, encoding : str = "utf-8", 
                       passwordCheckTime : float = 2.0):
        startTime : float = time.time()
        config = configparser.ConfigParser()
        config.read(self._configFile)
        passwordFlag : bool | None = None
        if config["main"]["hashSalt"] == "":
            passwordFlag = None
        elif checkHashSalt(password, config["main"]["hashSalt"], 
                      config["main"]["saltSize"], encoding):
            
            passwordFlag = True
        else:
            passwordFlag = False
        if time.time() - startTime < passwordCheckTime:
            time.sleep(time.time() - startTime)
        waitRandomTime(1)
        return passwordFlag
        
        
    
        