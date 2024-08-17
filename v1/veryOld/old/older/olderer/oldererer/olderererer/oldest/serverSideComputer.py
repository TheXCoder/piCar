#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 15:23:18 2024

@author: goduser
"""
import socket, Communication, time

def timeoutConnection(startTime):
    if time.time() - startTime > 300:
        return True
    return False


def startServer():
    hostname : str = socket.gethostname()
    hostIP : str = socket.gethostbyname(hostname)
    port = 5050
    serverBeginingTime = time.time()
    
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((hostIP,port))
    server.listen(5)
    
    
    while not timeoutConnection(serverBeginingTime):
        communication_socket, clientAddress = server.accept()
        clientname = socket.gethostbyaddr(clientAddress)[0]
        print(f"{clientname} @ {clientAddress} connected")
        serverMessager = Communication.Message()
        server.send(serverMessager.generateMessage(f"Hello {clientname}!"))
        server.send(serverMessager.generateMessage("Please send me program files"))
    server.close()
    


def main():
    print("This is a test server")
    startServer()
if __name__ == '__main__':
    main()

