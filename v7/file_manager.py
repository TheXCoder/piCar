# -*- coding: utf-8 -*-

import copy
"""
Created on Tue May 14 21:04:10 2024

@author: Phatty
"""
import io, os
from misc import *

class DirectoryManager:
    #lockedDir has the following items:
    # [str], directory as string: [str], determines what modes are able to access directory
    __lockedDirectories : dict = {}
    def __init__(self, directory : str, mode : str):
        self._mode = mode
        #directory has been configured to be locked
        if any(lockedDir == directory for lockedDir in self.__lockedDirectories.keys()):
            ...
        #checking to see if an
        possibleDirectories = [lockedDir for lockedDir in self.__lockedDirectories.keys() if lockedDir in directory]
        if len(possibleDirectories > 0):
            possibleDirectories = rankMatchString(directory, possibleDirectories)
        if any(possibleDirectories)
            
            
    @staticmethod
    def createDirectory(directory : str):
        if os.path.exists(directory):
            ...
    @staticmethod
    def lockDirectory(directory : str, accessType : bool):
        if any(directory == lockedDir for lockedDir in DirectoryManager.__lockedDirectories.keys()):
            return False
        if DirectoryManager.isModeValid(accessType) is False:
            return False
        DirectoryManager.__lockedDirectories[directory] = accessType
        return True
    @staticmethod 
    def isModeValid(mode : str):
        if any(symbol not in "rwabt+x" for symbol in mode):
            return False
        if 'x' in mode and len(mode) > 1:
            return False
        if not any(permissionSymbol in mode for permissionSymbol in "rwa"):
            return False
        if 'b' in mode and 't' in mode:
            return False
        return True
            
    
        
        
            
    
        
            

class FileManger(DirectoryManager):
    #lockedFiles has the following items:
    # [str], fileDirectory : [bool], determines if the file is read-only [true] or completely unaccessable [false]
    __lockedFiles : dir = {};
    __filesInUse : dict = {};
    def __init__(self, fileDirectory : str, fileMode : str):
        """
        Class for more safety when handling files

        Parameters
        ----------
        fileDirectory : str
            directory for file, ior just use file name if
            file is in current working directory
        fileMode : str
            determines what type of access the file should open with
            all information of the fileModes is 
            quoted from https://docs.python.org/3/library/functions.html#open
            'r' - open for reading
            
            'w' - open for writing, truncating the file first
            
            'a' - open for writing, appending to the end of file if it exists
            
            the following must be combined with anyone of the previous in order to work
            
            'b' - binary mode
            
            't' - text mode (default)
            
            the following must be combined with only 'r' or 'w' in order to work
            
            '+' - open for updating (reading and writing)
            
            this next one is a unique case and cannot be combined with any of the above
            
            'x' - open for exclusive creation, failing if the file already exists
        """
        self.__fileDirectory : str = None;
        self._fileMode : str = fileMode
        if self.__checkFileDir(fileDirectory, fileMode) and self.__checkFileMode(fileDirectory, fileMode):
            self.__filesInUse[self.__fileDirectory] = self
            self.__fileDirectory = fileDirectory
        
        self.__file : io.TextIOWrapper = None
    
    def __del__(self):
        """
        removes instance from list of files in use to
        allow other instances access to the file

        Returns
        -------
        None.

        """
        del self.__filesInUse[self.__fileDirectory]
    
    def __checkFileDir(self, fileDirectory, fileMode):
        if fileDirectory in self.__lockedFiles:
            try:
                assert self.__lockedFiles[fileDirectory]
                if any(char in "xw+a" for char in fileMode) :
                    raise PermissionError("File is read-only")
                    return False
            except AssertionError:
                raise PermissionError("This file is locked")
                return False
        
        if fileDirectory in self.__filesInUse:
            error = "File is being used by a different instance, \""
            error += str(type(self.__filesInUse[fileDirectory])) + "\" -->> \""
            error += str(id(self.__filesInUse[fileDirectory]))
            error +="\". Either delete instance or don't ask to open the file"
            raise FileExistsError(error)
            return False
        return True
    
    def __checkFileMode(self, fileDirectory : str, fileMode : str):
        if fileMode == 'x':
            try:
                assert not os.path.isfile(fileDirectory)
                with open(fileDirectory, fileMode):
                    ...
                return True
            except AssertionError:
                raise FileExistsError("File cannot be created because it already exist")
                return False
        if 'x' in fileMode:
            raise TypeError("this mode cannot be stacked with othe modes and is only useful when creating files")
        if any(char in "r+" for char in fileMode) :
            try:
                assert os.path.isfile(fileDirectory)
            except AssertionError:
                raise FileNotFoundError("File does not exist")
                return False
        return True
        
#------lock file---------------------------
    @staticmethod
    def lockFile(fileDirectory : str, isReadOnly : bool = False):
        FileManger.__lockedFiles[fileDirectory] = isReadOnly
        
#-------context handling methods------------    
    def __enter__(self):
        if self._fileMode == 'x':
            raise TypeError("File cannot be opened when the mode is in exclusive creation ")
            return self
        self.__file = open(self.__fileDirectory, self._fileMode)
        return self
    
    def __exit__(self,exc_type, exc_val, exc_tb):
        self.__file.close()


#--------standard open and close methods-------
    def open(self) -> bool:
        if self._fileMode == 'x':
            raise TypeError("File cannot be opened when the mode is in exclusive creation ")
            return False
        self.__file = open(self.__fileDirectory, self._fileMode)
        return True
    def close(self) -> bool:
        if self.__file is None:
            return False
        self.__file.close()
        self.__file = None
        return True
    
#---------access data---------------------
    def read(self, size : int  = 1):
        if self.__file is None:
            raise RuntimeError("The instance has never been opened. Use the open() method or the with context manager")
        if any(char in "r+" for char in self._fileMode):
            return self.__file.read(size)
        raise TypeError("This instance is in write-only mode try remaking instance in a read mode")
        return None
    
    def write(self, data : str):
        if self.__file is None:
            raise RuntimeError("The instance has never been opened. Use the open() method or the with context manager")
        if any(char in "aw+" for char in self._fileMode):
            self.__file.write(data)
            return True
        raise TypeError("This instance of class is in read-only mode, try remaking instance in a write mode")
        return False
#---------get info methods-----------------    
    def getInfoAsText(self) -> str:
        info : str = "Instance ID: \"" + str(type(self)) + "\" -->> \"" + str(id(self)) + "\""
        info += "\nFile directory: " + self.__fileDirectory
        info += "\nFile mode: " + self._fileMode
        info += "\nAmount written" + str(self._writeAmount)
        return info
    
    @staticmethod
    def getFilesDirectoryList() -> list:
        info : list = []
        for fileDirectory in FileManger.__filesInUse.keys():
            info.append(fileDirectory)
        return info
    
#----------methods to restrict access-------------
    @property
    def fileDirectory(self):
        return self.__fileDirectory
    
    @fileDirectory.setter
    def fileDirectory(self, value):
        raise TypeError("Values of the instance cannot be modified")
    
if __name__ == "__main__":
    ...
   # raise NotImplementedError("This is a module is not a script and should only be imported")

        