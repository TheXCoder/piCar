# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 16:04:18 2024

@author: Phatty
"""
#✓
# To do 9/1/2024: add aes encryption
# To do 
from locked_file import LockedFile
import configparser, os, copy
class ConfigParsePuller:
    """
    a wrapper for configparser
    to help LockedFile instances to deal with configparser

    """
    def __init__(self): 
        self.__data : str = ""
    def write(self, data):
        self.__data += data
    @property
    def data(self):
        return self.__data
    @data.getter
    def data(self):
        returnData = self.__data
        self.__data = ""
        return returnData
    @data.setter
    def data(self, dataToAdd : str):
        self.__data += dataToAdd
        return self.__data
    
    
class LockedFileConfigParseConverter(LockedFile):
    def __init__(self, file : str, password : str | None = None,             
                 textEncoding : str = "utf-8"):
        """
        Locked File handler for config files

        Parameters
        ----------
        file : str
            file name / path
        password : str | None, optional
            Password is used for creating a file in a soft locked directory.
            The default is None.
        textEncoding : str, optional
            The encoding of the password. The default is "utf-8".


        """
        self._config : configparser.ConfigParser = configparser.ConfigParser()
        super(LockedFileConfigParseConverter, self).__init__(file, password, textEncoding)
    
    def load(self, password : str | None = None,textEncoding: str = "utf-8") -> None:
        """
        Load data from config file

        Parameters
        ----------
        password : str | None, optional
            Password is used for creating a file in a soft locked directory.
            The default is None.
        textEncoding : str, optional
            The encoding of the password. The default is "utf-8".

        Returns
        -------
        None
            I will tell you that this function returns nothing okay. Cool and goodbye

        """
        
        self._config.read_string(self.read(password = password, textEncoding=textEncoding))
    
    def save(self, password : str | None = None, textEncoding : str = "utf-8") -> None:
        """
        

        Parameters
        ----------
        password : str | None, optional
            Password is used for creating a file in a soft locked directory.
            The default is None.
        textEncoding : str, optional
            The encoding of the password. The default is "utf-8".

        Raises
        ------
        PermissionError
            if directory is password protected and password is incorrect

        Returns
        -------
        None
            getting returns from this function will resault in a missing void where
            your heart should be. You have been warned tin-man

        """
        password = "" if password is None else password
        passwordGood = self._checkPassword(password, textEncoding)
        if self._getFolderMode() in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self._getFolderMode() in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure mode")
            return None
        if self.getFileMode() in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self.getFileMode() in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure mode")
            return None
        puller : ConfigParsePuller = ConfigParsePuller()
        self._config.write(puller)
        self.write(puller.data, False, password, textEncoding)
    
    def __iter__(self) -> tuple:
        """
        iterations

        Yields
        ------
        tuple
            DESCRIPTION.

        """
        key : tuple
        for key in self._config.sections():
            yield (key, self._config.items(key))
        return None
    
    #properties to access config file information
    @property
    def config(self) -> configparser.ConfigParser:
        return self._config
    @config.getter
    def config(self) -> dict:
        return {s:dict(self._config.items(s)) for s in self._config.sections()}
    @config.setter
    def config(self, data : tuple):
        self._config[data[0]] = data[1]