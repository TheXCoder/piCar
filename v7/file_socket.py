# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:33:42 2024

@author: Phatty
"""

from socket_handler import SocketHandler
import socket, io, os, logging, json


class FileSocket(SocketHandler):
    __FILECHUNKSIZE = 200 # should be about 10 times the encoding message size
    _FOLDERSAVE = "recievedFiles"
    def __init__(self, deviceSocket : socket.socket, eventsDictionary : dict = None):
        """
        Automatically handle sockets and streamlines the message from sockets
        Now with direct file sending

        Parameters
        ----------
        deviceSocket : socket.socket
            usable socket to handle. The socket will be handled by instance
        eeventsDictionary : {str, func(data)-> bool | data}, optional
            creates a dictionary of events. The default is None.
        folderToSaveFilesDIR : str, optional
            a folder in directory to save files in. The default is None.

        """
        eventsDictionary = {} if eventsDictionary is None else eventsDictionary
        super(FileSocket,self).__init__(deviceSocket, eventsDictionary)
    
        self._masterPath : str = os.getcwd() #current directory where execution takes place

        
        
        self._folderToSaveDir = self._masterPath + os.sep + FileSocket._FOLDERSAVE
        #files to send have the following items:
        #   [str] filename, the name of the file : [generator], fileGenerator created by _fileGenerator
        self._filesToSend : dict(dict) = {}
        #files to recv have the following keys:
        #   [str] filename, the name of the file : [dict]
        #       inside the filename has the following keys:
        #       "isBinary" : [bool], a determines if the file is text or binary data
        #       [int] chunckNumber, determines the order of chuncks in the file : [filedata] data inside the file corisponding to the chunk
        #
        self._filesToRecv : dict = {}
    
    def _fileGenerator(self, filename : str, isBinary : bool = False) -> tuple:
        """
        creates a generator to the file

        Parameters
        ----------
        filename : str
            name of file.
        isBinary : bool, optional
            True, if the file is binary data. False, if file is
            text data. The default is False.

        Yields
        ------
        tuple
            [str], command name
            [dict], the data of command has the following items:
                "filename" : [str], name of file
                optional "isBinary" : [bool], as stated
                optional "fileData" : [dict], has the following keys:
                    [int], chunkIndex or the order of the chunk : chunkData

        """
        fileMode = "rb" if isBinary else "r"
        with open(filename, fileMode) as file:
            chunkData : str = ''
            chunkIndex = 0
            yield "finfo", {"filename" : filename.split(os.sep)[-1], "isBinary" : isBinary}
            while True:
                chunkData = file.read(self.__FILECHUNKSIZE)
                if chunkData == '':
                    break
                yield "fdata", {"filename": filename, 
                                "fileData":{chunkIndex : chunkData}}
                chunkIndex += 1
            yield "fend", {"filename" : filename}
        return filename, chunkIndex
    
    
    
    def loadFile(self, filename : str, isBinary : bool = False) -> bool:
        """
        loads file to be sent in messages

        Parameters
        ----------
        filename : str
            name of file to load. Directory of file can be used as well.
        sBinary : bool, optional
            True, if the file is binary data. False, if file is
            text data. The default is False.

        Raises
        ------
        KeyError
            If file has already been loaded.
            will also return false and not load the file

        Returns
        -------
        bool
            True, if file has been loaded.

        """
        if filename in self._filesToSend.keys():
            raise KeyError("Unfortantly you have this file all ready loaded")
            return False
        fileGen = self._fileGenerator(filename, isBinary)
        self._filesToSend[filename] = fileGen
        command, data = next(fileGen)
        self.command(command, data)
        return True
    
    def updateQue(self) -> bool:
        """
        (Please overload)
        function allows for que to be updated with with new messages
        loaded files will only add a message to the que when this method is called

        Returns
        -------
        bool
            True, if method updated que
            False, if method cannot update que

        """
        if not self._filesToSend:
            return False
        endedFilesKeys : list = []
        for key in self._filesToSend:
             gen = self._filesToSend[key]
             try:
                 command, data = next(gen)
                 self.command(command, data)
             except StopIteration:
                 endedFilesKeys.append(key)
        for endKey in endedFilesKeys:
            del self._filesToSend[endKey]
        return True
#--------------recv message----------------------
    def _getFileInfo(self, recvMessage : dict, encoding : str) -> tuple:
        """
        processes file info

        Parameters
        ----------
        recvMessage : dict
            message recieved as dict.
        encoding : str
            message encoding

        Returns
        -------
        tuple
            {"command" : None, "ID" : None}

        """
        #recvMessage has the following items:
        #   "command" : [str], name of the command
        #   "data" : [dict], data has the following keys: 
        #       "filename": [str], name of the file 
        #       "isBinary" : [bool], determines if file is binary
        data : dict = recvMessage["data"]
        if data["filename"] in self._filesToRecv.keys():
            self._acceptAndDecline(recvMessage, None, False)
        else:
            self._filesToRecv[data["filename"]] = {"isBinary" : data["isBinary"]}
            self._acceptAndDecline(recvMessage, None, True)
        return {"command" : None, "ID" : None}
        
    def _getFileData(self, recvMessage : dict, encoding : str) -> dict:
        """
        processes file data and orders it

        Parameters
        ----------
        recvMessage : dict
            message recieved as dict.
        encoding : str
            message encoding.

        Returns
        -------
        dict
            {"command" : None, "ID" : None}

        """
        #recvMessage has the following items:
        #   "command" : [str], name of the command
        #   "data" : [dict], data has the following items: 
        #       "filename": [str], name of the file 
        #       "fileData" : [dict] has the following items:
        #           [int], chunk number : [str], data from the File
        data : dict = recvMessage["data"]
        if data["filename"] in self._filesToRecv.keys():
            # I do not know why but the chunk index key in file data is a string
            fileDataConverted, fileDataUnconverted = self.__fileDataHelp(data["fileData"])
            fileData : dict = {}
            fileData.update(fileDataConverted)
            fileData.update(fileDataUnconverted)
            self._filesToRecv[data["filename"]].update(fileData)
            self._acceptAndDecline(recvMessage, data["filename"], True)
            print(fileData)
        else:
            self._acceptAndDecline(recvMessage, None, False)
        return {"command" : None, "ID" : None}            
    
    def __fileDataHelp(self, fileData : dict) -> tuple:
        """
        helps processing file data and orders it
        converts file key str into int

        Parameters
        ----------
        fileData : dict
            original fileData from _getFileData method

        Returns
        -------
        tuple
            ([dict] converted file data, [dict] unconverted file data.)

        """
        fileDataConverted : dict = {} #items where keys can be converted into ints
        fileDataUnconverted : dict = {} # items where keys cannot be converted to ints
        for key, value in zip(fileData.keys(), fileData.values()):
            try:
                fileDataConverted.update({int(key) : value})
            except ValueError:
                fileDataUnconverted.update({key : value})
        return fileDataConverted, fileDataUnconverted
                
        
            
    def _getFileEnd(self, recvMessage : dict, encoding : str):
        """
        processes file end message and writes file to specified folder
        in the directory specified by folderToSaveFilesDIR

        Parameters
        ----------
        recvMessage : dict
            message recieved as dictionary
        encoding : str
            message encoding

        Returns
        -------
        dict
            {"command" : None, "ID" : None}

        """
        #recvMessage has the following items:
        #   "command" : [str], name of the command
        #   "data" : [dict], data has the following keys: 
        #       "filename": [str], name of the file 
        data : dict = recvMessage["data"]
        #files to recv have the following keys:
        #   [str] filename, the name of the file : [dict]
        #       inside the filename has the following keys:
        #       "isBinary" : [bool], a determines if the file is text or binary data
        #       [int] chunckNumber, determines the order of chuncks in the file : [filedata] data inside the file corisponding to the chunk
        #
        
        if data["filename"] in self._filesToRecv.keys():
            recvFileInfo : dict = self._filesToRecv[data["filename"]]
            fileMode = "wb" if recvFileInfo["isBinary"] else "w"
            if not os.path.exists(self._folderToSaveDir):
                os.mkdir(self._folderToSaveDir)
            os.chdir(self._folderToSaveDir)
        
        #the split for the file name is to gaurd against directory data
        #the os seperator is the seperator between directories
        #   example the "\" in C:\Users
            with open(data["filename"].split(os.sep)[-1], fileMode) as file:
                chunkIndex : int = 0
                while chunkIndex in recvFileInfo.keys():
                    file.write(recvFileInfo[chunkIndex])
                    chunkIndex +=1
            os.chdir(self._masterPath)
            del self._filesToRecv[data["filename"]]
            self._acceptAndDecline(recvMessage, None, True)
        else:
            self._acceptAndDecline(recvMessage, None, False)
        return {"command" : None, "ID" : None}
    
    def recv(self) -> dict:
        """
        recieves messages from socket and processes them into useful commands
        and information
        Raises
        ------
        KeyError
            If the command recieved is not a command that has been bounded to a function.
        RuntimeError
            if the socket has been closed
    
        Returns
        -------
        dict
            If the recieved message is a valid accept or decline message
            that was sent to respond to this instance of the class's message 
            The method will return dictionary:
            {"command":command, "ID":ID}. Please use this to
            access the data from the message by using the method getData(dict|str, int)
    
        """        
        try:
            assert self._socket is not None
            messageSize : int; messageEncoding : str
            messageSize, messageEncoding = self.nextMessageFormat()
            messageRecieved : str = self._socket.recv(messageSize).decode(messageEncoding)
            returnValue = self._getFormatMessage(messageRecieved, messageEncoding)
            if isinstance(returnValue, dict):
                return returnValue
            
            recvMessage : dict = json.loads(messageRecieved)
            if recvMessage["command"] == "echo":
                returnValue = self._getEchoMessage(recvMessage, messageEncoding)
            elif recvMessage["command"] == "rply":
                returnValue = self._getEchoReplyMessage(recvMessage, messageEncoding)
            elif recvMessage["command"] == "endc":
                returnValue = self.__getEndCommunication(recvMessage,messageEncoding)
            elif recvMessage["command"] =="finfo":
                returnValue = self._getFileInfo(recvMessage, messageEncoding)
            elif recvMessage["command"] == "fdata":
                returnValue = self._getFileData(recvMessage, messageEncoding)
            elif recvMessage["command"] == "fend":
                returnValue = self._getFileEnd(recvMessage, messageEncoding)
            elif recvMessage["command"] == "acct":
                returnValue = self._getAcceptDeclineMessage(recvMessage, messageEncoding, True)
            elif recvMessage["command"] == "decl":
                returnValue = self._getAcceptDeclineMessage(recvMessage, messageEncoding, False)
            
            elif recvMessage["command"] in self._eventsDictionary.keys():
                returnValue = self._getCommandMessage(recvMessage, messageEncoding)
            else:
                raise KeyError("The command \"" + recvMessage["command"] + "\" is not a known command")
                self._acceptAndDecline(recvMessage, None, False)
            self._currentMessageSize = 0
            self._currentMessageEncoding = ""
            return returnValue
            # if "endc" in commandDict.values():
            #     #command IDs has the following keys:
            #     #   [int], the id number as an integer, no two commands can have same ID
            #     #       inside the ID key:
            #     #           "command" : name of command
            #     #           "data" : data that is used with the command
            #     #           "hasAccept" : True/False, true if command was recieved 
            #     #               with an accepted command, false if decline command
            #     #               This will start as None if no accept/decline message was recieved
            #     #           "replyData" : the data the was recieved from the 
            #     #               accept/decline message for the command
            #     #               This will start as None if no accept/decline message was recieved
            #     #           "messageSent" : True/False, true if message has been called using the
            #     #               nextMessage() generator
            #     #
            #     commandInfo : dict = self._commandIDs[commandDict["ID"]]
            #     if(commandInfo["hasAccept"]):
            #         self.__closeSocket()
        except AssertionError:
            self._logger.error("socket cannot receive messages because it has been terminated within the instance or has never existed")
            raise RuntimeError("socket does not exist within the instance")
        return {"command" : None, "ID" : None}

if __name__ == '__main__':
    raise NotImplementedError("This must be import and not ran")