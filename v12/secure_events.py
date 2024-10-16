# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:11:19 2024

@author: Phatty
"""
#✓
# To do:  
import os, copy, logging, rsa
from unlocked_file import UnlockedFile
from config_file_maker import ConfigFileMaker
from misc import checkTypeHard, generateHash, checkHashSalt, waitRandomTime
class SecureEvents:
    def __init__(self, password : str | None = None, encoding : str = "utf-8"):
        self._eventDirectory : str = os.path.abspath("events" + os.sep + "events.ini")
        self._file : UnlockedFile = UnlockedFile(self._eventDirectory)
        self._config : ConfigFileMaker() = ConfigFileMaker()
        self._logger : logging.Logger = logging.getLogger("SecureEvents for \"" + self._eventDirectory + "\"")
        self._file.unlock(password, encoding)
        
    def _readConfig(self, password : str | None = None, encoding : str = "utf-8") -> bool:
        data : str | None = self._file.read(password = password, encoding = encoding)
        if data is None:
            return False
        self._config.recieve(data)
        return True
    
    def findLevel(self, commandName : str):
        self._readConfig()
        section : str | None = None
        data : dict | None = None
        for section, data in self._config:
            try:
                assert commandName in data["commands"]
            except TypeError:
                continue
            except AssertionError:
                break
        else:
            return None
        return section
    
    def checkCommand(self, command : str, password : str | None = None,
                     encryptedDeviceSigniture : str | None = None,
                     encoding : str = "utf-8"):
        self._readConfig()
        level : str = self.findLevel(command)
        if level is None:
            return None
        #level 0 checker
        if level == "level 0":
            if password is None:
                return False
            return self.__checkLevelZeroCommand(password, encryptedDeviceSigniture, encoding)
        #othe levels
        return self.__checkLevelCommand(level, command, password, encryptedDeviceSigniture, encoding)
    
    def __checkLevelCommand(self, level : str, password : str | None = None,
                     encryptedDeviceSigniture : str | None = None,
                     encoding : str = "utf-8"):
        
        #if a the signiture of the level is incorrect and there is no password for current level
        #then the function will return false
        #if there is no signiture and there is no password specified the function will look in the lower levels for
        # a password. 
        
        #check this level's signiture
        signitureFlag : bool | None = self.__checkSigniture(level, encryptedDeviceSigniture, encoding)
        if signitureFlag is True:
            return True
        #check this level's password
        passwordFlag : bool | None = self.__checkLevelPassword(level, password, encoding)
        if passwordFlag is not None:
            return passwordFlag
        
        if signitureFlag is False:
            return False
        
        #check for previous levels' password and signitures
        section : str
        for section in self._config.getSections():
            if int(section[6]) > int(level[6]):
                signitureFlag = self.__checkSigniture(section, encryptedDeviceSigniture, encoding)
                if signitureFlag is not None:
                    return signitureFlag
                passwordFlag = self.__checkLevelPassword(section, password, encoding)
                if passwordFlag is not None:
                    return passwordFlag
        return True
    
    def __checkSigniture(self, level : str, encryptedDeviceSigniture : str | None = None, encoding : str = "utf-8"):
        if encryptedDeviceSigniture is not None and self._config[level]["trustedDevices"] is not None:
            deviceSigniture : str | None = None
            key : str = self._config[level]["privateKey"]
            keyEncoding : str = self._config[level]["encoding"]
            privateKey : rsa.PrivateKey =rsa.PrivateKey.load_pkcs1(key.encode(keyEncoding))
            deviceSigniture = rsa.decrypt(encryptedDeviceSigniture.encode("utf-8"), privateKey).decode(encoding)
            if deviceSigniture in self._config[level]["trustedDevices"]:
                return True
            return False
        return None
    
    def __checkLevelPassword(self, level : str, password : str | None = None, encoding : str = "utf-8"):
        if self._config[level]["password"] is not None:
            if password is None:
                return False
            byteSize : int = self._config[level]["byteSize"]
            endienness : str = self._config[level]["endienness"]
            hashSalt : bytes = self._config[level]["password"].to_bytes(byteSize, byteorder = endienness)
            passwordsMatch : bool = checkHashSalt(password, hashSalt, self._config[level]["saltSize"], encoding)
            return passwordsMatch
        return None
            
    def __checkLevelZeroCommand(self, password, encryptedDeviceSigniture : str | None, encoding : str = "utf-8"):
        raise NotImplemented()
    def getPublicKey(self, levelNumber : int):
        self._readConfig()
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            self._logger.error("levelNumber must be an int > 0")
            return None
        if self._config["level " + str(levelNumber)]["publicKey"] is None :
            return None
        key = self._config["level " + str(levelNumber)]["publicKey"]
        encoding = self._config["level " + str(levelNumber)]["encoding"]
        publicKey : rsa.PublicKey = rsa.PublicKey.load_pkcs1(key.encode(encoding))
        return publicKey
    