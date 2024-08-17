# -*- coding: utf-8 -*-
"""
Created on Fri May  3 17:53:48 2024

@author: Phatty
"""
from __future__ import annotations
import socket, time, json
from my_message import MyMessage
from typing import Callable, Annotated


#=============Original=================================
class SocketHandler(MyMessage):
    def __init__(self, deviceSocket : socket.socket, eventsDictionary : dict = None):
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
        eventsDictionary = {} if eventsDictionary is None else eventsDictionary
        eventsDictionary["endc"] = self.__getEndCommunication #adds buitin messages assocciated with sockets
        super(SocketHandler,self).__init__(eventsDictionary)
        self._socket : socket.socket = deviceSocket

#--------------close and remove socket methods----------------------------
    def __del__(self):
        """
        
        deleting the instance of the class will
        Force terminates socket without letting any devices know

        Returns
        -------
        None.

        """
        self.__closeSocket()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__closeSocket()
        
    def _closeSocket(self)->bool:
        """
        closes sockets and removes closed socket

        Returns
        -------
        bool
            True if socket has been closed
            False, if socket does not exist

        """
        if self._socket is not None:
            self._socket.close()
            self._socket = None
            self._logger.debug("socket has been closed by instance")
            return True
        self._logger.warning("socket has either been closed or never existed")
        return False

#--------------------check if socket is valid-----------------------
    def isSocketValid(self) -> bool:
        """
        Check if socket is has not been closed
        by the instance of the class

        Returns
        -------
        bool
            False if socket has been closed by the instance
            otherwise True

        """
        if self._socket is None:
            return False
        return True


#--------------------built in communication methods---------------------

    
    
    def endCommunication(self, data) -> bool:
        """
        A command to manually add a end communication
        command to the send que

        Parameters
        ----------
        data : TYPE
            data associated with the command

        Returns
        -------
        bool
            return True upon adding the command to que
        """
        self.command("endc", data)
        return True

#-------------send messages--------------------------------------
    def nextMessage(self):
        """
        An iterator to send next message on the que
        using the socket

        Yields
        ------
        bool
            True, if message is sent
        
        Returns
        -------
        None if the next message ends the communication
        False if their are no more message in the que

        """
        while True:
            try:
                assert self._socket is not None
                message : str; encoding : str
                message, encoding = next(super(SocketHandler, self).nextMessage())
                self._socket.send(message.encode(encoding))
                
                #termanates self if accepted the end communication
                try:
                    messageData = json.loads(message)
                    if messageData["command"] == "acct":
                        if messageData["data"]["command"] == "endc":
                            self._closeSocket()
                            return None
                except json.JSONDecodeError:
                    ...
                yield True
            except StopIteration: 
                ...
            except AssertionError:
                self._logger.error("socket cannot send messages because it has been terminated within the instance or has never existed")
                raise RuntimeError("socket does not exist within the instance")
            return False
#----------recieved messages-----------------------------------------------
    def _endCommunicationProccessor(self, data):
        """
        

        Parameters
        ----------
        data : TYPE
            DESCRIPTION.

        Raises
        ------
        NotImplementedError
            DESCRIPTION.

        Returns
        -------
        bool
            DESCRIPTION.
        data : TYPE
            DESCRIPTION.

        """
        raise NotImplementedError()
        return True, data
    
    def __getEndCommunication(self, recvMessage : dict, encoding : str):
        """
        A builtin methoded that 
        allows for the end communication
        command to close communication
        between instances of the clas

        Parameters
        ----------
        recvMessage : dict
            recieved message as a dictionary
        encoding : str, optional
            encoding of recieved message.

        Returns
        -------
        dict
            returns a dictionary {"command":None, "ID":None}.

        """
        canClose : bool = False
        returnData = None
        try:
            canClose, returnData = self._endCommunicationProccessor(recvMessage["data"])
        except NotImplementedError:
            canClose = True
        self._acceptAndDecline(recvMessage, returnData, canClose)
        return {"command" : None, "ID" : None}
    
    def _getAcceptDeclineMessage(self, recvMessage : dict, encoding : str, isAccepted : bool):
        """
        handles accept and Decline messages and stores their data to be accessed later
        
        
        Parameters
        ----------
        recvMessage : dict
            recieved message as a dictionary
        encoding : str
            encoding as recieved message
        isAccepted : bool
            This will be True if recieved message is an accepted message.
            False if recieved message is an decline message.

        Returns
        -------
        dict
            returns dictionary {"command", command as [str] : [int], ID as int}
            the information in the dictionary can be used to access
            the stored data from the message

        """
        commandID = recvMessage["ID"]
        if self._commandIDs[commandID]["command"] != recvMessage["data"]["command"]:
            error = "Command, " + recvMessage["data"]["command"] + ", with ID["
            error += str(recvMessage["ID"]) + "] does not exist."
            raise KeyError(error)
            return {"command" : None, "ID" : None}
            
         #command IDs has the following keys:
         #   [int], the id number as an integer, no two commands can have same ID
         #       inside the ID key:
         #           "command" : name of command
         #           "data" : data that is used with the command
         #           "hasAccept" : True/False, true if command was recieved 
         #               with an accepted command, false if decline command
         #               This will start as None if no accept/decline message was recieved
         #           "replyData" : the data the was recieved from the 
         #               accept/decline message for the command
         #               This will start as None if no accept/decline message was recieved
         #           "messageSent" : True/False, true if message has been called using the
         #               nextMessage() generator
         #
        
        if self._commandIDs[commandID]["command"] == "endc" and isAccepted:
            self._closeSocket()
        self._commandIDs[commandID]["replyData"]=recvMessage["data"]["data"]
        self._commandIDs[commandID]["hasAccept"] = isAccepted
        return {"command" : recvMessage["data"]["command"], "ID" : commandID}
    
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
            self._logger.debug("recieved a message from the socket")
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
        except AssertionError:
            self._logger.error("socket cannot receive messages because it has been terminated within the instance or has never existed")
            raise RuntimeError("socket does not exist within the instance")
        return {"command" : None, "ID" : None}
    
            
        






    
    