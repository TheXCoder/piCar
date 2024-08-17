# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:15:18 2024

@author: Phatty
"""
from __future__ import annotations
import json, sys
from typing import Callable, Annotated

#--------------------------Annotations of variables
messageQueInformation = Annotated[list, """
                                  message que is a list inside the list
                                  there are dictionaries with the following keys:
                                     "command": name of command
                                     "ID" : The unique identifier of the command
                                         (multiple commands with the same name can different identifiers)
                                     "data" : data that is used with the command
                                  """]
commandIDsInformation = Annotated[dict, """
                                  command IDs has the following keys:
                                     [int], the id number as an integer, no two commands can have same ID
                                         inside the ID key:
                                             "command" : name of command
                                             "data" : data that is used with the command
                                              
                                  """]

messageRecievedDataInformation = Annotated[dict,"""
                                           message recieved data has the following keys:
                                              [int], the ID number as an integer
                                                  inside the ID key:
                                                      "hasAccepted" : True/False, true if command was recieved 
                                                          with an accepted command, false if decline command
                                                      "command" : the name of the command
                                                      "data" : the data the was recieved
                                           """]
                                          
#-----------------------------------------------------------------------------------------------------------------

class MyMessage:
    """class to simply sending messages between devices"""
    __ENCODINGMESSAGESIZE = 20
    __ENCODINGMESSAGEENCODING = "utf-8"
    def __init__(self, eventsDictionary : dict = {}):
        """
        Class to handle messaging between devices

        Parameters
        ----------
        eventsDictionary : {str, func(data)-> bool | data}, optional
            creates a dictionary of events. The default is {}.

        Returns
        -------
        object
            creates instance of MyMessage

        """
        #message que is a list 
        #inside the list there are dictionaries with the following keys:
        #   "command": name of command
        #   "ID" : The unique identifier of the command
        #       (multiple commands with the same name can different identifiers)
        #   "data" : data that is used with the command
        self.__messageQue : messageQueInformation = []
        #command IDs has the following keys:
        #   [int], the id number as an integer, no two commands can have same ID
        #       inside the ID key:
        #           "command" : name of command
        #           "data" : data that is used with the command
        #               
        self.__commandIDs : dict = {}
        #message recieved data has the following keys:
        #   [int], the ID number as an integer
        #       inside the ID key:
        #           "hasAccepted" : True/False, true if command was recieved 
        #               with an accepted command, false if decline command
        #           "command" : the name of the command
        #           "data" : the data the was recieved
        self.__messageRecvData : messageRecievedDataInformation = {} #data received by the return of a command (accept and decline)

        #message handling
        #event dictionary uses the command as a key and the function activated by the command as a value
        #ex: {"kill":killFunction}
        self.__eventsDictionary : {str:Callable[[object],[bool,object]]} = eventsDictionary
        self.__currentMessageSize : int = 0
        self.__currentMessageEncoding : str = ""
#----------queing-------------------------------------------
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
    def __addToQue(self, newMessage : str, encoding : str = "utf-8"):
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
            self.__addToQue(encodingMessage, "utf-8") # repeats encoding process until encoding message is proper size
            self.__messageQue.append((newMessage, encoding))
            return None
        self.__messageQue.append((encodingMessage,"utf-8"))
        self.__messageQue.append((newMessage, encoding))
        return None
    
#-------object Modification methods-----------------------------------------------------

        #add a new command command event list
    def addcommand(self, command : str, eventFunction : Callable[[object],[bool,object]])-> bool:
        """
        binds event function to command and adds that to
        the event dictionary

        Parameters
        ----------
        command : str
            command to respond to
            
        eventFunction : func(object) -> (bool, data)
            must be a valid function that has:
            1) one parameter that will be used to pass command data into
            2) return a bool value that determines if accept/decline (True/False) will be sent
            function can more than one value at a time, the rest will be packaged and sent in
            the accept/decline message as command data

        Returns
        -------
        bool
            returns True if function and command have been added to the events
        
        Additional Information
        ----------------------
        You may want to implement your own function to
        overide the builtin version for the recieving back the echo. 
        You can do this easily by using "rply" as the command parameter
        example: addCommand("rply", validFunction)

        """
        #add function to event list
        if not callable(eventFunction):
            error = TypeError("Event function is not callable. Read the doc string")
            raise error
            return False
        if command in self.__eventsDictionary.keys():
            error = KeyError("This command is already in use")
            raise error
            return False
        
        self.__eventsDictionary[command] = eventFunction
        return True
    
    #if clearAll is false. Only commands behind the next command in the que are deleted
    def clearQue(self, clearAll : bool = False):
        ...
#---------------builtin commands for handling messages---------------------------------------

                        #echo commands
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
        self.__addToQue(message, encoding)
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
        self.__addToQue(message, encoding)
        return None
    
                #decline and accepting messages
    def __acceptAndDecline(self, recvMessage : dict, data, hasAccepted : bool):
        """
        creates an acception or decline message with the added data

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
        command = "acct" if hasAccepted else "decl"
        #message has the following keys:
        #   "command":"acct" or "decl", acct for accept or decl for decline
        #   "ID : [int], the ID number as an integer
        #   "data" : data being sent
        #       inside the "data" key:
        #           "command" : the command of the recieved message
        #           "data" : the data being sent with the message
        message = {"command":command, "ID":recvMessage["ID"],
                   "data":{"command":recvMessage["command"], "data":data}}
        message = json.dumps(message)
        message = message.encode("utf-8")
        self.__addToQue(message, "utf-8")
        return None
    
