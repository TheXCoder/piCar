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
            return True
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
    
    def _endCommunicationProccessor(self, dataIn) -> (bool, object):
        """
        PLEASE IMPLEMENT
        An unimplemented version of
        the end communication processor

        Parameters
        ----------
        dataIn : TYPE
            data that from the endc message

        Raises
        ------
        NotImplementedError
            Always raises a not this error
            because method is not implemented

        Returns
        -------
        (bool, reply data)
            implementations of this function require two returns
            bool:
                True if instance can accept the communication being ended
                False if the instance stilll needs to send and recieve crucial information
            reply data:
                The data the that is going to be sent with the acceot/decline message
                
        """
        raise NotImplementedError("This method should be defined in the child class")
        return True, dataIn
    
    def __getEndCommunication(self, data) -> tuple:
        """
        A builtin methoded that allows the ending of the
        allows for the end communication
        command to close communication
        between instances of the class

        Parameters
        ----------
        data : TYPE
            data from recieved form end communication command

        Returns
        -------
        tuple
            A bool value that determines if the instance
            accepts or declines the end communication
            command
            data associated with the accept/decline
            command

        """
        canEndCommunication : bool = True;
        newData = None
        try:            
            canEndCommunication, *newData = self._endCommunicationProccessor(data)
        except NotImplementedError:
            ...
        return canEndCommunication, newData
    
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
                            self.__closeSocket()
                            return None
                except json.JSONDecodeError:
                    ...
                yield True
            except StopIteration or AssertionError: 
                return False
#----------recieved messages-----------------------------------------------
    def recv(self):
        """
        receives message from socket
        and process them into useful information(s)

        Returns
        -------
        commandDict : TYPE
            {"command" : [str] command name, "ID" : [int] command ID}

        """
        commandDict = {"command" : None, "ID" : None}
        try:
            assert self._socket is not None
            messageSize : int; messageEncoding : str
            messageSize, messageEncoding = self.nextMessageFormat()
            recievedMessage : str = self._socket.recv(messageSize).decode(messageEncoding)
            commandDict : dict = super(SocketHandler,self).recv(recievedMessage, messageEncoding)
            if "endc" in commandDict.values():
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
                commandInfo : dict = self._commandIDs[commandDict["ID"]]
                if(commandInfo["hasAccept"]):
                    self.__closeSocket()
        except AssertionError:
            ...
        return commandDict
            
        






    
    