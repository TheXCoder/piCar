#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 23:37:25 2024

@author: goduser
"""
import fileReader, Communication, myThread
import threading, time, socket


def getFilesFromUser():
    files = [file for file in fileReader.getUserFiles()]
    return files

def startClient():
    clientMessager = Communication.Message()
    findServerThread = threading.Thread(target=findLocalHost, args=("TacomaPi", 20, 0.25))
    findServerThread.start()
    tmp = fileReader.getUserFiles()
    try:
        fileDirectory = next(tmp)
    except StopIteration:
        findServerThread.join()
        print("File fallback error")
        return None;
    serverIP = findServerThread.join()
    if serverIP == None:
        print("Server IP fallback error")
        return None
    
    toServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(toServerSocket.connect(serverIP, 5050))
    print(toServerSocket.recv(clientMessager.getMessageSize()).format(clientMessager.getMessageEncoding()))
    print(toServerSocket.recv(clientMessager.getMessageSize()).format(clientMessager.getMessageEncoding()))
    for fileDirectory in tmp:
        pass
    toServerSocket.send(clientMessager.generateClosingMessage())
    
    
        
def main():
    startClient()
if __name__ == '__main__':
    main()