#-----------------access recieved message data----------------------

    def getData(self, commandOrDictionary : str | dict, commandID : int = None):
        """
        

        Parameters
        ----------
        commandOrDictionary : str | dict
            can be the name of the command or the dictionary the recieve method
        commandID : int, optional
            ID of command. If using the dictionary from the recieve method
            please leve blank

        Returns
        -------
        bool
            if the command had been accepted by the reciever
            this will be true
            if the command had been declined by the reciever
            this will be false
        data
            data sent by the reciever

        """
        #message recieved data has the following keys:
        #   [int], the ID number as an integer
        #       inside the ID key:
        #           "hasAccepted" : True/False, true if command was recieved 
        #               with an accepted command, false if decline command
        #           "command" : the name of the command
        #           "data" : the data the was recieved
        if commandID is None and isinstance(commandOrDictionary, dict):
            recievedInformation = self.__messageRecvData[commandOrDictionary["ID"]]
            if recievedInformation["command"] != commandOrDictionary["command"]:
                return None
            return recievedInformation["hasAccept"], recievedInformation["data"]

#------------create and send messages-------------------------------------------
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
        self.__addToQue(message, encoding)

    def nextMessage(self) -> tuple:
        """
        creates a generator object for accessing the que of messages

        Yields
        ------
        tuple(str, str)
            message, message encoding.
            the message should be recieved by another instance
            of this class for communication

        """
        while True:
            try:
                messageWithEncoding = self.__messageQue.pop(0)
                yield messageWithEncoding
            except IndexError:
                return None,None
            
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
#---------receive messages------------------------------------------------------------
    def __getFormatMessage(self, messageRecieved:str, encoding : str) -> dict | bool:
        """
        modifies the message size and format
        to match the recieved message

        Parameters
        ----------
        messageRecieved : str
            message in json format.
        encoding : str
            encoding of message

        Returns
        -------
        dict or bool
            returns false if message is not a format message
            returns a dictionary {"command":None,"ID":None} if message
            is a format message

        """
        if messageRecieved[0:4] == "size":
            endSize : int = messageRecieved.find("code")
            endEncoding : int = messageRecieved.find(";")
            self.__currentMessageSize = int(messageRecieved[4:endSize])
            self.__currentMessageEncoding = messageRecieved[endSize+4:endEncoding]
            return {"command": None, "ID":None}
        elif messageRecieved[0:4] == "lmf ":
            endSize : int = messageRecieved.find("code")
            endEncoding : int = messageRecieved.find(";")
            self.__currentMessageSize = int(messageRecieved[8:endSize])
            self.__currentMessageEncoding = messageRecieved[endSize+4:endEncoding]
            return {"command": None, "ID":None}
        return False
    
    def __getEchoMessage(self, recvMessage : dict, encoding : str) -> dict:
        """
        handles an echo command by adding a reply message to que

        Parameters
        ----------
        recvMessage : dict
            recieved message as a dictionary
        encoding : str
            encoding of the recieved message

        Returns
        -------
        dict
            returns a dictionary {"command":None,"ID":None}

        """
        self.__returnEcho(recvMessage, encoding)
        self.__currentMessageSize = 0
        self.__currentMessageEncoding = ""
        return {"command" : None, "ID":None}
            
    def __getEchoReplyMessage(self, recvMessage : dict, encoding : str) -> dict:
        """
        handles a reply command from echo
                

        Parameters
        ----------
        recvMessage : dict
            recieved message as a dictionary
        encoding : str
            encoding of recieved message

        Returns
        -------
        dict
            returns a dictionary {"command":"rply", "ID":None}

        """
        if "rply" in self.__eventsDictionary.keys():
            hasAccepted, data =self.__eventsDictionary["rply"](recvMessage["data"])
            if hasAccepted:
                print(data)
            else:
                print('\n')
        else:
            ...
        return {"command":"rply", "ID":None}
    
    def __getAcceptDeclineMessage(self, recvMessage : dict, encoding : str, isAccepted : bool) -> dict:
        """
        handles accept and Decline messages and stores their data to be accessed later
        
        
        Parameters
        ----------
        recvMessage : dict
            recieved message as a dictionary
        encoding : str
            encoding as recieved message
        isAccepted : bool
            This will be True if recieved message is an accepted message.
            False if recieved message is an decline message.

        Returns
        -------
        dict
            returns dictionary {"command":command as str, "ID" : ID as int}
            the information in the dictionary can be used to access
            the stored data from the message

        """
        commandID = recvMessage["ID"]
        commandAndData = self.__commandIDs[commandID]
        recvCommand = recvMessage["data"]["command"]
        if commandAndData["command"] != recvCommand:
            ...
        self.__messageRecvData[commandID] = {"hasAccepted": isAccepted, 
                                             "command":commandAndData["command"],
                                             "data" : recvMessage["data"]["data"]}
        return {"command" : commandAndData["command"], "ID" : commandID}
    
    def __getCommandMessage(self, recvMessage : dict, encoding : str) -> dict:
        """
        handles recieved message and passes the message information to
        the functions specified in event dictionary

        Parameters
        ----------
        recvMessage : dict
            recieved message as a dictionary
        encoding : str
            encoding of recieved message

        Returns
        -------
        dict
            returns a dictionary {"command":None, "ID":None}
            
        Additional Information
        ----------------------
        Just so we are clear!
        eventFunction : func(object) -> (bool, data)
            must be a valid function that has:\n\t\t
            1) one parameter that will be used to pass command data into \n\t\t
            2) return a bool value that determines if accept/decline (True/False) will be sent \n
            function can more than one value at a time, the rest will be packaged and sent in \n
            the accept/decline message as command data

        """
        function = self.__eventsDictionary[recvMessage["command"]]
        functionReturns = function(recvMessage["data"])
        isAccepted, *functionData = functionReturns
        if not isinstance(isAccepted, bool):
            error = "Function \"" + str(type(function)) + "\" bounded to command \""
            error += recvMessage["command"] + "\" does not return a bool value"
            return {"command":None, "ID":None}
        
        self.__acceptAndDecline(recvMessage, functionData, isAccepted)
        return {"command":None, "ID":None}
        
        
    
    def recv(self, messageRecieved:str, encoding = "utf-8") -> dict:
        """
        the recieve method
        recieves messages sent by other instances of this class

        Parameters
        ----------
        messageRecieved : str
            message should be from another instance of this class
            message should also be in json or formating format
        encoding : TYPE, optional
            DESCRIPTION. The default is "utf-8".

        Returns
        -------
        dict
            If the recieved message is a valid accept or decline message
            that was sent to respond to this instance of the class's message 
            The method will return dictionary:
            {"command":command, "ID":ID}. Please use this to
            access the data from the message by using the method getData(dict|str, int)

        """
        returnValue = self.__getFormatMessage(messageRecieved, encoding)
        if isinstance(returnValue, dict):
            return returnValue
        
        recvMessage : dict = json.loads(messageRecieved)
        if recvMessage["command"] == "echo":
            returnValue = self.__getEchoMessage(recvMessage, encoding)
        elif recvMessage["command"] == "rply":
            returnValue = self.__getEchoReplyMessage(recvMessage, encoding)
        
        elif recvMessage["command"] == "acct":
            returnValue = self.__getAcceptDeclineMessage(recvMessage, encoding, True)
        elif recvMessage["command"] == "decl":
            returnValue = self.__getAcceptDeclineMessage(recvMessage, encoding, False)
        elif recvMessage["command"] in self.__eventsDictionary.keys():
            returnValue = self.__getCommandMessage(recvMessage, encoding)
        self.__currentMessageSize = 0
        self.__currentMessageEncoding = ""
        return returnValue
             
                
            

    

def recvEcho(data : object):
    print("recieved echo", data)
    return True, None
    
if __name__ == "__main__":
    raise NotImplementedError("This is a module, and thus should not be ran as a script")
    
    