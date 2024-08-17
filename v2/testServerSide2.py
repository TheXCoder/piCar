# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 18:03:05 2024

@author: Phatty
"""
import socket, time
from MyMessage import *
class ListeningServer:
    def __init__(self, port : int, amountOfClients : int = 1):
        """
        

        Parameters
        ----------
        port : int
            Port for getting clients.
        amountOfClients : int, optional
            Amount of clients that can be used
            connect to the port at once
            The default is 1.

        Returns
        -------
        None.

        """
        
        self.__listeningPort : int = port
        self.__hostname : int = socket.gethostname()
        self.__hostIP : int = socket.gethostbyname(self.__hostname)
        
        self.__listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listeningSocket.bind((self.__hostIP, self.__listeningPort))
        self.__listeningSocket.listen(amountOfClients)

    def __del__(self):
        """
        Close closes socket when object is destroyed

        Returns
        -------
        None.

        """
        self.__listeningSocket.close()
    
    def getSocket(self):
        """
        Gets a unique socket for the client to communicate with
        make sure that the socket is properly closed

        Returns
        -------
        communicationSocket : TYPE
            Socket for server-client communication
        dict
            client information
            items used all keys are strings:
                
                client name : the name of the client (str)
                client address : the IP address of the client (str)
                client port : the port of the client (int)

        """
        communicationSocket, clientAddress = self.__listeningSocket.accept() #becuase client address and port is a tuple? ¯\_(ツ)_/¯
        clientAddress, clientPort = clientAddress
        
        clientName = socket.gethostbyaddr(clientAddress)
        return communicationSocket, {"client name":clientName, "client address": clientAddress, "client port":clientPort}

class HostingServer:
    def __init__(self, hostingSocket, clientInfo : dict = {}):
        self.__serverSocket = hostingSocket
        self.__clientInfo : dict = clientInfo
        self.__serverMessager = MyMessage({"endc":self.__closeSocket})
    
    def __del__(self):
        self.endCommunication()
        self.__serverSocket.close()
        self.__clientInfo = None

    def __closeSocket(self, data):
        self.__serverSocket.close()
        self.__serverSocket = None
        self.__clientInfo = None
        return True, None
#--------------------------------------------------------
    def endCommunication(self):
        self.__serverMessager.command("endc", None)
        for message, encoding in self.__serverMessager.nextMessage():
            self.__serverSocket.send(message.encode(encoding))
        
        self.__closeSocket(None)

    def echo(self, message : str):
        self.__serverMessager.echo(message)

    def queCommand(self, command : str, data):
        self.__serverMessager.command(command, data)
        
    def sendNext(self):
        try:
            message, encoding = next(self.__serverMessager.nextMessage())
            self.__serverSocket.send(message.encode(encoding))
            return True
        except StopIteration:
            return False
        
    def recv(self):
        if self.__serverSocket is None:
            raise TypeError()
            return None
        messageSize, messageEncoding = self.__serverMessager.nextMessageFormat()
        recievedMessage = self.__serverSocket.recv(messageSize).decode(messageEncoding)
        print(recievedMessage)
        return self.__serverMessager.recv(recievedMessage, messageEncoding)
    
    
        

def startServer(port : int = 5050):
    startTime = time.time()
    listeningServer = ListeningServer(port, 5)
    
    server = None
    try:
        while time.time() < startTime+30:
            communicationSocket, clientInfo = listeningServer.getSocket()
            while True:
                server = HostingServer(communicationSocket, clientInfo)
                server.recv()
            
            
    except KeyboardInterrupt:
        print("server has been forced shutdown")
    finally:
        try:
            del server
        except:
            print("socket was never opened")
        del listeningServer

startServer()