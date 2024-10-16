# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 15:08:46 2024

@author: Phatty
"""
import time, socket
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
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__listeningSocket.close()
    def getSocket(self) -> tuple:
        """
        returns socket for hosting client and client information
        all information can be passed to the HostingServer as parameters
        
        Returns
        -------
        socket.socket
            the socket for communication IMPORTANT: this socket must be terminated
            by using socket.close()
        dict    
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



