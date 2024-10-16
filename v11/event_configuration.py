# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 17:40:46 2024

@author: Phatty
"""
import os, copy, logging, rsa
from unlocked_file import UnlockedFile
from config_file_maker import ConfigFileMaker
from misc import checkTypeHard, generateHash, getRandomString
class EventConfiguration:
    #level 0 will require a password and a device signiture, 
    #if no password for level 0 exists, then level 0 cannot be accessed
    _eventFileDict : dict = {"commands": None,
                             "trustedDevices" : None, #device signiture
                             "publicKey" : None,
                             "privateKey" : None,
                             "password" : None,
                             "saltSize" : None,
                             "endienness" : None,
                             "encoding" : "utf-8"}
    
    def __init__(self, password : str | None = None, encoding : str = "utf-8"):
        """
        creates and modifies a configuration file for commands used with the
        MyMessage class. These events will be vetted and locked 

        Parameters
        ----------
        password : str | None, optional
            password for accessing the locked file in the directory. The default is None.
        encoding : str, optional
            The encoding of the password. The default is "utf-8".

        """
        self._eventDirectory : str = os.path.abspath("events" + os.sep + "events.ini")
        self._file : UnlockedFile = UnlockedFile(self._eventDirectory)
        self._config : ConfigFileMaker() = ConfigFileMaker()
        self._logger : logging.Logger = logging.getLogger("EventConfiguration for \"" + self._eventDirectory + "\"")
        if password is not None:
            self._file.newPassword(password, encoding)
        self.__generateFile(password, encoding)
        self._file.unlock(password, encoding)
    
    #all the private member functions should ust
    def __generateFile(self, password : str | None = None, encoding : str = "utf-8"):
        """
        creates the directory for the config file along with the file itself

        Parameters
        ----------
        password : str | None, optional
            password for accessing the locked file in the directory. The default is None.
        encoding : str, optional
            The encoding of the password. The default is "utf-8".

        Returns
        -------
        bool
            True if file has been created successfully
            False if file has already been created

        """
        if self._file.justCreated():
            self._config.addSection("level 0")
            self._config["level 0"] = self._eventFileDict
            self._writeConfig(password, encoding)
            return True
        return False
    
    def _readConfig(self, password : str | None = None, encoding : str = "utf-8") -> bool:
        """
        reads the config file and loads the data in the instance

        Parameters
        ----------
        password : str | None, optional
            password for accessing the locked file in the directory. The default is None.
        encoding : str, optional
            The encoding of the password. The default is "utf-8".

        Returns
        -------
        bool
            True if data has been read successfully
            otherwise, False

        """
        data : str | None = self._file.read(password = password, encoding = encoding)
        if data is None:
            return False
        self._config.recieve(data)
        return True
    
    def _writeConfig(self, password : str | None = None, encoding : str = "utf-8") -> bool:
        """
        writes 

        Parameters
        ----------
        password : str | None, optional
            DESCRIPTION. The default is None.
        encoding : str, optional
            DESCRIPTION. The default is "utf-8".

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if self._file.write(self._config.send(), False, password, encoding):
            return True
        return False
    
    def addLevel(self, levelNumber : int):
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            raise TypeError("")
            return False
        self._readConfig()
        if "level " + str(levelNumber) in self._config.getSections():
            return False
        self._config.addSection("level " + str(levelNumber))
        self._config.addData("level " + str(levelNumber), self._eventFileDict)
        return self._writeConfig()
    def addCommand(self, levelNumber : int, commandName : str):
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            return False
        self._readConfig()
        if "level " + str(levelNumber) not in self._config.getSections():
            print("level does not exist")
            return False
        section : str; data : dict
        for section, data in self._config:
            try:
                assert not commandName in data["commands"]
            except TypeError:
                continue
            except AssertionError:
                return False
            
        if self._config["level " + str(levelNumber)]["commands"] is None:
            self._config["level " + str(levelNumber)]["commands"] = [commandName]
            self._writeConfig()
            return True
        self._config["level " + str(levelNumber)]["commands"].append(commandName)
        self._writeConfig()
        return True
            
            
    def addPassword(self, levelNumber : int, newPassword : str, encoding : str = "utf-8", endianness = "big"):
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            return False
        self._readConfig()
        if "level " + str(levelNumber) not in self._config.getSections():
            return False
        if self._config["level " + str(levelNumber)]["password"] is not None:
            return None
        passwordAsHash : int | bytes
        passwordAsHash, saltSize = generateHash(newPassword)
        passwordAsHash = int.from_bytes(passwordAsHash,byteorder=endianness) 
        self._config["level " + str(levelNumber)]["password"] = passwordAsHash
        self._config["level " + str(levelNumber)]["saltSize"] = saltSize
        self._config["level " + str(levelNumber)]["endienness"] = endianness
        self._writeConfig()
        return True
    
    def _generateKeys(self, levelNumber : int, bitSize : int = 512) -> bool | None:
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            return None
        self._readConfig()
        if self._config["level " + str(levelNumber)]["publicKey"] is not None and \
        self._config["level " + str(levelNumber)]["privateKey"] is not None:
            return False
        publicKey : rsa.PublicKey; privateKey : rsa.PrivateKey
        publicKey, privateKey = rsa.newkeys(512)
        encoding : str = self._config["level " + str(levelNumber)]["encoding"]
        self._config["level " + str(levelNumber)]["publicKey"] = publicKey.save_pkcs1("PEM").decode(encoding)
        self._config["level " + str(levelNumber)]["privateKey"] = privateKey.save_pkcs1("PEM").decode(encoding)
        self._writeConfig()
    
    def getPublicKey(self, levelNumber : int) -> rsa.PublicKey | None:
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            return None
        self._readConfig()
        self._generateKeys(levelNumber)
        key = self._config["level " + str(levelNumber)]["publicKey"]
        encoding = self._config["level " + str(levelNumber)]["encoding"]
        publicKey : rsa.PublicKey = rsa.PublicKey.load_pkcs1(key.encode(encoding))
        return publicKey
    
    def addTrustedDevice(self, levelNumber : int, deviceName : str):
        self._readConfig()
        if not checkTypeHard(levelNumber, int) or levelNumber < 0:
            return None
        if self._config["level " + str(levelNumber)]["trustedDevices"] is None:
            signitureAddon : str = getRandomString(8)
            self._config["level " + str(levelNumber)]["trustedDevices"] = [deviceName + signitureAddon]
            self._writeConfig()
            return True
        
        deviceInLevel : bool
        deviceInLevel = any(deviceName in deviceSigniture \
                        for deviceSigniture in self._config["level " + str(levelNumber)]["trustedDevices"])
        if deviceInLevel is True:
            return False
        self._config["level " + str(levelNumber)]["trustedDevices"].append(deviceName + signitureAddon)
        self._writeConfig()
        return True
        
        