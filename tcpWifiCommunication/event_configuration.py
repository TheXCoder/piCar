# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 17:40:46 2024

@author: Phatty
"""
#✓
# To do:  add docstring and comments
# To do:  add more logging points
import os, copy, logging, rsa
from unlocked_file import UnlockedFile
from config_file_maker import ConfigFileMaker
from misc import checkTypeHard, generateHash, getRandomString
class EventConfiguration:
    #level 0 will require a password and a device signiture, 
    #if no password for level 0 exists, then level 0 cannot be accessed
    _eventFileDict : dict = {"commands": None,
                             "trustedDevices" : None, #device signiture
                             "password" : None,
                             "byteSize" : None,
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
        self._eventDirectory : str = os.path.abspath("events" + os.sep + "events.ini") #gets the absolute path for the config file
        self._file : UnlockedFile = UnlockedFile(self._eventDirectory) #Uses the Unlocked class to access the config file
        self._config : ConfigFileMaker() = ConfigFileMaker() # the interface for the config file
        self._logger : logging.Logger = logging.getLogger("EventConfiguration for \"" + self._eventDirectory + "\"") #the logger
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
            self._logger.debug("the event config file has been created successfully")
            return True
        self._logger.debug("the event config file has already been created or the password is incorrect")
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
            self._logger.warning("There is no data stored in the config file. This will be detrimental later. ;)")
            return False
        self._logger.debug("data has successfully been loaded into the instance")
        self._config.recieve(data)
        return True
    
    def _writeConfig(self, password : str | None = None, encoding : str = "utf-8") -> bool:
        """
        writes data stored to the config file

        Parameters
        ----------
        password : str | None, optional
            password for accessing the locked file in the directory. The default is None.
        encoding : str, optional
            The encoding of the password. The default is "utf-8".

        Returns
        -------
        bool
            True if data has been written successfully
            otherwise, False

        """
        if self._file.write(self._config.send(), False, password, encoding):
            self._logger.debug("data has successfully been wrote onto the config file")
            return True
        self._logger.warning("cannot write the data to the config file.")
        return False
    
    def addLevel(self, levelNumber : int) -> bool:
        """
        adds security level to the config file

        Parameters
        ----------
        levelNumber : int
            the level number. Must be an integerValue that is greater then 0

        Raises
        ------
        TypeError
            If the levelNumber parameter is not a int > 0

        Returns
        -------
        bool
            True if the level has been added
            otherwise, False

        """
        if checkTypeHard(levelNumber, int) is False or levelNumber < 1:
            self._logger.error("level number must be a int > 0")
            raise TypeError("level number must be a int > 0")
            return False
        self._readConfig()
        if "level " + str(levelNumber) in self._config.getSections():
            self._logger.debug("level already exist in the config file")
            return False
        self._logger.debug("adding the level the config file...")
        self._config.addSection("level " + str(levelNumber))
        self._config.addData("level " + str(levelNumber), self._eventFileDict)
        return self._writeConfig()
    def addCommand(self, levelNumber : int, commandName : str) -> bool:
        """
        adds a command to the security level

        Parameters
        ----------
        levelNumber : int
            the level number. Must be an integerValue that is equal to or greater then 0.
        commandName : str
            name of the command.

        Raises
        ------
        TypeError
            levelNumber is not an int >= 0

        Returns
        -------
        bool
            True if command is not added to the config file
            otherwise, False

        """
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            self._logger.error("levelNumber must be an int > 0")
            raise TypeError()
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
                self._logger.debug("command name is already in a level of security")
                return False
            
        if self._config["level " + str(levelNumber)]["commands"] is None:
            self._config["level " + str(levelNumber)]["commands"] = [commandName]
            self._logger.debug("There are no commands in this level, adding the command...")
            return self._writeConfig()
        self._config["level " + str(levelNumber)]["commands"].append(commandName)
        self._logger.debug("Adding command to this level...")
        return self._writeConfig()
            
            
    def addPassword(self, levelNumber : int, newPassword : str, encoding : str = "utf-8", endianness = "big")-> bool:
        """
        

        Parameters
        ----------
        levelNumber : int
            DESCRIPTION.
        newPassword : str
            DESCRIPTION.
        encoding : str, optional
            DESCRIPTION. The default is "utf-8".
        endianness : TYPE, optional
            DESCRIPTION. The default is "big".

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            return False
        self._readConfig()
        if "level " + str(levelNumber) not in self._config.getSections():
            return False
        if self._config["level " + str(levelNumber)]["password"] is not None:
            return None
        passwordAsHash : int | bytes
        passwordAsHash, saltSize = generateHash(newPassword)
        byteSize : int = len(passwordAsHash)
        passwordAsHash = int.from_bytes(passwordAsHash,byteorder=endianness) 
        self._config["level " + str(levelNumber)]["password"] = passwordAsHash
        self._config["level " + str(levelNumber)]["byteSize"] = byteSize
        self._config["level " + str(levelNumber)]["saltSize"] = saltSize
        self._config["level " + str(levelNumber)]["endienness"] = endianness
        return self._writeConfig()
    
    def addTrustedDevice(self, levelNumber : int, deviceName : str) -> bool | tuple | None:
        self._readConfig()
        if checkTypeHard(levelNumber, int) is False or levelNumber < 0:
            raise TypeError()
            return None
        if "level " + str(levelNumber) not in self._config.getSections():
            raise KeyError()
            return None
        deviceSigniture = deviceName if len(deviceName) < 64 else deviceName[:64]
        deviceSigniture : str = deviceSigniture + getRandomString(64)
        encoding : str = self._config["level " + str(levelNumber)]["encoding"]
        if self._config["level " + str(levelNumber)]["trustedDevices"] is None:
            publicKey : rsa.PublicKey; privateKey : rsa.PrivateKey
            publicKey, privateKey = rsa.newkeys(2084)
            trustedDevice : dict = {"signiture" : deviceSigniture,
                                    "publicKey" : publicKey.save_pkcs1("PEM").decode(encoding),
                                    "privateKey" : privateKey.save_pkcs1("PEM").decode(encoding)}
            self._config["level " + str(levelNumber)]["trustedDevices"] = {deviceName : trustedDevice}
            self._writeConfig()
            return publicKey, deviceSigniture
        if deviceName in self._config["level " + str(levelNumber)]["trustedDevices"].keys() :
            return False
        publicKey : rsa.PublicKey; privateKey : rsa.PrivateKey
        publicKey, privateKey = rsa.newkeys(2084)
        trustedDevice : dict = {"signiture" : deviceSigniture,
                                "publicKey" : publicKey.save_pkcs1("PEM").decode(encoding),
                                "privateKey" : privateKey.save_pkcs1("PEM").decode(encoding)}
        self._config["level " + str(levelNumber)]["trustedDevices"].update({deviceName : trustedDevice})
        self._writeConfig()
        return publicKey, deviceSigniture

        
        