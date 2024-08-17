# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 12:14:53 2024

@author: Phatty
"""
from __future__ import annotations
import json, copy, logging
from typing import Callable, Annotated

#--------------------------Annotations of variables
messageQueInformation = Annotated[list, """
                                  message que is a list 
                                  inside the list there are dictionaries with the following keys:
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
                                             "hasAccept" : True/False, true if command was recieved 
                                                 with an accepted command, false if decline command
                                                 This will start as None if no accept/decline message was recieved
                                             "replyData" : the data the was recieved from the 
                                                 accept/decline message for the command
                                                 This will start as None if no accept/decline message was recieved
                                             "messageSent" : True/False, true if message has been called using the
                                                 nextMessage() generator
                                                 
                                              
                                  """]
class MyMessage:
    """class to simply sending messages between devices"""
    _ENCODINGMESSAGESIZE = 20
    _ENCODINGMESSAGEENCODING = "utf-8"
    def __init__(self, eventsDictionary : dict = None):
        """
        Class to handle messaging between devices

        Parameters
        ----------
        eventsDictionary : {str, func(data)-> bool | data}, optional
            creates a dictionary of events. The default is None.
        Raises
        ------
        TypeError
            If fuunction in eventDictionaries is not callable
        
        Returns
        -------
        MyMessage
            creates instance of MyMessage

        """
        eventsDictionary = {} if eventsDictionary is None else eventsDictionary
        #message que is a list 
        #inside the list there are dictionaries with the following keys:
        #   "command": name of command
        #   "ID" : The unique identifier of the command
        #       (multiple commands with the same name can different identifiers)
        #   "data" : data that is used with the command
        self._messageQue : messageQueInformation = []
        #command IDs has the following keys:
        #   [int], the id number as an integer, no two commands can have same ID
        #       inside the ID key:
        #           "command" : name of command
        #           "data" : data that is used with the command
        #           "hasAccept" : True/False, true if command was recieved 
        #               with an accepted command, false if decline command
        #               This will start as None if no accept/decline message was recieved
        #           "replyData" : the data the was recieved from the 
        #               accept/decline message for the command
        #               This will start as None if no accept/decline message was recieved
        #           "messageSent" : True/False, true if message has been called using the
        #               nextMessage() generator
        #               
        self._commandIDs : dict = {}
        

        #message handling
        #event dictionary uses the command as a key and the function activated by the command as a value
        #ex: {"kill":killFunction}
        self._eventsDictionary : {str:Callable[[object],[bool,object]]} = {}
        try: #this test each function to see if the can be called
            for function in eventsDictionary.values():
                if not callable(function):
                    raise TypeError("All functions must be callable")
        except TypeError as error: #does add any event functions to the dictionary
            self._eventsDictionary = {}
            raise error
        else: #adds the events to event dictionary if no error has occured
            self._eventsDictionary = copy.deepcopy(eventsDictionary)
        
        self._currentMessageSize : int = 0
        self._currentMessageEncoding : str = ""

#----------queing-------------------------------------------
    def _getNewID(self, command : str, data) -> int:
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
        while newID in self._commandIDs.keys():
            newID +=1
        #command IDs has the following keys:
        #   [int], the id number as an integer, no two commands can have same ID
        #       inside the ID key:
        #           "command" : name of command
        #           "data" : data that is used with the command
        #           "hasAccept" : True/False, true if command was recieved 
        #               with an accepted command, false if decline command
        #               This will start as None if no accept/decline message was recieved
        #           "replyData" : the data the was recieved from the 
        #               accept/decline message for the command
        #               This will start as None if no accept/decline message was recieved
        #           "messageSent" : True/False, true if message has been called using the
        #               nextMessage() generator
        #               
        self._commandIDs[newID]={"command" : command, "data" : data,
                                  "hasAccept" : None, "replyData" : None, "messageSent" : False}
        return newID
    def _addToQue(self, newMessage : str, encoding : str = "utf-8", hasPriority : bool = False):
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
        hasPriority : bool, optional
            if True the message will be pushed to the top of the que. The default is False.

        Returns
        -------
        None
            method will never return anything

        """
        if hasPriority:
            if self._messageQue[0][0][0:4] == "size" or self._messageQue[0][0][0:4] == "lmf ":
                newQue : tuple = *self.__makeEncodingMessage(newMessage, encoding), *self._messageQue
            else:
                newQue : tuple = self._messageQue[0], *self.__makeEncodingMessage(newMessage, encoding), *(self._messageQue[1:])
            self._messageQue = list(newQue)
            return None
        
        newQue : tuple = *self._messageQue, *self.__makeEncodingMessage(newMessage, encoding)
        self._messageQue = list(newQue)
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
        
        Raises
        ------
        TypeError
            If parameter eventFunction is not callable
        KeyError
            If command is already bounded to a function
        

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
        
        reply to echo function
        ----------------------
        function must follow the same rules as the event functions
        if the reply to echo function returns True then the instance will 
        print the data to the console
        otherwise it will be up to you to manipulate the data how you see fit
        

        """
        #add function to event list
        if not callable(eventFunction):
            error = TypeError("Event function is not callable. Read the doc string")
            raise error
            return False
        if command in self._eventsDictionary.keys():
            error = KeyError("This command is already in use")
            raise error
            return False
        
        self._eventsDictionary[command] = eventFunction
        return True
    
        

#---------------builtin messages and commands---------------------------------------
    def __makeEncodingMessage(self, messageToSend : str, encoding : str = "utf-8") -> tuple(str):
        """
        creates an encoding message for the message and adds that as a tuple
        

        Parameters
        ----------
        messageToSend : str
            the message that needs the encoding message
        encoding : str, optional
            Format of the message. The default is "utf-8".

        Returns
        -------
        tuple(str)
            The encoding message(s) plus the message in a tuple.

        """
        messageSize = len(messageToSend) 
        encodingMessage = "size" + str(messageSize) + "code" + encoding +";" #creates encoding message
        if len(encodingMessage) > self._ENCODINGMESSAGESIZE: # if encoding message is to big to fit in normal encoding size 
            encodingMessage = encodingMessage.replace("size", "lmf size") # replace normal encoding with large message format encoding
            return *self.__makeEncodingMessage(encodingMessage, "utf-8"), messageToSend
        return (encodingMessage, "utf-8"), (messageToSend, encoding)
                            #echo commands
    def echo(self, messageToEcho : str, encoding : str = "utf-8", hasPriority : bool = False)-> None:
        """
        Sends a message that will be recieved and parroted back.

        Parameters
        ----------
        messageToEcho : str
            message to be parroted
        encoding : str, optional
            The encoding of the message. The default is "utf-8".
        hasPriority : bool, optional
            if true the message will be pushed to the top of the message que. The default is False.
            
        Returns
        -------
        None
            The method will never return anything

        """
        message = {"command":"echo", "ID":None, "data":messageToEcho}
        message = json.dumps(message)
        message = message.encode(encoding)
        #echo does not get an idea because it is special
        #echo is not dependent on a message back from sender
        self._addToQue(message, encoding, hasPriority)
        return None
    def _returnEcho(self, recvMessage : dict, encoding : str = "utf-8") -> None:
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
            You will get None and be happy! >:-O

        """
        #return echo echo
        message = {"command":"rply", "ID":None, "data":recvMessage["data"]}
        message = json.dumps(message)
        message = message.encode(encoding)
        self._addToQue(message, encoding)
        return None
    
                #decline and accepting messages
    def _acceptAndDecline(self, recvMessage : dict, data, hasAccept : bool):
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
        command = "acct" if hasAccept else "decl"
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
        #removed encoding here: because it was converting message into byte form
        self._addToQue(message, "utf-8")
        return None

