# -*- coding: utf-8 -*-
"""
Created on Fri May  3 17:53:48 2024

@author: Phatty
"""
from __future__ import annotations
import socket, time, json
from MyMessage import MyMessage
from typing import Callable, Annotated


#=============Original=================================
class SocketHandler(MyMessage):
    def __init__(self, deviceSocket : socket.socket, eventsDictionary : dict = {}):
        """
        Automatically handle sockets and streamlines the message from sockets
   
        Parameters
        ----------
        deviceSocket : socket.socket
            must be valid socket
            I strongly recommend a socket that looks like
            socket.socket(socket.AF_INET, socket.SOCK_STREAM) as no other versions have been tested. 
        eventsDictionary : {str, func(data)-> bool | data}, optional
            creates a dictionary of events. The default is {}.
        """ 
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
        
    def __closeSocket(self)->bool:
        """
        closes sockets and removes closed socket

        Returns
        -------
        bool
            True if socket has been closed
            False, if socket does not exist

        """
        if self.__socket is not None:
            self.__socket.close()
            self.__socket = None
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
        if self.__socket is None:
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
                assert self.__socket is not None
                message : str; encoding : str
                message, encoding = next(super(SocketHandler, self).nextMessage())
                self.__socket.send(message.encode(encoding))
                
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
            assert self.__socket is not None
            messageSize : int; messageEncoding : str
            messageSize, messageEncoding = self.nextMessageFormat()
            recievedMessage : str = self.__socket.recv(messageSize).decode(messageEncoding)
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
            
        




#===========helper functions=================================

def findDevice(device_IPOrName : str, isLocal : bool = True, numberIntervals : int = 5, intervalWaitTime : float = 1) -> tuple(str):
    """
    Find the name and ip of host by using name or ip

    Parameters
    ----------
    host_IPOrName : str
        IP example: 64.233.160.5
        the system name of device you want to find
    isLocal : bool, optional
        Binary value to determine weither to look for
        the device on the local area network, or on the internet
        this value only matters if using a name to search for device
        The default is True.
    numberIntervals : int, optional
        How many times the function will try to look for the device. 
        The default is 5.
    intervalWaitTime : float, optional
        Wait period in between search cycles.
        The measurement is in seconds The default is 1 for 1 second

    Raises
    ------
    ConnectionError
        if device cannot be located

    Returns
    -------
    tuple(str, str)
        tuple(host name, hostIP).

    """
    deviceIP : str = int((device_IPOrName[0]).isnumeric()) * device_IPOrName
    deviceName : str = int(deviceIP=="") * device_IPOrName
    for count in range(numberIntervals):
        try:
            if deviceIP != "":
                deviceIP = socket.gethostbyaddr(deviceIP)[0]
            #this block will never get ran if the the first if statement ran
            elif deviceName != "":
                deviceIP = socket.gethostbyname(deviceIP + (".local" * isLocal))
            return deviceName, deviceIP
        except socket.gaierror or socket.herror:
            time.sleep(intervalWaitTime)
    error : str = ""
    if deviceName == "":
        error = "host"
    else:
        error = "local" * int(isLocal)
        error += f"host named \"{deviceName}\""
    if deviceIP != "":
        error += " with IP \"{deviceIP}\""
    error += " cannot be found"
    raise ConnectionError(error)
    return "", ""

#============server=====================================

class ListeningServer:
    def __init__(self, port : int, amountOfClients : int = 1): 
        """
        server for handling incoming clients

        Parameters
        ----------
        port : int
            port the listening server is hosted at
            I recommond an unsused port like (6060) or something
        amountOfClients : int, optional
            amount of clients can be connected to the listening server at once. The default is 1.

        
            

        """
        
        self.__listeningPort : int = port
        self.__hostname : int = socket.gethostname()
        self.__hostIP : int = socket.gethostbyname(self.__hostname)
        
        self.__listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listeningSocket.bind((self.__hostIP, self.__listeningPort))
        self.__listeningSocket.listen(amountOfClients)

    def __del__(self):
        """
        Force terminates ListeningServer socket upon call
        Does not warn client

        Returns
        -------
        None.

        """
        self.__listeningSocket.close()
    
    def getSocket(self) -> tuple:
        """
        returns socket for hosting client and client information
        all information can be passed to the HostingServer as parameters
        
        Returns
        -------
        tuple (socket, dict)
            the socket for communication IMPORTANT: this socket must be terminated
            by using socket.close()
            
            client information has the following items:
                "client name" : [str], the name of the client
                "client address" : [str], the client IP address
                "client port" : [int], the port used by the client to communicate
        
        Additional Information
        ----------------------
        The HostingServer will automatically handle the socket and close it without
        any additional coding.
        """
        communicationSocket, clientAddress = self.__listeningSocket.accept() #becuase client address and port is a tuple? ¯\_(ツ)_/¯
        clientAddress, clientPort = clientAddress
        
        clientName = socket.gethostbyaddr(clientAddress)
        return communicationSocket, {"client name":clientName[0], "client address": clientAddress, "client port":clientPort}

    
    