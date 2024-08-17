#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 10:12:49 2024

@author: goduser
"""
from math import ceil as m_ceil
def getBytesNeeded(n : int) -> int:
    if isinstance(n, int):
        if not n:
            return 1
        return m_ceil(n.bit_length()/8)
    raise TypeError("variable must be an integer only")
    return None

class MySocketMessage:
    def __init__(self, messageSize : int = 255, encoding : str = "utf-8"):
        self.__messageSize = messageSize
        self.__encoding = encoding
        self.__tmpStorage : dict = {"currentCommand" :None} #locks message object so no other message can be run until message is completed
    
    def __setProtocal__(self, message : str):
        
        if message.find('size=') > -1:
            sizeLocation = (message.find('size=')+5,
                         message.find(';',message.find('size=')))
            newMessageSizeBytes = message[sizeLocation[0]:
                                                sizeLocation[1]]
            print(newMessageSizeBytes)
            newMessageSizeBytes = bytes(newMessageSizeBytes.encode(self.__encoding))
            self.__messageSize.from_bytes(newMessageSizeBytes, 'big')
        if message.find('code=') > -1:
            encodingLocation = (message.find('code=')+5,
                         message.find(';',message.find('code=')))
            self.__encoding = message[encodingLocation[0], encodingLocation[1]]
        
        return ("acct".format(self.__encoding), self.__encoding)
             
    def getMessageSize(self) -> int:
        return self.__messageSize
    def getEncoding(self) -> str:
        return self.__encoding
    
    def sendEcho(self, messageToEcho):
        if self.__tmpStorage["currentCommand"] == None:
            message = ("echo: " + str(messageToEcho)).format(self.__encoding)
            if len(message) > self.__messageSize:
                return None
            return (message, self.__encoding)
        return None
    
    def setNewProtocal(self, messageSize : int, encoding : str) -> str:
        if self.__tmpStorage["currentCommand"] != None: #no other command is currently running
            return None
        
        message = "prot:size="
        messageSizeAsBytes= messageSize.to_bytes(getBytesNeeded(messageSize), 'big')
        message += str(messageSizeAsBytes) + ';'
        message += "code:" + encoding
        message.encode(self.__encoding)
        if len(message) > self.__messageSize:
            self.__tmpStorage.update({"newMessageSize": None})
            self.__tmpStorage.update({"newEncoding": None})
            return None
        self.__tmpStorage.update({'newMessageSize':messageSize})
        self.__tmpStorage.update({"newEncoding":encoding})
        self.__tmpStorage.update({"currentCommand":"prot"})
        return (message,self.__encoding)
    
    def resvMessage(self, message):
        if message[0:4] == "prot":
            return self.__setProtocal__(message)
            
        elif message[0:4] == 'acct':
            if self.__tmpStorage['currentCommand'] == "prot":
                self.__messageSize = self.__tmpStorage['newMessageSize']
                self.__encoding = self.__tmpStorage['newEncoding']
                self.__tmpStorage['currentCommand'] = None
        elif message[0:4] == "decl":
            if self.__tmpStorage['currentCommand'] == "prot":
                self.__tmpStorge['currentCommand'] = None
                self.__tmpStorage['newMessageSize'] = None
                self.__tmpStorage['newEncoding'] = None
        elif message[0:4] == "echo":
            return (("note:" + message[4:]).format(self.__encoding),
                    self.__encoding)
        elif message[0:4] == "note":
            print(message)
        
        return (None, None)
                
            
            
        


if __name__ == '__main__':
    test = MySocketMessage()
    test2 = MySocketMessage()
    message = test.setNewProtocal(255*2, 'utf-16')
    message = test2.resvMessage(message[0])
    test.resvMessage(message[0])
    print(test.getEncoding())
    message = test.sendEcho("Hello World")
    message = test2.resvMessage(message[0])
    test.resvMessage(message)
    