#-----------------get message data and states----------------------

    def getData(self, commandOrDictionary : str | dict, commandID : int = None):
        """
        

        Parameters
        ----------
        commandOrDictionary : str | dict
            can be the name of the command or the dictionary the recieve method
            dictionary requirements:
                {name of command as str : commandID0} 
        commandID : int, optional
            ID of command. If using the dictionary from the recieve method
            please leve blank
        Raises
        ------
        TypeError
            If the commandOrDictionary is not a string or a dictionary
        KeyError
            If the command and ID pair does not exist in the current list of running commands
        ReferenceError
            If command has not been sent as a message yet (this ussaully means it is still in the que)
        
        Returns
        -------
        bool | None
            if the command had been accepted by the reciever
            this will be true
            if the command had been declined by the reciever
            this will be false
            if the receiver has not sent any message replying to this command
            this will be None
        data
            data sent by the reciever
        
        Important Information
        ---------------------
        A command/message that has recieved an accept/decline message will be deleted after acessing the data
        This will ensure that unneeded commands/messages will not hog resources

        """
        #command IDs has the following keys:
        #   [int], the id number as an integer, no two commands can have same ID
        #       inside the ID key:
        #           "command" : name of command
        #           "data" : data that is used with the command
        #           "hasAccept" : True/False, true if command was recieved 
        #               with an accepted command, false if decline command
        #               This will start as None if no accept/decline message was recieved
        #           "replyData" : the data the was recieved from the 
        #               accept/decline message for the command
        #               This will start as None if no accept/decline message was recieved
        #           "messageSent" : True/False, true if message has been called using the
        #               nextMessage() generator
        #
        command : str = None
        if commandID is None and isinstance(commandOrDictionary, dict):
            commandOrDictionary = commandOrDictionary["command"]
            commandID = commandOrDictionary["ID"]
        elif isinstance(commandOrDictionary, str):
            command = commandOrDictionary
        else:
            raise TypeError("commandOrDictionary must be a string or a dictionary")
        try:
            commandInfo = self._commandIDs[commandID]
        except KeyError:
            raise KeyError("There is no command with an ID of [" + str(commandID) + "] that currently exist.")
        if commandInfo["command"] == command:
            if commandInfo["messageSent"]:
                hasAccept = commandInfo["hasAccept"]
                replyData = commandInfo["replyData"]
                #checks to see if an accept/decline message has been recieved
                if isinstance(hasAccept, bool):
                    del self._commandIDs[commandID] #removes command data from commandIDs list if accept/decline message has been recieved
                return hasAccept, replyData
            error = "command \"" + command + "\" with ID[" + str(commandID) + "] has not been sent please send message before trying to access the data"
            raise ReferenceError(error) #I do not know of a better error
    
    def getCommandStatus(self, commandOrDictionary : str | dict, commandID : int = None) -> str:
        """
        gets useful information about the command in the form of a string

        Parameters
        ----------
        command : str | dict
            the name of the command or dictionary from recieve method
        commandID : int, optional
            The ID of command

        Raises
        ------
        KeyError
            If command with the name and ID does not existm the instance of the
            class will throw an error

        Returns
        -------
        str
            command status in the form of a user readable string
            (you can use to print to a console)

        """
        #command IDs has the following keys:
        #   [int], the id number as an integer, no two commands can have same ID
        #       inside the ID key:
        #           "command" : name of command
        #           "data" : data that is used with the command
        #           "hasAccept" : True/False, true if command was recieved 
        #               with an accepted command, false if decline command
        #               This will start as None if no accept/decline message was recieved
        #           "replyData" : the data the was recieved from the 
        #               accept/decline message for the command
        #               This will start as None if no accept/decline message was recieved
        #           "messageSent" : True/False, true if message has been called using the
        #               nextMessage() generator
        #
        
        #this block ensures that weither recieveing a string or a command dictionary
        #the correct information about ID and name is still filled in
        command : str = None
        if commandID is None and isinstance(commandOrDictionary, dict):
            commandOrDictionary = commandOrDictionary["command"]
            commandID = commandOrDictionary["ID"]
        elif isinstance(commandOrDictionary, str):
            command = commandOrDictionary
        else:
            raise TypeError("commandOrDictionary must be a string or a dictionary")
            return None
        
        commandInfo : str = ''
        if self._commandIDs[commandID]["command"] != command:
            raise KeyError("Command instance not found")
            return commandInfo
        commandInfo += "command [" + command + "], data["
        try:
            commandInfo += str(self._commandIDs[commandID]["data"]) + "], "
        except TypeError:
            commandInfo += "data cannot be converted], "
        
        if self._commandIDs[commandID]["messageSent"] \
            and self._commandIDs[commandID]["hasAccept"] is None:
            commandInfo += "message is waiting for a message, "
        elif self._commandIDs[commandID]["messageSent"] \
            and self._commandIDs[commandID]["hasAccept"] == True:
            commandInfo+= "message has recieved an accept, "
        elif self._commandIDs[commandID]["messageSent"] \
            and self._commandIDs[commandID]["hasAccept"] == False:
            commandInfo += "message has recieved an decline, "
        elif not self._commandIDs[commandID]["messageSent"] \
            and self._commandIDs[commandID]["hasAccept"] is None:
                commandInfo += "message is ready to be sent, "
        else:
            commandInfo += "undefined behavior[" + \
                str(self._commandIDs[commandID]["messageSent"]) + ", " + str(self._commandIDs[commandID]["hasAccept"]) + "]"
        
        if self._commandIDs[commandID]["hasAccept"] is None:
            commandInfo += "No data has been recieved, "
        else:
            commandInfo += "recieved data["
            try:
                commandInfo += str(self._commandIDs[commandID]["replyData"])
            except TypeError:
                commandInfo += "data cannot be converted"
            commandInfo += "]"
        return commandInfo
    
    def getAllCommandStatus(self) -> str: 
        """
        gets the status of all current commands in a human readable string

        Returns
        -------
        str
            command status in the form of a user readable string
            (you can use to print to a console)

        """
        commandStatus : str = ''
        for ID, commandInfo in self._commandIDs.items():
            commandStatus += self.getCommandStatus(commandInfo["command"], ID) + '\n'
        return commandStatus
    
    
    def getQueList(self) -> tuple :
        """
        list of message in a the current que.

        Returns
        -------
        tuple
            a (deep-)copy of the messages

        """
        queList : tuple  = tuple(copy.deepcopy(self._messageQue))
        return queList
            
    def getCommandList(self) -> tuple:
        """
        list of commands and their IDs
        

        Returns
        -------
        tuple
            a (deep-)copy of the commands and IDs.

        """
        commandList : list = []
        for commandID, commandInfo in self._commandIDs.items():
            commandList.append({"command":commandInfo["command"], "ID" : commandID})
        return tuple(copy.deepcopy(commandList))
    
    @staticmethod
    def getStaticEncodingSize():
        return MyMessage.ENCODINGMESSAGESIZE
    @staticmethod
    def getStaticEncodingEncoding():
        return MyMessage.ENCODINGMESSAGESIZE
    
                
