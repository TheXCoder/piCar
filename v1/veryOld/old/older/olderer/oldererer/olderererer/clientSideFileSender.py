#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 10:44:39 2024

@author: goduser
"""
import socket, time, tkinter.filedialog as fileGUI

def getUserFiles()->str:
    fileList = fileGUI.askopenfiles(filetypes = [("Program Files", ".py .c .cpp .h"), 
                                                 ("python files", ".py"), 
                                                 ("C Files", ".c .cpp .h")])
    for filePath in fileList:
        yield filePath.name

def openFileByLine(filepath:str):
    with open(filepath, 'rb') as file:
        line = file.readline()
        while line:
            yield line
            line = file.readline()
def findLocalHost(serverName:str, numberIntervals : int = 5, intervalWaitTime : float = 1)->str:
    serverIP : str= None
    for _ in range(numberIntervals):
        if _ == numberIntervals -1:
            print("Last try before giving up")
        try:
            serverIP = socket.gethostbyname(serverName + '.local')
            print(f"{serverName} has been found at {serverIP}")
            return serverIP
            
        except socket.gaierror:
            print(f"{serverName} has not been found. Waiting {intervalWaitTime} seconds before retrying.")
            time.sleep(intervalWaitTime)
    return serverIP

def getConnected(serverIP : str, port : int, clientsocket, numberIntervals : int = 5, intervalWaitTime : float = 1):
    for _ in range(numberIntervals):
        if _ == numberIntervals -1:
            print("Last try before giving up")
        else:
            print("Server has refused to connect. Trying again")
        try:
            connectedToServer = clientsocket.connect((serverIP,5050))
            print("Connected to server")
            return connectedToServer
        except ConnectionRefusedError:
            time.sleep(intervalWaitTime)
            
    print("System has failed to connect with the server.")
    return None


def startClient():
    filename = "fileReaderClient.py"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverIP = findLocalHost("TacomaPi",intervalWaitTime=0.5)
    if serverIP == None:
        return None
    toServer = getConnected(serverIP, 5050, client)
    if toServer == None:
        return None
    toServer.send(filename)
    while True:
        for line in openFileByLine(filename):
            toServer.send(str(len(line)).format('utf-8'))
            toServer.send(line.format('utf-8'))
        toServer.send("etrn:".format('utf-8'))
        break
    
            

def startServer():
    hostIP : str = socket.gethostname()
    hostname = socket.gethostbyname(hostIP)
    port : int = 5050
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((hostIP,port))
    server.listen(1)
    communication_socket, clientAddress = server.accept()
    #make intp method
    lientName = socket.gethostbyaddr(clientAddress) #fix connects only once
    print(f"{clientName} @ {clientAddress} connected")
    with open(communication_socket.listen(512), 'wb+') as newFile:
        while True:
            clientMessage = communication_socket.listen(512)
            if clientMessage.find("etrn:") == 0:
                break
            try:
                value = int(clientMessage)
                clientMessage = communication_socket.listen(value)
                newFile.write(clientMessage)
            except ValueError:
                newFile.write(clientMessage)
    communication_socket.close()
        
        
        

def main():
    startClient()
    
    
    
    

if __name__ == '__main__':
    main()