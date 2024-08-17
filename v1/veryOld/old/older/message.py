#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 19:02:29 2024

@author: goduser
"""

import json, fileReader

class MyMessage:
    __minimumMessageSize = 50
    def __init__(self, deviceName:str, messageSize:int=255, messageEncoding:str = 'utf-8'):
        self.__deviceName = deviceName
        self.__messageSize:int = messageSize
        self.__encoding:str = messageEncoding
        self.__commandLock = {"commandLock":None, "deviceLock" : None}
        self.__tmp:dict = {} #information about the commands
        
    
    def __returnEcho__(self, messageRecieved:dict):
        message = {"deviceName":self.__deviceName,"command":"note", 
                   "data":messageRecieved['data']}
        message = json.dumps(message)
        return message, self.__encoding
    
    #handles acknowledgement/acception messages
    def __handleAccept__(self, messageRecieved:dict):
        if messageRecieved["data"] == "prot":
            self.__tmp.update({"oldMessageSize":self.__messageSize})
            self.__tmp.update({"oldEncoding":self.__encoding})
            self.__messageSize = self.__tmp["newMessageSize"]
            self.__encoding = self.__tmp["newEncoding"]
            del self.__tmp["newMessageSize"]
            del self.__tmp["newEncoding"]
            
            message = {"deviceName":self.__deviceName, "command":"note", 
                       "data":"changed protocol"}
            message = json.dumps(message)
            if len(message) > self.__messageSize:
                return None, None
            return message, self.__encoding
        
            
        
    def __setProtocal__(self, messageSize : int, messageEncoding : str):
        """
        Do not use
        Internally sets the messaging protocal
        to the new protocal

        Parameters
        ----------
        messageSize : int
            message size of new protocal.
        messageEncoding : str
            encodinng of new protocal.

        Returns
        -------
        message : str, None
            returns an acknowledgment message
            
        str, None
            DESCRIPTION.

        """
        message = {"deviceName": self.__deviceName,
                   "command" : "acct", "data":"prot"}
        self.__tmp.update({"oldMessageSize":self.__messageSize})
        self.__tmp.update({"oldEncoding":self.__encoding})
        self.__messageSize = messageSize
        self.__encoding = messageEncoding
        message = json.dumps(message)
        if len(message) > self.__tmp["oldMessageSize"]:
            return None, None
        return message, self.__tmp['oldEncoding']
    
    def __writeFile__(self, message):
        pass
    def __readFile__(self, message):
        pass
    def echo(self, message):
        """
        Sends a message to a reciever
        The reciever sends back a copy of the message
        Parameters
        ----------
        message : TYPE
            String to be echoed

        Returns
        -------
        message : TYPE
            DESCRIPTION.
        TYPE
            DESCRIPTION.

        """
        if self.__commandLock["commandLock"] == None:
            message = {"deviceName":self.__deviceName,
                       "command":"echo", "data":message}
            message = json.dumps(message)
            if len(message) > self.__messageSize:
                return None, None
            return message, self.__encoding
        return None, None
        
    def newProtocal(self, messageSize:int, messageEncoding:str):
        message = {"deviceName":self.__deviceName,"command" : "prot",
                   'size':messageSize, 'code':messageEncoding}
        self.__tmp.update({"currentCommand":"prot"})
        message = json.dumps(message)
        if len(message) > self.__messageSize:
            return None, None
        self.__tmp.update({"newMessageSize":messageSize})
        self.__tmp.update({"newEncoding":messageEncoding})
        return message, self.__encoding
            
    
    def recvMessage(self, messageRecieved):
        messageRecieved = json.loads(messageRecieved)
        if self.__commandLock["commandLock"] == None:
            #handles protocol messages
            if messageRecieved["command"] == 'prot':
                return self.__setProtocal__(messageRecieved['size'], 
                                            messageRecieved['code'])
                
            # handles echo
            if messageRecieved["command"] == 'echo':
                return self.__returnEcho__(messageRecieved)
            
            # handles acct or accept
            if messageRecieved["command"] == "acct":
                return self.__handleAccept__(messageRecieved)
            
            # handles notices
            if messageRecieved["command"] == "note":
                print(f"\n{messageRecieved['data']}")
                return None, None
    
    def getStatus(self):
        if self.__commandLock["commandLock"] == None:
            return {"deviceName":self.__deviceName,
                    "messageSize":self.__messageSize, 
                    "encoding":self.__encoding}
        return {"deviceName":self.__deviceName,
                self.__commandLock["commadLock"]
                "messageSize":self.__messageSize, 
                "encoding":self.__encoding}
    
    def recvFile(self, filepath:str):
        message = {"command":"file","mode":"recv","data":None,"end":None}
        message = json.dumps(message)
        if len(message) > self.__messageSize:
            return None, None
        return message, self.__encoding
    
    def sendFile(self, filepath:str):
        self.__commandLock["commandLock"] = "sendFile"
        self
        
        
        
if __name__ == '__main__':
    test = MyMessage("Device 1")
    test2 = MyMessage("Device 2")
    message, encoding = test.newProtocal(600, 'utf-16')
    print(message.encode(encoding))
    message, encoding = test2.recvMessage(message)
    message, encoding = test.recvMessage(message)
    message, encoding = test2.recvMessage(message)