#------------create and send messages-------------------------------------------
    def command(self, command : str, data , encoding : str = "utf-8", hasPriority : bool = False)-> None:
        """
        creates a message with the command and data

        Parameters
        ----------
        command : str
            name of command
        data : TYPE
            any data used by command
        encoding : str, optional
            encoding of message. The default is "utf-8".
        hasPriority : bool, optional
            if True, the message will be pushed to the beginning of the message que. The default is False

        Returns
        -------
        dict
            {"command":command, "ID" : commandID}
            

        """
        if command == "echo":
            self.echo(data, encoding, hasPriority)
            return None
        commandID = self._getNewID(command, data)
        message = {"command":command, "ID":commandID, "data":data}
        message = json.dumps(message)
        message.encode(encoding)
        self._addToQue(message, encoding, hasPriority)
        return {"command":command, "ID" : commandID}

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
                messageWithEncoding = self._messageQue.pop(0)
                try:
                    #command IDs has the following keys:
                    #   [int], the id number as an integer, no two commands can have same ID
                    #       inside the ID key:
                    #           "command" : name of command
                    #           "data" : data that is used with the command
                    #           "hasAccept" : True/False, true if command was recieved 
                    #               with an accepted command, false if decline command
                    #               This will start as None if no accept/decline message was recieved
                    #           "replyData" : the data the was recieved from the 
                    #               accept/decline message for the command
                    #               This will start as None if no accept/decline message was recieved
                    #           "messageSent" : True/False, true if message has been called using the
                    #               nextMessage() generator
                    #
                    message : dict = json.loads(messageWithEncoding[0])
                    #these message do not exist in commandID
                    self._commandIDs[message["ID"]]["messageSent"] = True
                except KeyError:
                    ...
                except json.JSONDecodeError:
                    ...
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
        messageSize : int = self._ENCODINGMESSAGESIZE if self._currentMessageSize == 0 else self._currentMessageSize
        messageCode : str = self._ENCODINGMESSAGEENCODING if self._currentMessageEncoding == "" else self._currentMessageEncoding
        return messageSize, messageCode
