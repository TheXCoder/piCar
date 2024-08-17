# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:33:42 2024

@author: Phatty
"""

from socket_helper import SocketHandler
import socket, io, os, logging


class FileSocket(SocketHandler):
    __FILECHUNKSIZE = 200 # should be about 10 times the encoding message size
    def __init__(self, deviceSocket : socket.socket, folderToSaveFiles : str = None,
                 eventsDictionary : dict = None):
        eventsDictionary = {} if eventsDictionary is None else eventsDictionary
        eventsDictionary["finfo"] = self._getFileInfo
        eventsDictionary["fdata"] = self._getFileData
        eventsDictionary["fend"] = self._getFileEnd
        super(FileSocket,self).__init__(deviceSocket, eventsDictionary)
        
        self._masterPath : str = os.getcwd()
        if folderToSaveFiles is None:
            self._folderToSaveDir = self._masterPath
        else:
            self._folderToSaveDir = "./" + folderToSaveFiles
        self._filesToSend : dict(dict) = {}
        #files to recv have the following keys:
        #   [str] filename, the name of the file : [dict]
        #       inside the filename has the following keys:
        #       "isBinary" : [bool], a determines if the file is text or binary data
        #       [int] chunckNumber, determines the order of chuncks in the file : [filedata] data inside the file corisponding to the chunk
        #
        self._filesToRecv : dict = {}
            
    
    def _getFileInfo(self, data):
        #data has the following keys:
        #   "filename": [str], name of the file 
        #   "isBinary" : [bool], determines if file is binary
        print(vars(self))
        self._filesToRecv[data["filename"]] = {"isBinary" : data["isBinary"]}
        return True, None
        
    def _getFileData(self, data):
        #data has the following keys:
        #   "filename" : [str], name of file
        #   "fileData" : [dict]
        #       inside dictionary has following properties:
        #       [int] chunk number : [str], data from the file
        #   
        fileData : dict = data["fileData"]
        self._filesToRecv[data["filename"]].update(fileData)
        return True, fileData.keys()
    
    def _getFileEnd(self, data):
        #data has the following keys:
        #   "filename" : [str], name of the file
        recvFileInfo : dict = self._filesToRecv[data["filename"]]
        fileMode = "wb" if recvFileInfo["isBinary"] else "w"
        if not os.path.exists(self.__folderToSaveDir):
            os.mkdir(self.__folderToSaveDir)
        os.chdir(self.__folderToSaveDir)
        with open(data["filename"], fileMode) as file:
            chunkIndex : int = 0
            while chunkIndex in recvFileInfo.keys():
                file.write(recvFileInfo[chunkIndex])
                chunkIndex +=1
        os.chdir(self._masterPath)
        del self._filesToRecv[data["filename"]]
        return True, None
    
    def _createFileGenerator(self, filename : str, isBinary : bool = False):
        fileMode = "rb" if isBinary else "r"
        with open(filename, fileMode) as file:
            chunkData : str = ''
            chunkIndex = 0
            while True:
                chunkData = file.read(self.__FILECHUNKSIZE)
                if chunkData == '':
                    break
                yield filename, {chunkIndex : chunkData}
                chunkIndex += 1
        return filename, chunkIndex
    
    def loadFile(self, filename : str, isBinary : bool = False):
        if filename in self._filesToSend.keys():
            raise KeyError()
            return False
        self._filesToSend[filename] = self._createFileGenerator(filename, isBinary)
        self.command("finfo", {"isBinary" : isBinary})
        return True
    
    def updateQue(self):
        if not self._filesToSend:
            return False
        endedFilesKeys : list = []
        for key, value in zip(self._filesToSend.keys(), self._filesToSend.values()):
            try:
                filename : str; chunk : dict;
                filename, chunk = next(value)
                self.command("fdata", 
                             {"filename" : filename, "fileData" : chunk})
            except StopIteration:
                self.command("fend", {"filename" : key})
                endedFilesKeys.append(key)
        for endedFilesKey in endedFilesKeys:
            del self._filesToSend[endedFilesKey]
        return True
