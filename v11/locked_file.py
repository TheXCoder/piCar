# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 15:47:41 2024

@author: Phatty
"""

from locked_dir import LockedDir
from misc import createFile
import os, io, time, logging
import Cryptodome.Cipher
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2 as AES_PBKDF2
from Cryptodome.Util.Padding import pad as cryptPad, unpad as cryptUnpad


class LockedFile(LockedDir):
    _configFileDict : dict = {"mode" : None,
                              "timeCreated" : None,
                              "lastEdited" : None,
                              "fileSigniture" : None
                              }
    
    __doc__ = LockedDir.__doc__ 
    def __init__(self, filename, password : str | None = None, encoding : str = "utf-8"):
        """
        

        Parameters
        ----------
        filename : TYPE
            DESCRIPTION.
        password : str | None, optional
            DESCRIPTION. The default is None.
        encoding : str, optional
            DESCRIPTION. The default is "utf-8".

        Raises
        ------
        TypeError
            DESCRIPTION.
        IOError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self._fullFilePath : str = os.path.abspath(filename)
        self._filename = self._fullFilePath.split(os.sep)[-1]
        self._cursor : int = 0
        self._justCreated : bool | None = None
        super(LockedFile, self).__init__(os.sep.join(self._fullFilePath.split(os.sep)[:-1]), password, encoding)
        
        self._logger = logging.getLogger(self._filename + " logger")
        if self.__createFile(password, encoding) is False:
            self._fullFilePath = None
            self._filename = None
            raise IOError("File cannot be created at all")
            
        
    def __del__(self):
        self._readConfig()
        
        self._generateFileHash()
        
    
    def __createFile(self, password : str | None = None, encoding : str = "utf-8"):
        #makes sure you knuckleheads cannot read to a important file for the directory
        if self._fullFilePath == self._configFileDir:
            raise PermissionError("You do not have permissions to write or read from the directory config file")
            return False
        if os.path.exists(self._fullFilePath):
            self._justCreated = False
            self.checkFileHash()
            return None
        if any(self._getFolderMode() == mode for mode in ("rs", "r")):
            raise PermissionError("The directory is in a read-only mode")
            self._filename = None
            return False
        password = "" if password is None else password
        passwordFlag = self._checkPassword(password, encoding)
        if any(self._getFolderMode() == mode for mode in ("s", "ws")):
            if passwordFlag is None:
                raise PermissionError("Oh no! There is no password for the directory when the directory in a secure write mode")
                return False
            if passwordFlag is False:
                raise PermissionError("Password provide is incorrect there for file cannot be created")
                return False
        if not createFile(self._fullFilePath):
            raise RuntimeError("This should not be possible yet here it is")
        self._justCreated = True
        self._readConfig()
        self._config.addSection(self._filename)
        self._config[self._filename] = self._configFileDict
        self._config[self._filename]["timeCreated"] = time.time()
        file : io.TextIOWrapper
        with open(self._configFileDir, "w") as file:
            self._config.write(file)
        return True
    
    
    def read(self, amount : int | None = None, isBinary : bool = False,
             password : str | None = None, encoding : str ="utf-8") -> str | bytes | None:
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
        encoding : str, optional
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
        self._readConfig()
        passwordGood : bool = self._checkPassword(password, encoding)
        if self._config["main"]["mode"] in ("rs", "s") and not passwordGood:
            raise PermissionError("directory is in a secure read mode")
            return None
        if self._config[self._filename]["mode"] in ("rs", "s") and not passwordGood:
            raise PermissionError("file is in a secure read mode")
            return None
        data : str | None | bytes = None
        readMode = "r" + "b"*isBinary
        if amount is None:
            with open(self._fullFilePath, readMode) as file:
                file.seek(self._cursor)
                data = file.read()
                self._cursor = 0
        if isinstance(amount, int) and amount > 0:
            with open(self._fullFilePath, readMode) as file:
                file.seek(self._cursor)
                data = file.read(amount)
                self._cursor += amount
        return data
    
    def write(self, data : str | bytes, isBinary : bool = False,
              password : str | None = None, encoding : str ="utf-8"):
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
        encoding : str, optional
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
        self._readConfig()
        if self._config is None:
            return None
        passwordGood : bool = self._checkPassword(password, encoding)
        if self._config["main"]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self._config["main"]["mode"] in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure write mode")
            return None
        if self._config[self._filename]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self._config[self._filename]["mode"] in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure write mode")
            return None
        writeMode = "w" + "b" * isBinary
        file : io.TextIOWrapper
        with open(self._fullFilePath, writeMode) as file:
            file.write(data)
        self._config[self._filename]["lastEdited"] = time.time()
        with open(self._configFileDir, 'w') as file:
            self._config.write(file)
        return True
    
    def append(self, data : str | bytes, isBinary : bool = False,
              password : str | None = None, encoding : str ="utf-8"):
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
        encoding : str, optional
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
        self._readConfig()
        passwordFlag : bool = self._checkPassword(password, encoding)
        if self._config is None:
            return None
        if self._config["main"]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self._config["main"]["mode"] in ("ws", "s") and not passwordFlag:
            raise PermissionError("file is in a secure write mode")
            return None
        if self._config[self._filename]["mode"] in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self._config[self._filename]["mode"] in ("ws", "s") and not passwordFlag:
            raise PermissionError("file is in a secure write mode")
            return None
        writeMode = "a" + "b" * isBinary
        with open(self._fullFilePath, writeMode) as file:
            file.write(data)
        self._config[self._filename]["lastEdited"] = time.time()
        with open(self._configFileDir, 'w') as file:
            self._config.write(file)
        return True
        return True
                
    
    def fileMode(self, mode : str, password : str | None = None, encoding : str = "utf-8"):
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
        encoding : str, optional
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
        match self.getFolderMode():
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
        if self._checkPassword(password, encoding) is True:
            self._readConfig()
            self._config[self._filename]["mode"] = mode
            with open(self._configFileDir, 'w') as file:
                self._config.write(file)
            return True
        raise PermissionError("incorrect password or no password established for directory")
        return False
    
    def _checkFileHash(self):
        self._readConfig()
        hashFlag : bool = False
        file : io.TextIOWrapper
        with open(self._fullFilePath,'r') as file:
            hashFlag = self._config[self._filename]["fileSigniture"] == hash(file.read())
        return hashFlag
    
    def checkFileHash(self):
        if self._checkFileHash() is False:
            self._logger.warning("file \"" + self._fullFilePath + "\" has been modifed outside of this class.")
            return False
        return True
    
    def _generateFileHash(self):
        file : io.TextIOWrapper
        with open(self._fullFilePath, 'r') as file:
            self._config[self._filename]["fileSigniture"] = hash(file.read())
        with open(self._configFileDir, 'w') as file:
            self._config.write(file)
        return True
    
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
        self._readConfig()
        return self._config[self._filename]["mode"]
    
    
            
    
        
        
        