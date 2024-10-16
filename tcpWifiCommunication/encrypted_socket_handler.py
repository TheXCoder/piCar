# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 18:44:31 2024

@author: Phatty
"""
from command import Command
from encrypted_my_message import EncryptedMyMessage
import socket, json
from misc import checkTypeSoft
class EncryptedSocketHandler(EncryptedMyMessage):
    """
    A better Socket handler for a better future
    keeps messages over tcp private via encryption
    """
    __doc__ += "\n\n" + EncryptedMyMessage.__doc__
    def __init__(self, deviceSocket : socket.socket | None, eventDictionary : dict | None = None):
        """
        Automatically handle sockets and streamlines the message from sockets
   
        Parameters
        ----------
        deviceSocket : socket.socket
            must be valid socket
            I strongly recommend a socket that looks like
            socket.socket(socket.AF_INET, socket.SOCK_STREAM) as no other versions have been tested. 
        eventsDictionary : {str, func(data)-> bool | data}, optional
            creates a dictionary of events. The default is None.
        """ 
        #this flag tells the socket to stay open and ignore the endCommunication command
        #this will cause the instance to send a decline message to the endCommuincation message
        self._keepOpenFlag = False 
        
        self._endingMessage : dict | None = None
        self._socket : socket.socket | None = deviceSocket
        super(EncryptedSocketHandler, self).__init__(eventDictionary)
        print("encrypted socket handler instance has been created")
    
    def __del__(self):
        self.forceCloseSocket()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.forceCloseSocket()
#-----------------command----------------------
    def command(self, commandName : str, data : dict | None,  hasPriority : bool = False) -> dict | None:
        match commandName:
            case "endNow":
                self.forceCloseSocket()
                return {"command" : "endNow", "ID" : None}
            case "endCommunication":
                self.endCommunication(data)
                return {"command" : "endCommunication", "ID" : None}
            case "youDead":
                self.testAlive()
                return {"command" : "youDead", "ID" : None}
            case _:
                return super(EncryptedSocketHandler, self).command(commandName, data)
    
#-------------------------------
    def isSocketValid(self):
        return self._socket is not None
    
#---------------#builtin commands---------------------
    def forceCloseSocket(self):
        print("Force closing socket communication")
        super(EncryptedSocketHandler, self).command("endNow", data=None, hasPriority= True)
        return True
        
    def endCommunication(self, data : dict = None):
        print("generating a end communication command to be sent")
        endingMessage = super(EncryptedSocketHandler, self).command("endCommunication" , data)
        if self._endingMessage is None:
            self._endingMessage = endingMessage
        return True
   
    def testAlive(self):
        super(EncryptedSocketHandler, self).command("youDead", data = None, hasPriority=True)
        
        
        
    
#send messages
    def send(self):
        while len(self._commandQue):
            print("Attempting to send a message using socket protocol")
            self._checkCanMakeAES()
            #checks to see if the socket is valid
            if self._socket is None:
                message : str = "socket has been closed within the EncryptedSocketHandler instance"
                print(message)
                self._logger.error(message)
                raise RuntimeError(message)
                return None
            
            
            messageGenerator = None
            if self._aesKey is not None and self._encryptionMode == "AES":
                messageGenerator = self._sendAESEncrypted()
            elif self._sendKey is not None and self._encryptionMode == "RSA":
                messageGenerator = self._sendRSAEncrypted()
            else:
                if self._numberOfTimesTriedToSendEncryption <= self._MAXENCRYPTIONSENDTIMES:
                    self._logger.warning("Messages cannot be encrypted. Anyone can view the message")
                messageGenerator = self._getMessageToSend()
            
            
            for message in messageGenerator:
                if checkTypeSoft(message, bytes):
                    try:
                        self._socket.send(message)
                    except ConnectionAbortedError:
                        self._socketUncleanError()
                else:
                    try:
                        self._socket.send(message.encode(self._ENCODINGMESSAGEENCODING))
                    except ConnectionAbortedError:
                        self._socketUncleanError()
                    
                print("message has been sent using the socket")
                yield True
            #Force closing communication
            try:
                assert self._endingMessage["command"] == "endNow"
                if self.getCommandInfo(self._endingMessage)["commandSent"] is True:
                    self._socket.close()
                    self._socket = False
            except AssertionError:
                pass
            except TypeError:
                pass
        return None
#recieve messages
    def _socketUncleanError(self):
        self._socket = None
        errorMessage : str = "The connection between the two sockets has been terminated uncleanly."
        self._logger.error(errorMessage)
        raise ConnectionAbortedError(errorMessage)

    def _getForceCloseSocket(self, messageRecieved : dict):
        self._socket.close()
        self._socket = None
        return True
    def _getEndCommunication(self, messageRecieved : dict):
        """
        Handles the endCommunication command
        
        if the communiction can be ended then
        the endCommunication command recieved will spawn an endNow
        
        If the communication cannot be ended then
        the endCommunication command recieved will spawn a declining message

        Parameters
        ----------
        messageRecieved : TYPE
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if self._keepOpenFlag is True:
            self._acceptDecline(messageRecieved, -1, {"error" : "socket busy"})
            return False
        self.forceCloseSocket()
        return True
    
    def _getTestAlive(self, messageRecieved : dict):
        self._acceptDecline(messageRecieved, 1, None)
        return True
    
    def recv(self):
        print("recieving message from socket")
        if self._socket is None:
            message : str = "socket has been closed within the EncryptedSocketHandler instance"
            self._logger.error(message)
            raise RuntimeError(message)
            return None
        messageSize : int; messageEncoding : str;
        messageSize, messageEncoding = self.getMessageFormat()
        recievedMessage : str = ""
        recievedMessage = self._socket.recv(messageSize)
        try:
           recievedMessage = recievedMessage.decode(messageEncoding)
           #checks message encoding
           if self._setEncodingFromMessage(recievedMessage):
               return {"command" : None, "ID" : None} #returns this so that the message settings are not reset look down ↓
           
        except UnicodeDecodeError:
            self._logger.debug("This message is encrypted attempting to decrypted the message")
            #decrypts message
            if self._nextMessageEncryptionType is not None:
                recievedMessage = self._getDecryptedMessage(recievedMessage)
        
        
        self._checkCanMakeAES()
        
        #processes recieved message
        self._logger.debug("processing message")
        returnValue : dict | None = {"command" : None, "ID" : None}
        recvMessage : dict = json.loads(recievedMessage)
        match recvMessage["command"]:
            case "echo":
                self._returnEcho(recvMessage)
                returnValue = None
            case "reply":
                self._getReply(recvMessage)
            #newly added functions
            case "newRSA":
                self._getRSA(recvMessage)
            case "newAES":
                self._getAES(recvMessage)
            case "bossID":
                self._getBossNumber(recvMessage)
            case "endNow":
                self._getForceCloseSocket(recvMessage)
            case "endCommunication":
                self._getEndCommunication(recvMessage)
            case "youDead":
                raise NotImplementedError
            case "accept":
                 returnValue = self._getAcceptAndDecline(recvMessage)
                 if "newRSA" == returnValue["command"]:
                     self._canSendEncryption = True
            case "decline":
                returnValue = self._getAcceptAndDecline(recvMessage)
                if "newRSA" == returnValue["command"] and self._numberOfTimesTriedToSendEncryption < self._MAXENCRYPTIONSENDTIMES:
                    self._canSendEncryption = False
                    self._getNewRSAEncryption()
                    self._numberOfTimesTriedToSendEncryption += 1
                
            case "error":
                returnValue = self._getAcceptAndDecline(recvMessage)    
                if "newRSA" == returnValue["command"] and self._numberOfTimesTriedToSendEncryption < self._MAXENCRYPTIONSENDTIMES:
                    self._canSendEncryption = False
                    self._getNewRSAEncryption()
                    self._numberOfTimesTriedToSendEncryption += 1
            case _:
                try:
                    self._getCommandMessage(recvMessage)
                except KeyError:
                    logMessage : str = "\"{commandName}\" does not have a function associated with it."
                    logMessage.format(commandName = recvMessage["command"])
                    command : Command = Command("decline", recvMessage["ID"], None, recvMessage["hasPriority"])
                    self._addToQue(command, recvMessage["hasPriority"])
                    self._logger.warning(logMessage)
        
        #resets message setting so that next message can be sent
        self._currentMessageSize : int = 0
        self._currentMessageEncoding : str = ""
        self._nextMessageEncryptionType = None
        return returnValue
    
    