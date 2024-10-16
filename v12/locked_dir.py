# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 20:24:59 2024

@author: Phatty
"""
#✓
# To do:  
import os, logging, time, io
from misc import createDirectory, createFile, checkHashSalt, waitRandomTime, generateHash
from config_file_maker import ConfigFileMaker

def checkConfigPassword(config : ConfigFileMaker, password : str, encoding : str = "utf-8", 
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
    if config["main"]["hashSalt"] == None:
        passwordFlag = None
    else:
        hashSalt = config["main"]["hashSalt"]
        hashSalt = hashSalt.to_bytes(config["main"]["hashSize"], config["main"]["endienness"])
        if checkHashSalt(password, hashSalt, config["main"]["saltSize"], encoding):
            passwordFlag = True
        else:
            passwordFlag = False
    if time.time() - startTime < passwordCheckTime:
        time.sleep(time.time() - startTime)
    waitRandomTime(1)
    return passwordFlag
    

class LockedDir:
    """
    Discription
    -----------
    Creates a configuration directory along with a configuration file
    The configuration file is used for soft locking file inside the directory
    mode
    ----
        read/write mode for entire directory
        a valid one lowercase character string here are the modes:
            \to = open mode
            \tws = secure writes, read not secure
            \ts = secure mode
            \tr = read only mode
            \trs = read only secure
    FileType filtering
    ------------------
    file types can be explicitly black and white listed
    If both the blacklist and whitelist have file extentions in them
    then files not list in either the black or white list will require a password
    (they are grey-listed)
    """
    _saltSize : int = 64
    __configDict : dict = {"hashSalt" : None,
                           "hashSize" : 0,
                           "saltSize" : 0,
                           "endienness" : None,
                           "mode" : "o",
                           "whiteListedFiles" : None,
                           "blackListedFiles" : None
                           }
    _securityModes = ("r", "s", "ws", "o", "rs")
    def __init__(self, path : str, password : str | None = None, encoding : str = "utf-8"):
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
        self._path : str = os.path.abspath(path)
        self._directoryName : str = None
        self._configFileDir : str = None
        self._logger : logging.Logger = None
        self._config : ConfigFileMaker = None
        
        if self.__createDirectory(path, password, encoding) is False:
            raise PermissionError("You do not have permission to create a directory in this location")
        else:
            createDirectory(self._path)
            self._directoryName = self._path.split(os.sep)[-1]
            self._configFileDir = self._path + os.sep + f"{self._directoryName}_config.ini"
            self._logger = logging.getLogger(f"LockedDirectory{self._directoryName}")
            self._config = ConfigFileMaker()
            self.__createMasterLockFile()
        
    def __createDirectory(self, path, password : str | None = None, encoding : str = "utf-8"):
        #checks to see if parent directory has a lock on it
        _ = os.path.abspath(path).split(os.sep)[:-1]
        previousPath : str = os.sep.join(_)
        previousDirectoryName = previousPath.split(os.sep)[-1]
        return self.__checkParentDirectory(previousDirectoryName, password, encoding)
        
    
    def __checkParentDirectory(self, parentPath, password : str | None = None, encoding : str = "utf-8"):
        parentConfigFile : str = parentPath + os.sep + f"{parentPath}_config.ini"
        if not os.path.exists(parentConfigFile):
            return True
        config : ConfigFileMaker = ConfigFileMaker()
        file : io.TextIOWrapper
        with open(parentConfigFile, 'r') as file:
            config.read(file)
        passwordFlag = checkConfigPassword(config, "" if password is None else password, encoding)
        if config["main"]["mode"] in ("r", "rs"):
            return False
        elif config["main"]["mode"] in ("ws", "s") and passwordFlag is not True:
            return False
        return True
        
            
            
    def __createMasterLockFile(self) -> bool:
        """
        A method to create the configuration file
        used during instance creation

        Returns
        -------
        bool
            if the configuration file has been created
        

        """
        if createFile(self._configFileDir):
            with open(self._configFileDir, "w") as file:
                self._config.addSection("main")
                self._config.addData("main", self.__configDict)
                self._config.write(file)
            return True
        return False
    
    def __len__(self) -> int:
        return len(self._config) - 1 if len(self._config) > 0 else 0
            
    
    def _readConfig(self) -> bool:
        file : io.TextIOWrapper
        with open(self._configFileDir, 'r') as file:
            self._config.read(file)
        return True
            
    
    def _checkPassword(self, password : str, encoding : str = "utf-8", 
                       passwordCheckTime : float = 3.0) -> bool | None:
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
        self._readConfig()
        if self._config["main"]["hashSalt"] == None:
            self._logger.warning("The current directory does not have a password.")
            passwordFlag = None
        else:
            hashSalt = self._config["main"]["hashSalt"]
            hashSalt = hashSalt.to_bytes(self._config["main"]["hashSize"], self._config["main"]["endienness"])
            if checkHashSalt(password, hashSalt, self._config["main"]["saltSize"], encoding):
                passwordFlag = True
            else:
                passwordFlag = False
        if time.time() - startTime < passwordCheckTime:
            time.sleep(time.time() - startTime)
        waitRandomTime(0.5)
        return passwordFlag
    def checkPassword(self, password : str, encoding : str = "utf-8") -> bool:
        return self._checkPassword(password, encoding)
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
        self._readConfig()
        if passwordFlag is False:
            self._logger.debug("old password is incorrect. The current password will not be changed")
            return False
        if passwordFlag is None:
            self._logger.debug("there was no password to begin with, setting new password...")
        else:
            self._logger.debug("the old password was current password, changing to new password...")
        salt = os.urandom(self._saltSize)
        hashSalt, saltSize = generateHash(newPassword, salt, encoding)
        self._config["main"]["hashSalt"] = int.from_bytes(hashSalt, endienness)
        self._config["main"]["hashSize"] = len(hashSalt)
        self._config["main"]["saltSize"] = saltSize
        self._config["main"]["endienness"] = endienness
        file : io.TextIOWrapper
        with open(self._configFileDir, 'w') as file:
            self._config.write(file)
        return True
    
    def dirMode(self, mode : str, password : str, encoding : str = "utf-8") -> bool:
        """
        sets mode for directory
        *this will not extend to subdirectories*

        Parameters
        ----------
        mode : str
            read/write mode for entire directory
            a valid one lowercase character string here are the modes:
                o = open mode
                ws = secure writes, read not secure
                s = secure mode
                r = read only mode
                rs = read only secure
        password : str
            current password
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
            self._readConfig()
            self._config["main"]["mode"] = mode
            file : io.TextIOWrapper
            with open(self._configFileDir, 'w') as file:
                self._config.write(file)
            return True
        return False
    
    def _getFolderMode(self) -> str:
        """
        checkes folder read write permissions

        Returns
        -------
        str
            gives mode as a set of charactors see doc string

        """
        self._readConfig()
        return self._config["main"]["mode"]
    
    def getFolderMode(self) -> str:
        """
        checkes folder read write permissions

        Returns
        -------
        str
            gives mode as a set of charactors see doc string

        """
        return self._getFolderMode()
    
    
    def whiteList(self, fileExtension : str, password : str,
                          encoding : str = "utf-8" ,removeFromList : bool = False):
        self._readConfig()
        #checks password
        if self._checkPassword(password, encoding) is not True:
            return False
        #checks to see file extention is in the white list
        if self._config["main"]["blackListedFiles"] is not None:
            if fileExtension in self._config["main"]["blackListedFiles"]:
                message : str = "The extention {fileExtension} can already be found in the black list."
                message = message.format(fileExtension = fileExtension) + \
                    "Please remove it before adding it to the white list"
                self._logger.error(message)
                return False
        #checks to see if whitelisted file has been initalized
        if self._config["main"]["whiteListedFiles"] is None:
            self._config["main"]["whiteListedFiles"] = []
        #checks to see if extension is in the white list
        if fileExtension in self._config["main"]["whiteListedFiles"] and removeFromList:
            self._config["main"]["whiteListedFiles"].remove(fileExtension)
        #checks to see if trying to remove from list (usuing context from previous if statements)
        if removeFromList is True:
            message : str = "The extention {fileExtension} cannot be found in the white list."
            message = message.format(fileExtension = fileExtension)
            self._logger.error(message)
            return False
        if fileExtension in self._config["main"]["whiteListedFiles"]:
            return False
        if fileExtension[0] != '.':
            raise TypeError("this is not an extension")
            return False
        self._config["main"]["whiteListedFiles"].append(fileExtension)
        file : io.TextIOWrapper
        with open(self._configFileDir, "w") as file:
            self._config.write(file)
        return True
    
    def blackList(self, fileExtension : str, password : str,
                          encoding : str = "utf-8", removeFromList : bool = False):
        self._readConfig()
        #checks password
        if self._checkPassword(password, encoding) is not True:
            return False
        #checks to see file extention is in the white list
        if self._config["main"]["whiteListedFiles"] is not None:
            if fileExtension in self._config["main"]["whiteListedFiles"]:
                message : str = "The extention {fileExtension} can already be found in the white list."
                message = message.format(fileExtension = fileExtension) + \
                    "Please remove it before adding it to the black list"
                self._logger.error(message)
                return False
        #checks to see if blacklisted file has been initalized
        if self._config["main"]["blackListedFiles"] is None:
            self._config["main"]["blackListedFiles"] = []
        #checks to see if extension is in the black list
        if fileExtension in self._config["main"]["blackListedFiles"] and removeFromList:
            self._config["main"]["blackListedFiles"].remove(fileExtension)
        #checks to see if trying to remove from list (usuing context from previous if statements)
        if removeFromList is True:
            message : str = "The extention {fileExtension} cannot be found in the white list."
            message = message.format(fileExtension = fileExtension)
            self._logger.error(message)
            return False
        if fileExtension in self._config["main"]["blackListedFiles"]:
            return False
        if fileExtension[0] != '.':
            raise TypeError("this is not an extension")
            return False
        self._config["main"]["blackListedFiles"].append(fileExtension)
        file : io.TextIOWrapper
        with open(self._configFileDir, "w") as file:
            self._config.write(file)
        return True
        
        
        
    
    
    
        