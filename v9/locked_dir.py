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
                           "hashSize" : 0,
                           "saltSize" : 0,
                           "endienness" : "",
                           "mode" : "o",
                           "allowedFiles" : ""}
    _securityModes = ("r", "s", "ws", "o", "rs")
    def __init__(self, path : str):
        """
        Creates a configuration directory along with a configuration file
        The configuration file is used for soft locking file inside the directory

        Parameters
        ----------
        path : str
            folder path to soft lock
            if folder path does not exist the folder
            and the subsequent configuration file will be created.

        Returns
        -------
        instance

        """
        self._path = os.path.abspath(path)
        createDirectory(self._path)
        self._directoryName = self._path.split(os.sep)[-1]
        self._configFile : str = self._path + os.sep + f"{self._directoryName}_config.ini"
        self._logger : logging.Logger = logging.getLogger(f"LockedDirectory{self._directoryName}")
        self.__createLockFile()
    
    
    def _readConfig(self) -> configparser.ConfigParser | None:
        """
        return a config parser

        Raises
        ------
        TypeError
            if config file cannot be read

        Returns
        -------
        config : configparser.ConfigParser | None
            the parser as a Config parser instance
            None, if config file cannot be parsed

        """
        config : configparser.ConfigParser | None = None
        try:
            config : configparser.ConfigParser = configparser.ConfigParser()
            config.read(self._configFile)
        except configparser.MissingSectionHeaderError:
            self._logger.error("config file could not be parsed")
            raise TypeError("Bad config file")
            return None
        return config
    
    def __createLockFile(self) -> bool:
        """
        A method to create the configuration file
        used during instance creation

        Returns
        -------
        bool
            if the configuration file has been created
        

        """
        if createFile(self._configFile) is True:
            config = configparser.ConfigParser()
            with open(self._configFile, 'w') as file:
                config["main"] = self.__configDict
                config.write(file)
                self._logger.debug("config file has now been created")
                return True
        else:
            self._logger.debug("config file has already been created")
            return False
    
    
    
    def newPassword(self, newPassword : str, oldPassword:str | None = None,
                    encoding = "utf-8", endienness : str = "big") -> bool | None:
        """
        changes password for directory

        Parameters
        ----------
        newPassword : str
            password to change to
        oldPassword : str | None, optional
            original password. Can leave blank if there was no password
            to begin with
        encoding : TYPE, optional
            text encoding of both password parameters. The default is "utf-8".
        endienness : str, optional
            Endienness of the processed password. The default is "big".

        Returns
        -------
        bool | None
            True if the current password has been changed
            False if old password parameter is incorrect and the current password has not changed
            None if the config file cannot be read properly

        """
        oldPassword = "" if oldPassword == None else oldPassword
        passwordFlag : bool | None = self._checkPassword(oldPassword)
        config = self._readConfig()
        if config is None:
            return False
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
        config["main"]["hashSize"] = str(len(hashSalt))
        config["main"]["saltSize"] = str(saltSize)
        config["main"]["endienness"] = endienness
        with open(self._configFile, 'w') as file:
            config.write(file)
        return True
                 
            
    def _checkPassword(self, password : str, encoding : str = "utf-8", 
                       passwordCheckTime : float = 2.0) -> bool | None:
        """
        checks the password parameter against the currennt password in the
        config file

        Parameters
        ----------
        password : str
            password to check against
        encoding : str, optional
            text encoding of the password. The default is "utf-8".
        passwordCheckTime : float, optional
            delays password check to guard against brute force attacks.
            The default is 2.0.

        Returns
        -------
        bool | None
            True if password matches the confug file password
            False if they do not match
            None if config file cannot be parsed through

        """
        startTime : float = time.time()
        passwordFlag : bool | None = None
        config = self._readConfig()
        if config is None:
            return False
        if config["main"]["hashSalt"] == "":
            self._logger.warning("The current directory does not have a password.")
            passwordFlag = None
        else:
            hashSalt = int(config["main"]["hashSalt"])
            hashSalt = hashSalt.to_bytes(int(config["main"]["hashSize"]), config["main"]["endienness"])
            if checkHashSalt(password, hashSalt, int(config["main"]["saltSize"]), encoding):
                passwordFlag = True
            else:
                passwordFlag = False
        if time.time() - startTime < passwordCheckTime:
            time.sleep(time.time() - startTime)
        waitRandomTime(1)
        return passwordFlag
    
    def checkPassword(self, password : str, encoding : str = "utf-8") -> bool | None:
        return self._checkPassword(password, encoding)
        
    
    def dirMode(self, password : str, mode : str, encoding : str = "utf-8") -> bool:
        """
        sets mode for directory
        *this will not extend to subdirectories*

        Parameters
        ----------
        password : str
            current password
        mode : str
            a valid one lowercase character string here are the modes:
                o = open mode
                ws = secure writes, read not secure
                s = secure mode
                r = read only mode
                rs = read only secure
        encoding : str, optional
            text encoding. The default is "utf-8".

        Raises
        ------
        TypeError
            if the mode is invalid

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if not any(mode == validMode for validMode in self._securityModes):
            raise TypeError("the mode parameter must be a valid mode")
            return None
        if self._checkPassword(password, encoding) == True:
            config = self._readConfig()
            config["main"]["mode"] = mode
            return True
        return False
    def setAllowedFileExtention(self, fileExtensions : list, password: str,
                                textEncoding : str = "utf-8"):
        if not all('.' in extension[0] for extension in fileExtensions):
            raise TypeError("Not an exstension")
        if not self._checkPassword(password, textEncoding):
            return False
        config = self._readConfig()
        config["main"]["allowedFiles"] = str.join("|", fileExtensions)
        self._writeToConfig(config)
        return True
    
    def checkFile(self, filenameWithExtenstion:str):
        config = self._readConfig()
        if config is None:
            return None
        if config["main"]["allowedFiles"] == "":
            return True
        extention = filenameWithExtenstion[filenameWithExtenstion.rfind('.'):]
        if extention in config["main"]["allowedFiles"].split("|"):
            return True
        return False
    
    def _writeToConfig(self, config : configparser.ConfigParser | None):
        if config is None:
            return False
        with open(self._configFile, 'w') as file:
            config.write(file)
            return True
        