#-----------Error Checking Functions
    def __checkFunctionAndGetReturns(self, command : str, function, data):
        """
        runtime check to make sure function is returning the right values and will
        allow the data to be passed to it

        Parameters
        ----------
        command : str
            name of command associated with the function.
        function : TYPE
            the function,
        data : TYPE
            the data being passed to the function,
            the data for function parameters

        Raises
        ------
        TypeError
            If the function does not return the correct types in the
            correct order

        Returns
        -------
        bool
            if the function returns true for if the command has been accepted
        TYPE
            the return data made by the function

        """
        hasAccept, returnData = None, None
        try:
            functionReturns : tuple = tuple(function(data))
            hasAccept, returnData = functionReturns[0], functionReturns[1:]
        except TypeError as e:
            if "is not iterable" in str(e):
                error = "Function \"" + str(function) + "\" bounded to command \"" + command + "\" does not return the correct parameters. Please see documentation for details"
                raise TypeError(error)
        try:
            assert isinstance(hasAccept, bool)
        except AssertionError:
            error = "The first value of the return that the\"" + str(function) + "\" should return is bool value for accepting/declining"
            raise TypeError(error)
            return None, None
        return hasAccept, *returnData
    
    # try:
    #     hasAccept, xdata = functionReturns
    # except TypeError as e:
    #     print(e)
    #     if "cannot unpack non-iterable" in str(e):
    #         function = self._eventsDictionary["rply"]
    #         error = "Function \"" + str(function) + "\" bounded to command \""
    #         error += recvMessage["command"] + "\" the correct information. Please see documentation for details"
    #         print (error)
    #         raise TypeError(error)
    #         return {"command":None, "ID":None}
    # try:
    #     assert isinstance(hasAccept, bool)
    # except AssertionError:
    #     raise TypeError("The first Ret")
    # if hasAccept:
    #     print(data)
    # else:
    #     ...
    
