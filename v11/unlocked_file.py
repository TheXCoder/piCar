# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 20:26:28 2024

@author: Phatty
"""


import io, time
from locked_file import LockedFile

class UnlockedFile(LockedFile):
    def __init__(self, filename, password : str | None = None, encoding : str = "utf-8", unlockFile : bool = False):
        self._isUnlocked : bool = False
        super(UnlockedFile, self).__init__(filename, password, encoding)
    
    def unlock(self, password : str | None = None, encoding : str = "utf-8"):
        if self._checkPassword(password, encoding) is True:
            self._isUnlocked = True
            return True
            
        #if the password is wrong it doesn't relock the file
        #you should us the lock method instead
        return False
    
    def lock(self):
        if self._isUnlocked is True:
            self._isUnlocked = False
            self._logger.warning("File" + self._fullFilePath + " is locked")
            return True
        self._isUnlocked = False
        return False
    
    def _checkLock(self, password : str | None = None, encoding : str = "utf-8"):
        if self._isUnlocked:
            return True
        return self._checkPassword("" if password is None else password, encoding)
    
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
        passwordGood : bool = self._checkLock(password, encoding)
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
        passwordGood : bool = self._checkLock(password, encoding)
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
        passwordFlag : bool = self._checkLock(password, encoding)
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
    
    