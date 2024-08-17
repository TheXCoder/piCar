# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 17:47:27 2024

@author: Phatty
"""
import json

#this class works by sending an encoding message every other message
#this allows for messages to be dynamically resized
class MyMessage:
    __ENCODINGMESSAGESIZE = 20
    __ENCODINGMESSAGEENCODING = "utf-8"
    def __init__(self, eventsDictionary : dict = {}):
        #event dictionary uses the command as a key and the function activated by the command as a value
        #ex: {"kill":killFunction}
        self.__messageQue : list = []
        self.__commandIDs : dict = {}

        #message handling
        self.__eventsDictionary : dict = eventsDictionary
        self.__currentMessageSize : int = 0
        self.__currentMessageEncoding : str = ""

#------Message and command queing methods-------
    def __getNewID(self, command : str, data) -> int:
        """
        gives command new idea and adds it to the command id dictionary

        Parameters
        ----------
        command : str
            name of command
        data : TYPE
            command data

        Returns
        -------
        int
            a fresh ID with along with adding the command to the dictionary

        """
        newID : int = 0
        while newID in self.__commandIDs.keys():
            newID +=1
        self.__commandIDs[newID]={"command" : command, "data" : data}
        return newID
        

    #adds message plus its encoding message to que
    #always returns none
    def __generateQue(self, newMessage : str, encoding : str) -> None:
        """
        generates a format message based off of the newMessage
        adds the format message to que, then adds the newMessage

        Parameters
        ----------
        newMessage : str
            uses either a basic message
            or a message formated by json
        encoding : str
            the encoding of the message
            ex "utf-8"

        Returns
        -------
        None
            method will never return anything

        """
        messageSize = len(newMessage)
        encodingMessage = "size" + str(messageSize) + "code" + encoding +";" #creates encoding message
        if len(encodingMessage) > self.__ENCODINGMESSAGESIZE: # if encoding message is to big to fit in normal encoding size 
            print("Test")
            encodingMessage = encodingMessage.replace("size", "lmf size") # replace normal encoding with large message format encoding
            self.__generateQue(encodingMessage, "utf-8") # repeats encoding process until encoding message is proper size
            self.__messageQue.append((newMessage, encoding))
            return None
        self.__messageQue.append((encodingMessage,"utf-8"))
        self.__messageQue.append((newMessage, encoding))
        return None
#------------------------------------------------------------
    def nextMessageFormat(self) -> (int,str):
        """
        gets the size and encoding of the message to be recieved
        use this along with the recieve command to get a properly formated
        message/command

        Returns
        -------
        (int,str)
            size of next message, encoding of next message

        """
        messageSize : int = self.__ENCODINGMESSAGESIZE if self.__currentMessageSize == 0 else self.__currentMessageSize
        messageCode : str = self.__ENCODINGMESSAGEENCODING if self.__currentMessageEncoding == "" else self.__currentMessageEncoding
        return messageSize, messageCode

    #add a new command command event list
    def addCommandAndEvent(self, command : str, eventFunction)-> bool:
        """
        pairs command and event and 
        adds them to the event dictionary

        Parameters
        ----------
        command : str
            name of command
        eventFunction : TYPE
            must be a valid function that has:
            1) one parameter that will be used to pass command data into
            2) return a bool value that determines if accept/decline (True/False) will be sent
            function can more than one value at a time, the rest will be packaged and sent in
            the accept/decline message as command data

        Returns
        -------
        bool
            will return true if command has been added to dictionary

        """
        #add function to event list
        if command in self.__eventsDictionary.keys():
            return False
        self.__eventsDictionary.update({command, eventFunction})
        return True

#-----------Hard coded commands-----------------------
    #echo is the only command hardcoded into class because it is special and will never change :-)
    def echo(self, messageToEcho : str, encoding : str = "utf-8")-> None:
        """
        Sends a message that will be recieved and parroted back.

        Parameters
        ----------
        messageToEcho : str
            message to be parroted
        encoding : str, optional
            The encoding of the message. The default is "utf-8".
            
        Returns
        -------
        None
            The method will never return anything

        """
        message = {"command":"echo", "data":str(messageToEcho)}
        message = json.dumps(message)
        message = message.encode(encoding)
        #echo does not get an idea because it is special
        #echo is not dependent on a message back from sender
        self.__generateQue(message, encoding)
        return None

    def __returnEcho(self, recvMessage : dict, encoding : str = "utf-8") -> None:
        """
        sends message back to send

        Parameters
        ----------
        recvMessage : dict
            recieved message in dictionary format
        encoding : str, optional
            encoding that the message was recieved in
            The default is "utf-8".

        Returns
        -------
        None
            method will NEVER return anything

        """
        #return echo echo
        message = {"command":"rply", "data":str(recvMessage["data"])}
        message = json.dumps(message)
        message = message.encode(encoding)
        self.__generateQue(message, encoding)
        return None

    def __accept(self, recvMessage : dict, data):
        """
        sends a acception message
        with added data

        Parameters
        ----------
        recvMessage : dict
            message recieved in dictionary form
        data : TYPE
            data to be sent to be sent with the accept command
            
        Returns
        -------
        None.
            I need to get something off my chest,
            This method will NEVER ever ever return anything

        """
        message = {"command":"acct", "ID":recvMessage["ID"], "data":data}
        message = json.dumps(message)
        message = message.encode("utf-8")
        self.__generateQue(message, "utf-8")
        return None
    
                            
    def __decline(self, recvMessage : dict, data) -> None:
        """
        sends a declining message
        with added data

        Parameters
        ----------
        recvMessage : dict
            message recieved in dictionary form
            
        data : TYPE
            data to be sent to be sent with the decline command

        Returns
        -------
        None
            I know you won't see this, but this function won't ever return anything

        """
        message = {"command":"decl", "ID":recvMessage["ID"], "data":data}
        message = json.dumps(message)
        message = message.encode("utf-8")
        self.__generateQue(message, "utf-8")
        return None

#------------Message in/out-------------------------------------------
    def command(self, command : str, data , encoding : str = "utf-8")-> None:
        """
        creates a message with the command and date

        Parameters
        ----------
        command : str
            name of command
        data : TYPE
            any data used by command
        encoding : str, optional
            encoding of message. The default is "utf-8".

        Returns
        -------
        None
            You will get None and be happy! >:-O

        """
        if command == "echo":
            self.echo(data, encoding)
            return None
        commandID = self.__getNewID(command, data)
        message = {"command":command, "ID":commandID, "data":data}
        message = json.dumps(message)
        message.encode(encoding)
        self.__generateQue(message, encoding)

    def nextMessage(self) -> tuple:
        while True:
            try:
                messageWithEncoding = self.__messageQue.pop(0)
                yield messageWithEncoding
            except IndexError:
                return None,None

    #message in json format or in simple message format
    def recv(self, messageRecieved:str, encoding = "utf-8"):
        """
        

        Parameters
        ----------
        messageRecieved : str
            DESCRIPTION.
        encoding : TYPE, optional
            DESCRIPTION. The default is "utf-8".

        Raises
        ------
        TypeError
            when function linked to the command
            does not output the correct 

        Returns
        -------
        bool
            DESCRIPTION.
        returnValues : TYPE
            DESCRIPTION.

        """
        if messageRecieved[0:4] == "size":
            endSize : int = messageRecieved.find("code")
            endEncoding : int = messageRecieved.find(";")
            self.__currentMessageSize = int(messageRecieved[4:endSize])
            self.__currentMessageEncoding = messageRecieved[endSize+4:endEncoding]
            return None
        elif messageRecieved[0:4] == "lmf ":
            endSize : int = messageRecieved.find("code")
            endEncoding : int = messageRecieved.find(";")
            self.__currentMessageSize = int(messageRecieved[8:endSize])
            self.__currentMessageEncoding = messageRecieved[endSize+4:endEncoding]
            return None

        recvMessage : dict = json.loads(messageRecieved)
        if recvMessage["command"] == "echo":
            self.__returnEcho(recvMessage, encoding)
            self.__currentMessageSize = 0
            self.__currentMessageEncoding = ""
            return None
            
        elif recvMessage["command"] == "acct":
            command = self.__commandIDs[recvMessage["ID"]]
            del self.__commandIDs[recvMessage["ID"]]
            returnValues = {"command":command, "ID":recvMessage["ID"], "data":recvMessage["data"]}
            self.__currentMessageSize = 0
            self.__currentMessageEncoding = ""
            return True, returnValues
            
        elif recvMessage["command"] == "decl":
            command = self.__commandIDs[recvMessage["ID"]]
            del self.__commandIDs[recvMessage["ID"]]
            returnValues = {"command":command,"ID":recvMessage["ID"], "data":recvMessage["data"]}
            self.__currentMessageSize = 0
            self.__currentMessageEncoding = ""
            return False, returnValues
            
        elif recvMessage["command"] in self.__eventsDictionary.keys():
            #functions must return a  true or false apon completion
            #functions that return false will cause the instance to create a decline message
            #functions that return true will cause the instance to create an accept message
            #function must have single parameter to pass in data
            hasAccept : bool = None
            functionData = self.__eventsDictionary[recvMessage["command"]](recvMessage["data"])
            self.__currentMessageSize = 0
            self.__currentMessageEncoding = ""
            if isinstance(functionData, bool):
                hasAccept = functionData
                functionData = None
            else:
                hasAccept, *functionData = functionData
            
            if not isinstance(hasAccept, bool):
                    raise TypeError(
                    "First value of a function command must be a boolean determined by whether or not the said function has accept the recieved message"
                    )
            try:
                functionData = tuple(functionData)
            except TypeError:
                pass
            if hasAccept:
                self.__accept(recvMessage, functionData)
                return None
            self.__decline(recvMessage, functionData)
            return None
            
        self.__decline(recvMessage, "not a command")
        self.__currentMessageSize = 0
        self.__currentMessageEncoding = ""
        return None