#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 12:58:55 2024

@author: goduser
"""
import json
class MySocketMessage:
    __minimumMessageSize = 100
    def __init__(self, deviceName:str, messageSize:int=255, messageEncoding:str = 'utf-8'):
        self.__deviceName = deviceName
        self.__messageSize:int = messageSize if messageSize > self.__minimumMessageSize else self.__minimumMessageSize
        self.__encoding:str = messageEncoding
        self.__currentCommands = []
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
        if "prot" in self.__currentCommands:
            del self.__tmp["newMessageSize"]
            del self.__tmp["newEncoding"]
            self.__currentCommands.remove("prot")
            message = {"deviceName": self.__deviceName,
                       "command" : "decl", "data":"prot"}
            message = json.dumps(message)
            return message, self.__encoding
        message = {"deviceName": self.__deviceName,
                   "command" : "acct", "data":"prot"}
        self.__tmp["oldMessageSize"] = self.__messageSize
        self.__tmp["oldEncoding"] = self.__encoding
        self.__messageSize = messageSize
        self.__encoding = messageEncoding
        message = json.dumps(message)
        if len(message) > self.__tmp["oldMessageSize"]:
            return None, None
        return message, self.__tmp['oldEncoding']
    
    def __handleDecline__(self, messageRecieved):
        if messageRecieved["data"] == "prot":
            del self.__tmp["newMessageSize"]
            del self.__tmp["newEncoding"]
            self.__currentCommands.remove("prot")
            message = {"deviceName":self.__deviceName, "command":"note", 
                       "data":"protocol has failed to change"}
            message = json.dumps(message)
            return message, self.__encoding
        return None, None
            
            
    
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
    
    def newProtocal(self, messageSize : int, messageEncoding : str):
        if "prot" in self.__currentCommands:
            return None, None
        else:
            messageSize = messageSize if messageSize > self.__minimumMessageSize else self.__minimumMessageSize
            message = {"deviceName":self.__deviceName,"command" : "prot",
                   'size':messageSize, 'code':messageEncoding}
            message = json.dumps(message)
            if len(message) > self.__messageSize:
                return None, None
            self.__currentCommands.append("prot")
            self.__tmp["newMessageSize"] = messageSize
            self.__tmp["newEncoding"] = messageEncoding
            return message, self.__encoding
        
    def recvMessage(self, messageRecieved):
        messageRecieved = json.loads(messageRecieved)
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
        
        if messageRecieved["command"] == "decl":
            return self.__handleDecline__(messageRecieved)
        
        # handles notices
        if messageRecieved["command"] == "note":
            print(f"\n{messageRecieved['data']}")
            return None, None
    def getStatus(self):
        if self.__currentCommands == [] or self.__currentCommands == None:
            return {"deviceName":self.__deviceName,
                    "messageSize":self.__messageSize, 
                    "encoding":self.__encoding}
        
        return {"deviceName":self.__deviceName,
                "currentCommands":self.__currentCommands,
                "messageSize":self.__messageSize, 
                "encoding":self.__encoding}
if __name__ == "__main__":
    test = MySocketMessage("test")
    test2 = MySocketMessage("test2")
    message, encoding = test.newProtocal(165, "utf-8")
    message2, encoding = test2.newProtocal(297, "utf-16")
    message, encoding = test2.recvMessage(message)
    message, encoding = test.recvMessage(message)
    message, encoding = test2.recvMessage(message)
    message2, encoding = test.recvMessage(message2)
    print(message2) #weird behavior when seting new protocal still
            