#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 19:02:20 2024

@author: goduser
"""

import json

class MyMessage:
    __DEFAULTSIZE : int = 150
    __DEFAULTENCODING : str = "utf-8"
    def __init__(self, devicename : str, messageSize : int = 50, messageEncoding : str = "utf-8"):
        self.__devicename = devicename
        self.__messageSize : int = messageSize if messageSize > self.__DEFAULTSIZE else self.__DEFAULTSIZE
        self.__encoding : str = messageEncoding
        self.__tmp : dict = {}
        
        
        self.__messageQue : list(dict) = [] #the order to which message are created
        self.__messageIDs : dict(dict) = {}  #the id and data of messages 
        self.__usedIDs : list(int) = [] # which IDs are being used
    
    def __getNewID__(self, command : str, data):
        newID : int = 0
        while newID in self.__usedIDs:
            newID+=1
        
        self.__usedIDs.append(newID)
        self.__messageIDs[str(newID)]={"command" : command, "data" : data}
        return newID
    
    def __messageAccept__(self, recievedMessage : dict):
        if recievedMessage["data"]["command"] == "prot":
            return self.__finishProtocolSetup__(recievedMessage)
        supposedMessage : dict = self.__messageIDs[str(recievedMessage["ID"])]
        
    def __setProtocol__(self, recievedMessag : dict):
        for item in self.__messageIDs.items():
            if item["command"] == "prot":
                message : dict = {"devicename" : self.__devicename,
                                  "command" :"decl", 
                                  "ID" : recievedMessag["ID"],
                                  "data" : {"command" : "prot"}}
                self.__messageQue.append(message)
                return
            
        if (recievedMessag["data"])["messageSize"] < self.__DEFAULTSIZE:
            essage : dict = {"devicename" : self.__devicename,
                              "command" :"decl", 
                              "ID" : recievedMessag["ID"],
                              "data" : {"command" : "prot"}}
            self.__messageQue.append(message)
            return
        
        self.__tmp["oldSize"] = self.__messageSize
        self.__tmp["oldEncoding"] = self.__encoding
        message = {"devicename": self.__devicename, "command" : "acct",
                    "ID" : recievedMessag["ID"], "data" : {"command" : "prot"}}
        self.__messageQue.append(message)
        return
    
    def __finishProtocolSetup__(self, returnMessage : dict):
        pass
        
        
    
    def newProtocol(self, messageSize : int, messageEncoding : str) -> int:
        if messageSize < self.__DEFAULTSIZE:
            messageSize = self.__DEFAULTSIZE
        newID = self.__getNewID__("prot", {"messageSize" : messageSize,
                                           "encoding":messageEncoding})
        message = {"devicename" : self.__devicename, "command" : "prot",
                   "ID" : newID, 
                   "data" : {"messageSize" : messageSize, "encoding" : messageEncoding}}
        if len(json.dumps(message)) > messageSize:
            del self.__messageIDs[str(newID)]
            self.__usedIDs.remove(newID)
            return None
        self.__messageQue.append(message)
        return newID
        
    
    def echo(self, textToEcho : str, textEncoding : str = None) -> int:
        newID = self.__getNewID__("echo", textToEcho)
        message = {"devicename" : self.__devicename, "command" : "echo",
                   "ID" : newID, "data" : textToEcho}
        protocolRequirement : dict = {} # does the protocal need to be changed in order to send this message
        if len(json.dumps(message)) > self.__messageSize:
            protocolRequirement["messageSize"] = len(json.dumps(message))
            protocolRequirement["encoding"] = self.__encoding
        if textEncoding is not None:
            protocolRequirement[textEncoding]
            if "messageSize" not in protocolRequirement:
                protocolRequirement["messageSize"] = self.__messageSize
        
        if len(protocolRequirement) != 0:
            self.newProtocol(protocolRequirement["messageSize"],
                             protocolRequirement["encoding"])
        self.__messageQue.append(message)
        return newID
                
    
    def nextMessage(self):
        while True:
            try:
                message:dict =  self.__messageQue[0]
                del self.__messageQue[0]
                if message["command"] == "echo":
                    self.__usedIDs.remove(message["ID"])
                    del self.__messageIDs[str(message["ID"])]
                yield json.dumps(message), self.__encoding
            except IndexError as e:
                yield None, None
        
    def getNextMessage(self):
        try:
            message:dict =  self.__messageQue[0]
            del self.__messageQue[0]
            if message["command"] == "echo":
                self.__usedIDs.remove(message["ID"])
                del self.__messageIDs[str(message["ID"])]
            return json.dumps(message), self.__encoding
        except IndexError as e:
            return None, None
    
    def getMessage(self, messageID : int):
        pass
    
    def recvMessage(self, recievedMessage : str):
        if recievedMessage[0:4] == "rpad":
            self.__messageSize = self.__DEFAULTSIZE
            self.__encoding = self.__DEFAULTENCODING
            return "acct", encoding
        
        recievedMessage : dict = json.loads(recievedMessage)
        if recievedMessage["command"] == "prot":
            self.__setProtocol__(recievedMessage)
        
        if recievedMessage["command"] == "acct":
            

if __name__ == "__main__":
    test = MyMessage("test")
    test2 = MyMessage("test2")
    nextMessage = test.nextMessage()
    nextMessage2 = test2.nextMessage()
    next(nextMessage)
    print(test.newProtocol(90, "utf-16"))
    message, encoding = next(nextMessage)
    print(message)
    test2.recvMessage(message)
    message, encoding = next(nextMessage2)
    print(message)
    
    