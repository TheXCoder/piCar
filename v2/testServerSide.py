# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:24:48 2024

@author: Phatty
"""
from MyMessage import *
import time, socket

def getServerInfo():
    return {"hostname" : socket.gethostname(), "hostIP" : socket.gethostbyname(socket.gethostname())}

def startServer(port : int = 5050):
    serverInfo = getServerInfo()
    serverBeginingTime = time.time()
    
    serverMessager=MyMessage()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((serverInfo["hostIP"],port))
    server.listen(5)
    communication_socket = None
    try:
        for i in range(5):
            communication_socket, clientAddress = server.accept()
            clientname = socket.gethostbyaddr(clientAddress[0])
            print(f"{clientname} @ {clientAddress} connected")
            nextMessageSize, nextMessageEncoding = serverMessager.nextMessageFormat()
            recvMessage = communication_socket.recv(nextMessageSize).decode(nextMessageEncoding)
            print(f"recvMessage is {recvMessage}")
            communication_socket.close()
            
    except KeyboardInterrupt:
        print("server has been forced shutdown")
    finally:
        try:
            communication_socket.close()
        except:
            print("socket was never opened")
        server.close()
        
startServer()