#---------receive messages------------------------------------------------------------
    def _getFormatMessage(self, messageRecieved:str, encoding : str) -> dict | bool:
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
            self._currentMessageSize = int(messageRecieved[4:endSize])
            self._currentMessageEncoding = messageRecieved[endSize+4:endEncoding]
            return {"command": None, "ID":None}
        elif messageRecieved[0:4] == "lmf ":
            endSize : int = messageRecieved.find("code")
            endEncoding : int = messageRecieved.find(";")
            self._currentMessageSize = int(messageRecieved[8:endSize])
            self._currentMessageEncoding = messageRecieved[endSize+4:endEncoding]
            return {"command": None, "ID":None}
        return False
    
    def _getEchoMessage(self, recvMessage : dict, encoding : str) -> dict:
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
        self._returnEcho(recvMessage, encoding)
        self._currentMessageSize = 0
        self._currentMessageEncoding = ""
        return {"command" : None, "ID":None}
            
    def _getEchoReplyMessage(self, recvMessage : dict, encoding : str) -> dict:
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
        if "rply" in self._eventsDictionary.keys():
            hasAccept, data = self.__checkFunctionAndGetReturns("rply",
            self._eventsDictionary["rply"], recvMessage["data"])
            if hasAccept:
                logging.info("Data created from echo:", data)
        else:
            ...
        return {"command":"rply", "ID":None}
    
    def _getAcceptDeclineMessage(self, recvMessage : dict, encoding : str, isAccepted : bool) -> dict:
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
            returns dictionary {"command", command as [str] : [int], ID as int}
            the information in the dictionary can be used to access
            the stored data from the message

        """
        if self._commandIDs[recvMessage["ID"]]["command"] != recvMessage["data"]["command"]:
            error = "Command, " + recvMessage["data"]["command"] + ", with ID["
            error += str(recvMessage["ID"]) + "] does not exist."
            raise KeyError(error)
            return {"command" : None, "ID" : None}
            
         #command IDs has the following keys:
         #   [int], the id number as an integer, no two commands can have same ID
         #       inside the ID key:
         #           "command" : name of command
         #           "data" : data that is used with the command
         #           "hasAccept" : True/False, true if command was recieved 
         #               with an accepted command, false if decline command
         #               This will start as None if no accept/decline message was recieved
         #           "replyData" : the data the was recieved from the 
         #               accept/decline message for the command
         #               This will start as None if no accept/decline message was recieved
         #           "messageSent" : True/False, true if message has been called using the
         #               nextMessage() generator
         #
        commandID = recvMessage["ID"]
        self._commandIDs[commandID]["replyData"]=recvMessage["data"]["data"]
        self._commandIDs[commandID]["hasAccept"] = isAccepted
        return {"command" : recvMessage["data"]["command"], "ID" : commandID}

    def _getCommandMessage(self, recvMessage : dict, encoding : str) -> dict:
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
        function = self._eventsDictionary[recvMessage["command"]]
        isAccepted, *functionData = self.__checkFunctionAndGetReturns(recvMessage["command"], 
                                                                      function, recvMessage["data"])
        self._acceptAndDecline(recvMessage, functionData, isAccepted)
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
            
        Raises
        ------
        TypeError
            If the command recieved is not a command that has been bounded to a function
        
        Returns
        -------
        dict
            If the recieved message is a valid accept or decline message
            that was sent to respond to this instance of the class's message 
            The method will return dictionary:
            {"command":command, "ID":ID}. Please use this to
            access the data from the message by using the method getData(dict|str, int)

        """
        returnValue = self._getFormatMessage(messageRecieved, encoding)
        if isinstance(returnValue, dict):
            return returnValue
        
        recvMessage : dict = json.loads(messageRecieved)
        if recvMessage["command"] == "echo":
            returnValue = self._getEchoMessage(recvMessage, encoding)
        elif recvMessage["command"] == "rply":
            returnValue = self._getEchoReplyMessage(recvMessage, encoding)
        
        elif recvMessage["command"] == "acct":
            returnValue = self._getAcceptDeclineMessage(recvMessage, encoding, True)
        elif recvMessage["command"] == "decl":
            returnValue = self._getAcceptDeclineMessage(recvMessage, encoding, False)
        elif recvMessage["command"] in self._eventsDictionary.keys():
            returnValue = self._getCommandMessage(recvMessage, encoding)
        else:
            raise KeyError("The command \"" + recvMessage["command"] + "\" is not a known command")
            self._acceptAndDecline(recvMessage, None, False)
        self._currentMessageSize = 0
        self._currentMessageEncoding = ""
        return returnValue

if __name__ == "__main__":
    raise NotImplementedError("This is a module is not a script and should only be imported")
        