# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:11:19 2024

@author: Phatty
"""
import os, copy, logging, rsa
from unlocked_file import UnlockedFile
from config_file_maker import ConfigFileMaker
from misc import checkTypeHard, generateHas,
class SecureEvents:
    def __init__(self, password : str, encoding : str = "utf-8"):
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
    
    def checkCommand(self, password : str | None = None,
                     encryptedDeviceSigniture : str | None = None,
                     encoding : str = "utf-8"):
        raise NotImplemented()
    def __checkLevelZeroCommand(self, password, encryptedDeviceSigniture : str | None, encoding : str = "utf-8"):
        raise NotImplemented()
    def getPublicKey(self, levelNumber : int):
        key = self._config["level " + str(levelNumber)]["publicKey"]
        encoding = self._config["level " + str(levelNumber)]["encoding"]
        publicKey : rsa.PublicKey = rsa.PublicKey.load_pkcs1(key.encode(encoding))
        return publicKey
    