# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 13:37:40 2024

@author: Phatty
"""
#To do: fix password checking
#To do: add comments and docstrings
#To do: add file encryption (pressumbly using the directory password)
#To do: add time stamp data into the master config file with file time created and last edited
#To do: add file timesamp data into the file hash checker
import os, configparser, time, logging
from locked_dir import LockedDir
from misc import createFile, checkHashSalt, waitRandomTime, generateHash
class LockedFile(LockedDir):
    """
    A file manager for soft locked directories
    """
    __configFileDict : dict = {"mode" : "",
                               "encrypted" : "False",
                               #"timeCreated" : "", #add them here
                               #"lastEdited" : "",
                               "fileSigniture" : ""
                               }
    __doc__ += "\n\n" + LockedDir.__doc__
    def __init__(self, file : str, password : str | None = None,
                 textEncoding : str = "utf-8"):
        """
        Create or modify a soft locked file

        Parameters
        ----------
        file : str
            name of file and/or path of file
        password : str | None, optional
            Password is used for creating a file in a soft locked directory.
            The default is None.
        textEncoding : str, optional
            The encoding of the password. The default is "utf-8".

        Returns
        -------
        None.

        """
        self._filePath = os.path.abspath(file) #the path of the file
        self._folder : str = str.join(os.sep, self._filePath.split(os.sep)[0:-1:]) # the directory of the file
        self._filename = self._filePath.split(os.sep)[-1] #the name of the file
        self._file = None
        self._isUnlocked = False #force unlock file so no password is needed to modify this file
        self._justCreated : bool = False #true if the file was created upon creation of instance
        self._cursor : int = 0 #the read cursor for the file
        super(LockedFile,self).__init__(self._folder) #LockedDir initializer
        self._logger = logging.getLogger("File: " +self._filePath)
        if self.__createFile(password, textEncoding) != True:
            self._filename = None
        self.checkFileHash()
            
    def __del__(self):
        """
        Deconstructor for the class

        Returns
        -------
        None.

        """
        config : configparser.ConfigParser = self._readConfig()
        with open(self._configFile, "w") as configFile, open(self._filePath, "rb") as file:
            hashedValue = hash(file.read())
            config[self._filename]["fileSigniture"] = str(hashedValue)
            config.write(configFile)
#--------------constructor helper--------------------------------------------
    
    def __createFile(self, password : str | None = None, textEncoding : str = "utf-8") -> configparser.ConfigParser | None:
        """
        creates a file (if none exists) upon construction of the object

        Parameters
        ----------
        password : str | None, optional
            password to create a file in a soft locked directory. The default is None.
        textEncoding : str, optional
            The encoding of the inputed text. The default is "utf-8".

        Raises
        ------
        PermissionError
            If directory is in read-only mode

        Returns
        -------
        configparser.ConfigParser | None
            A config parser object with the master

        """
        if not self.checkFile(self._filename):
            raise PermissionError("file with that extention cannot be stored in this directory")
            return False
        if os.path.exists(self._filePath):
            return True
        password = "" if password is None else password
        passwordGood = self._checkPassword(password)
        match self._checkFolderMode:
            case "rs":
                raise PermissionError("directory is in secure read-only mode")
                return False
            case 'r':
                raise PermissionError("directory is in read-only mode")
                return False
            case 's':
                if passwordGood == False:
                    return False
            case 'ws':
                if passwordGood == False:
                    return False
        if createFile(self._filePath):
            config : configparser.ConfigParser = self._readConfig()
            config[self._filename] = self.__configFileDict
            self._justCreated = True
            return self._writeToConfig(config)

#-------------check function----------------------------------------------
    def checkFileHash(self):
        """
        checks file hash to see if it matches the stored file hash
        Used to check if file has been modified out side of this manager

        Returns
        -------
        bool
            True if current and stored hashes matches hash stored
            False if current and stored hashes do not match

        """
        if self._justCreated:
            self._logger.debug("recently created files do not have hashes")
            return None
        config : configparser.ConfigParser = self._readConfig()
        fileSame : bool = None
        with open(self._filePath, "rb") as file:
            fileSame = config[self._filename]["fileSigniture"] == str(hash(file.read()))
        if not fileSame:
            self._logger.warning("File has been modified without use of this class")
            return False
        return True
   
    
#------------------------------

    
    #not used may delete    
    def __openSpecial(self, mode, password : str | None = None, textEncoding : str = "utf-8"):
        config = self._readConfig()
        password = "" if password is None else password
        if mode in ("r", "rb", "rt"):
            ...
        if mode in ("r+", "rb+", "rt+", "w+", "wb+", "wt+", "a+", "ab+", "at+"):
            ...
        if mode in ("w", "wb", "wt", "a", "ab", "at"):
            ...
    
    def read(self, amount : int | None = None, isBinary : bool = False,
             password : str | None = None, textEncoding : str ="utf-8") -> str | bytes | None:
        """
        read a file

        Parameters
        ----------
        amount : int | None, optional
            Amount of data read from the file
            The amount read from the file is kept tracked
        isBinary : bool, optional
            is this purely a data file? The default is False.
        password : str | None, optional
            Password  for the directory. The default is None.
            *some directories do not have passwords*
        textEncoding : str, optional
            the encoding of the password. The default is "utf-8".

        Raises
        ------
        PermissionError
            If password does not match current directory password

        Returns
        -------
        data : str | bytes
            thhe data read, this is stored in the file
        None
            If file cannot be read
            

        """
        password = "" if password is None else password
        config = self._readConfig()
        passwordGood : bool = self._checkPassword(password, textEncoding)
        if config is None:
            return None
        if config["main"]["mode"] in ("rs", "s") and not passwordGood:
            raise PermissionError("directory is in a secure read-only mode")
            return None
        if config[self._filename]["mode"] in ("rs", "s") and not passwordGood:
            raise PermissionError("file is in a secure read-only mode")
            return None
        data : str | None | bytes = None
        readMode = "r" + "b"*isBinary
        if amount is None:
            with open(self._filePath, readMode) as file:
                file.seek(self._cursor)
                data = file.read()
                self._cursor = 0
        if isinstance(amount, int) and amount > 0:
            with open(self._filePath, readMode) as file:
                file.seek(self._cursor)
                data = file.read(amount)
                self._cursor += amount
        return data
    
    def write(self, data : str | bytes, isBinary : bool = False,
              password : str | None = None, textEncoding : str ="utf-8"):
        """
        Write data to file
        

        Parameters
        ----------
        data : str | bytes
            data to write to the file
        isBinary : bool, optional
            is this purely a data file? The default is False.
        password : str | None, optional
            Password  for the directory. The default is None.
            *some directories do not have passwords*
        textEncoding : str, optional
            the encoding of the password. The default is "utf-8".

        Raises
        ------
        PermissionError
            If password does not match current directory password.

        Returns
        -------
        bool
            True if the data has been written to the file.
            False if the data has not been written to the file

        """
        password = "" if password is None else password
        config = self._readConfig()
        if config is None:
            return None
        passwordGood : bool = self._checkPassword(password, textEncoding)
        if config["main"]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if config["main"]["mode"] in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure mode")
            return None
        if config[self._filename]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if config[self._filename]["mode"] in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure mode")
            return None
        writeMode = "w" + "b" * isBinary
        with open(self._filePath, writeMode) as file:
            file.write(data)
        return True
    
    def append(self, data : str | bytes, isBinary : bool = False,
              password : str | None = None, textEncoding : str ="utf-8"):
        """
        Add data to the end of the file

        Parameters
        ----------
        data : str | bytes
            data to write to the file
        isBinary : bool, optional
            is this purely a data file? The default is False.
        password : str | None, optional
            Password  for the directory. The default is None.
            *some directories do not have passwords*
        textEncoding : str, optional
            the encoding of the password. The default is "utf-8".

        Raises
        ------
        PermissionError
            If password does not match current directory password.

        Returns
        -------
        bool
            True if the data has been written to the file.
            False if the data has not been written to the file

        """
        password = "" if password is None else password
        config = self._readConfig()
        if config is None:
            return None
        if config["main"]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if config["main"]["mode"] in ("ws", "s") and not self._checkPassword(password, textEncoding):
            raise PermissionError("file is in a secure mode")
            return None
        if config[self._filename]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if config[self._filename]["mode"] in ("ws", "s") and not self._checkPassword(password, textEncoding):
            raise PermissionError("file is in a secure mode")
            return None
        writeMode = "a" + "b" * isBinary
        with open(self._filePath, writeMode) as file:
            file.write(data)
        return True
                
    
    def fileMode(self, mode : str, password : str | None = None, textEncoding : str = "utf-8"):
        """
        set the read/write permissions of the file

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
        password : str | None, optional
            DESCRIPTION. The default is None.
        textEncoding : str, optional
            DESCRIPTION. The default is "utf-8".

        Raises
        ------
        PermissionError
            If password is incorrect
            If no password exist in directory
            If directory mode is more restrictive then specified mode
        TypeError
            If mode specified is not a valid mode

        Returns
        -------
        bool
            True If read/write permisions have beem changed
            otherwise False

        """
        password = "" if password is None else password
        match self._checkFolderMode:
            case "rs":
                raise PermissionError("directory is in secure read-only mode")
                return False
            case 'r':
                if mode not in ("rs", 'r'):
                    raise PermissionError("directory is in read-only mode")
                    return False
            case 's':
                if mode not in ("rs"):
                    raise PermissionError("directory is in secure mode")
                    return False
                    
            case 'ws':
                if mode not in ("rs", 's', 'r'):
                    raise PermissionError("directory is in write secure mode")
                    return False
        if not any(mode == validMode for validMode in self._securityModes):
            raise TypeError("the mode parameter must be a valid mode")
            return None
        if self._checkPassword(password, textEncoding) is True:
            config : configparser.ConfigParser = self._readConfig()
            config[self._filename]["mode"] = mode
            with open(self._configFile, 'w') as file:
                config.write(file)
            return True
        raise PermissionError("incorrect password or no password established for directory")
        return False
    def justCreated(self) -> bool:
        """
        check if file has been created with the instance

        Returns
        -------
        bool
            True if file has been created upon creation of instance
            otherwise, false

        """
        return self._justCreated
    def getFileMode(self) -> str:
        """
        gets the mode set for the current file

        Returns
        -------
        str
            the mode as the associated charactors

        """
        config : configparser.ConfigParser = self._readConfig()
        if config is None:
            return None
        return config[self._filename]["mode"] 
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
            passwordFlag = None
        else:
            hashSalt = int(config["main"]["hashSalt"])
            hashSalt = hashSalt.to_bytes(int(config["main"]["hashSize"]), config["main"]["endienness"])
            if checkHashSalt(password, hashSalt, int(config["main"]["saltSize"]), encoding):
                passwordFlag = True
            else:
                passwordFlag = False
                
        if self._isUnlocked == True:
            passwordFlag == True
        if time.time() - startTime < passwordCheckTime:
            time.sleep(time.time() - startTime)
        waitRandomTime(1)
        return passwordFlag
    
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
        passwordFlag : bool | None = super(LockedFile, self)._checkPassword(oldPassword, encoding)
        config = self._readConfig()
        if config is None:
            return False
        if passwordFlag == False:
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