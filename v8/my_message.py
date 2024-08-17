# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 15:31:36 2024

@author: Phatty
"""

import json, logging, copy
from command import Command

class MyMessage:
    """A class to simplify sending messages between devices
    
    ===========Important information===========
    ===========================================
    
    eventsDictionary
    ----------------
    items in dictionary requirement {[str] command name : [function(dict | None) -> int, dict|None]} a valid function that has
    _________________________________________________________________________________________________________________________
    1) one parameter that will be used to pass command data into as a dictionary or None if nothing is being passed
    2) return a bool value that determines if accept/decline (True/False) will be sent function can more than one value at a time, the rest will be packaged and sent in the accept/decline message as None if no additional information is being sent or a dictionary with the the additional information
    """
    _ENCODINGMESSAGESIZE = 20
    _ENCODINGMESSAGEENCODING = "utf-8" #possible hold-over for old version of class, my delete later
    
    #logging
    __instanceCount : int = 0 #instance count of class. you can have multiple instances open
    __instanceIDs : dict = {}
    
    def __init__(self, eventsDictionary : dict | None = None):
        """
        A class to simplify sending messages between devices

        Parameters
        ----------
        eventsDictionary : dict | None, optional
            events can be attached to commands using dictionaries. The default is None.
            see __doc__ for more information

        """
        #set up logging
        self.__instanceID = self.__getNewInstanceID()
        self._logger : logging.Logger = logging.getLogger("myMessage" + str(self.__instanceID))
        self._logger.debug("Instance with ID " + str(self.__instanceID) + "  of MyMessage has been created")
        
        self._eventsDictionary : dict = self.__getCallableOnly(eventsDictionary)
        #contains Commands instances
        self._commandQue : list = []
        #commandIDs have the following items
        ##[int] the ID of the command : [Command] the instance of the command
        self._commandIDs : dict = {}
        
        self._currentMessageSize : int = 0
        self._currentMessageEncoding : str = ""
    
    def __del__(self):
        self.__removeInstanceID()
    
        
#-------------constructor helpers----------------------------------------
    def __getNewInstanceID(self) -> int:
        """
        adds instance to the ID dictionary and increases instance counter by one
        Only used with the constructor

        Returns
        -------
        int
            ID keyed to the instance from the ID dictionary

        """
        count : int = 0 #creates and sets count to zero
        #finds the smallest possitive int that is not being used
        while count in MyMessage.__instanceIDs.keys():
            count+=1
        #adds instance to the static list of instance IDs
        MyMessage.__instanceIDs[count] = self
        #increments the instance count by 1
        MyMessage.__instanceCount+=1
        return count
    
    def __getCallableOnly(self, eventsDictionary : dict | None) -> dict:
        """
        makes a dictionary of only callable events
        non callable a vents will have the key set to None

        Parameters
        ----------
        eventsDictionary : dict | None
            the commands and their events as a dictionary
            see __doc__ for more information

        Raises
        ------
        TypeError
            If an event in the dictionary is not callable.
            You can ignore the exception but worse things might happen down the line ;-)

        Returns
        -------
        dict
            blank dictionary if eventsDictionary is None
            a dictionary with the non-callable events removed

        """
        #check if eventsDictionary is a dictionary
        if isinstance(eventsDictionary, dict):
            newDictionary = eventsDictionary.copy() #makes a copy of the event dictionary
            #flag to make that is set to false if one or more events
            #are not callable or are unoveridable builtin commands
            allCallable : bool = True
            for command, func in eventsDictionary.items(): #checks all commands
                #checks if function is not callable
                if not callable(func):
                    newDictionary[command] = None
                    allCallable = False
                    error = f"Command \"{command}\" does not have a valid/callable event"
                    self._logger.error(error) #add to log
                #check if message if part of the unoveridable methods
                if any(command.lower() in ("echo","decline", "accept", "error")):
                    error = f"the special command \"{command.lower()}\" cannot be overided"
                    del newDictionary[command]
                    self._logger.error(error) #adds to log
                    allCallable = False
            #checks if the callable flag has been set to False and will raise an error                    
            if not allCallable:
                raise TypeError("One or more of the event are not valid/callable functions")
            return newDictionary
        
        return {} #if eventsDictionary is not a dictionary
        
    
#-----------------destructor helper------------------------
    def __removeInstanceID(self) -> None:
        """
        removes instance to the ID list and decreases instance counter by one
        Only used with the destructor

        Returns
        -------
        None
            This method is fresh out of something

        """
        del MyMessage.__instanceIDs[self.__instanceID]
        MyMessage.__instanceCount -= 1
        

#-----------ID handling----------------------------
    def _getNewID(self, commandName : str, data : dict, hasPriority : bool = False) -> int:
        """
        gives command new idea and adds it to the command id dictionary

        Parameters
        ----------
        command : str
            name of command
        data : dict
            command data
        hasPriority : bool, optional
            creates a command with higher priority
            see "_addToQue" method for more details

        Returns
        -------
        int, Command
            a fresh ID with along with adding the command to the dictionary
            and the command instance

        """
        newID : int = 0 #creates and sets count to zero
        #finds the smallest possitive int that is not being used
        while newID in self._commandIDs.keys():
            newID +=1
        #creates command
        command = Command(commandName, newID, data, hasPriority)
        self._commandIDs[newID] = command
        return newID, command
#--------command handling---------------------------------------------------

    def addcommand(self, command : str, eventFunction)-> bool:
        """
        binds event function to command and adds that to
        the event dictionary

        Parameters
        ----------
        command : str
            command to respond to
            
        eventFunction : func(bool, dict | None) -> (bool, dict | None)
           havent you been listening? I told you to see __doc__ for more details
        Raises
        ------
        TypeError
            If parameter eventFunction is not callable
        KeyError
            If command is already bounded to a function
            
                                                        
        ------------------------------------------------
        Returns
        -------
        bool
            returns True if function and command have been added to the events
        
        Additional Information
        ----------------------
        You may want to implement your own function to
        overide the builtin version for the recieving back the echo. 
        You can do this easily by using "rply" as the command parameter
        example: addCommand("reply", validFunction)
        
        reply to echo function
        ----------------------
        function must follow the same rules as the event functions
        if the reply to echo function returns True then the instance will 
        print the data to the console
        otherwise it will be up to you to manipulate the data how you see fit
        

        """
        #checks to see if the event function is callable
        if not callable(eventFunction):
            error = TypeError("Event function is not callable. Read the doc string")
            raise error
            return False
        #checks command has already been added in the eventsDictionary
        if command in self._eventsDictionary.keys():
            error = KeyError("This command is already in use")
            raise error
            return False
        
        self._eventsDictionary[command] = eventFunction #adds command/function item to the eventDictionary
        return True
    
    
    #helper for command method
    def __commandConvertToEcho(self, data : dict | None, hasPriority : bool = False)->None:
        """
        converts command dictionary or None instance to a string that can be sent as an echo
        used as a helper function for the command method

        Parameters
        ----------
        data : dict | None
            the data from the command method
            data must contain {"message": [str], "encoding" : [str]}
        hasPriority : bool, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None
            This function only returns nothing, you will run into this alot

        """
        if data is None:
            self.echo("", None, hasPriority)
        elif isinstance(data, dict):
            self.echo(data["message"], data["encoding"])
        #if data is not a dictionary or None instance then program will convert it to a string
        #will also log the conversion as a warning
        else:
            self._logger.warning("data is not a dictionary or None type. Program will assume object can be converted to a string")
            return self.echo(str(data))
    
    #command method
    def command(self, commandName : str, data : dict | None,  hasPriority : bool = False) -> dict | None:
        """
        creates a command with data

        Parameters
        ----------
        commandName : str
            DESCRIPTION.
        data : dict | None
            DESCRIPTION.
        hasPriority : bool, optional
            If True the message gets pushed to the top of the que and will be sent earlier. The default is False.

        Returns
        -------
        dict | None
            {"command" : [str] the commandName, "ID" : [int] the id of the new command}

        """
        #if for some reason, the command you choose is echo
        if commandName.lower() == "echo":
            return self.__commandConvertToEcho(data, hasPriority)
        
        commandID, command = self._getNewID(commandName, data, hasPriority)#adds command to ID dictionary
        self._addToQue(command, hasPriority) #adds command to the que list
        return {"command" : commandName, "ID" : commandID}
    
 #-----------------find command----------------------------------
    def findCommandFromName(self, commandName : str) -> list:
        """
        Finds all commands in the MyMessage instance with the name specified

        Parameters
        ----------
        commandName : str
            specify the name of the command

        Returns
        -------
        list
            a list of dictionaries with all commands that match the name
            {"command" : [str] the name of the command, "ID" : the ID of the command}
            will retrun an empty list if no current command has the name specified.

        """
        listofCommandWithName : list = []
        possibleCommand : Command; possibleID : int;
        for possibleID, possibleCommand in self._commandIDs.items():
            if possibleCommand.getName() == commandName:
                listofCommandWithName.append({"command" : possibleCommand.getName(), "ID" : possibleID})
        return listofCommandWithName
    def findCommandFromID(self, commandID : int) -> list:
        """
        Finds all commands in the MyMessage instance with the ID specified
        *note only one value should appear, this just returns a list for the
        sake of matching the findCommandFormName method*
        Parameters
        ----------
        commandID : int
            specify the ID of the command

        Returns
        -------
        list
            a list of dictionaries with all commands that match the name
            {"command" : [str] the name of the command, "ID" : the ID of the command}
            will retrun an empty list if no current command has the name specified.

        """
        listofCommandWithName : list = []
        possibleCommand : Command; possibleID : int;
        for possibleID, possibleCommand in self._commandIDs.items():
            if possibleID == commandID:
                listofCommandWithName.append({"command" : possibleCommand.getName(), "ID" : possibleID})
        return listofCommandWithName
        
    def getCommandInfo(self, commandDict : dict) -> dict | None:
        """
        Gets a copy of the command information
        *does not delete the command from the instance*
        Parameters
        ----------
        commandDict : dict
            {"command" : [str] the name of the command, "ID" : the ID of the command}
            this can be obtained by the findCommand methods or the returns from the
            recieve method

        Returns
        -------
        dict
            returns a dictionary with the following
            {"command" : [str],
             "ID" : [int],
             "data" : [TYPE],
             "hasPriority" : [bool]}
        
        None
            if the information of the commandDict does not match
            any of the current commands

        """
        command : Command = self._commandIDs[commandDict["ID"]]
        if command.getName() == commandDict["command"]:
            return copy.deepcopy(dict(command))
        return None
    
    def popCommandInfo(self, commandDict : dict) -> dict | None:
        """
        Returns the command information and deletes the command
        from the instance.
        
        *this will allow the ID of the command to be resued by future commands*

        Parameters
        ----------
        commandDict : dict
            {"command" : [str] the name of the command, "ID" : the ID of the command}
            this can be obtained by the findCommand methods or the returns from the
            recieve method

        Returns
        -------
        dict
            returns a dictionary with the following
            {"command" : [str],
             "ID" : [int],
             "data" : [TYPE],
             "hasPriority" : [bool]}
        
        None
            if the information of the commandDict does not match
            any of the current commands

        """
        command : Command = self._commandIDs[commandDict["ID"]]
        if command.getName() == commandDict["command"]:
            return dict(self._commandIDs.pop(commandDict["ID"]))
        return None
    

#------message que --------------------------------------
    def _addToQue(self, command : Command , hasPriority : bool = False) -> True:
        """
        adds command to que by using the Command.send() method
        all data in the que must be dictionaries

        Parameters
        ----------
        command : Command | dict
            the Command instance
        hasPriority : bool, optional
            pushes command to top of the que if True. The default is False.

        Returns
        -------
        True
            Will return True upon adding command to the que
            (which just means it will always return True bub)

        """
        if hasPriority:
            self._commandQue.insert(0, command.send())
            return True
        self._commandQue.append(command.send())
        return True
    


#-----------generate encoding message-----------
    def _getEncodingMessage(self, messageOrEncodeMessage : str, **kwargs) ->tuple:
        """
        creates an encoding message determined by the message size and encoding
        will recursively generate messages until encoding message can display
        the correct size

        Parameters
        ----------
        messageOrEncodeMessage : str
            message, usually in the form of a json message
            
            used by function only(or the encoding message for recursive creation)

        Returns
        -------
        tuple
            the encoding message(s) and the messageOrEncodingMessage variable
        
        Additional Information
        ----------------------
        the encoding message should look like
        size[int]code[str];
        example: "size256codeutf-8;"
        

        """
        messageSize = len(messageOrEncodeMessage)
        encodingMessage = "size" + str(messageSize) + "code" + self._ENCODINGMESSAGEENCODING +";" #creates encoding message
        if len(encodingMessage) > self._ENCODINGMESSAGESIZE: #if encoding message is to big to be a normal encoding message
            encodingMessage = encodingMessage.replace("size", "lmf size") # replace normal encoding with large message format encoding
            return *self._getEncodingMessage(encodingMessage), messageOrEncodeMessage #recursive until an encoding message meets encoding message size
        return encodingMessage, messageOrEncodeMessage

#------------builtin commands--------------
    def echo(self, messageToEcho : str, encoding : str | None = None, hasPriority : bool = False)-> None:
        """
        Sends a message that will be recieved and parroted back.

        Parameters
        ----------
        messageToEcho : str
            message to be parroted
        encoding : str | None, optional 
            the encoding of the message. The default is None
        hasPriority : bool, optional
            if true the message will be pushed to the top of the message que. The default is False.
            
        Returns
        -------
        None
            The method will never return anything

        """
        
        echoMessage : Command = None #creates variable
        if encoding is None:
            #creates a command with no ID and encoding
            echoMessage = Command("echo", None, {"message" : messageToEcho, "encoding" : encoding}, hasPriority)
        else:
            #creates a command with no ID and encodes the message with specified encoding
            echoMessage = Command("echo", None, {"message" : messageToEcho.encode(encoding), "encoding" : encoding}, hasPriority)
        #adds message to the sending que
        self._addToQue(echoMessage, hasPriority)
        return None
    
    def _returnEcho(self, messageRecived : dict)->None:
        """
        creates a reply message and adds it to the que

        Parameters
        ----------
        messageRecived : dict
            I think that is self evident

        Returns
        -------
        None
            This will never return anything

        """
        command : Command = Command("reply", None, 
                                    {"message" : messageRecived["data"]["message"], "encoding" : messageRecived["data"]["encoding"]},
                                    messageRecived["hasPriority"])
        self._addToQue(command, messageRecived["hasPriority"])
        return None
    
    
    
    def _acceptDecline(self, messageRecieved : dict, hasAccepted : int, returnData : dict | None) -> None:
        """
        creates accept and decline message

        Parameters
        ----------
        messageRecieved : dict
            documentation is documentation
        hasAccepted : int
            an [int] that determines the command sent. see __doc__ for more. 
            Usually used with a function from the eventDictionary in order to
            proccess recieved messages
        returnData : dict | None
            return data usually generated from a function in the event dictionary

        Returns
        -------
        None
            The accept/decline message will be added to que
            You will never get anything from this method! >:-L

        """
        if returnData is None:
            returnData = {}
        returnData["recievedCommand"] = messageRecieved["command"]
        command : Command = Command( #
            "accept" * (hasAccepted == 1) + "decline" * (hasAccepted == -1) + "error" * (hasAccepted == 0),
            messageRecieved["ID"], 
            returnData,
            messageRecieved["hasPriority"]) #fast math for message
        self._addToQue(command, messageRecieved["hasPriority"]) #add message to que
        return None
    
    
    
#-------send messages------------------------
    def _getMessageToSend(self) -> tuple | None:
        """
        Convert the first sent command from the commandQue into json and adds the
        encoding message(s)
        
        This will also be where encryption would be added
        Use this only end the send method

        Yields
        ------
        message : str
            the encoding message(s) followed by the command as a json

        """
        command : dict = self._commandQue.pop(0)
        messageToSend : str = json.dumps(command) # converts sent command as dictionary to json
        debugInfo : str = "sending message \"{commandName}\" with ID {commandID}."
        debugInfo.format(commandName = command["command"], commandID = command["ID"])
        self._logger.debug(debugInfo) # logs that the message is being sent
        for message in tuple(self._getEncodingMessage(messageToSend)):
            yield message
        
        
    def send(self) -> str | bool:
        """
        send the next command in que

        Yields
        ------
        message : str
            encoding message(s) followed by the command in json

        """
        while len(self._commandQue):
            for message in self._getMessageToSend():
                yield message
        return None
    
#--------event processor--------------
    def _getFunctionReturns(self, function, messageData : dict | None) -> tuple:
        """
        Proccess commands that use defined by the eventDictionary
        
    
        Parameters
        ----------
        function : [function([dict])-> [int], [dict | none]]
            see __doc__ for more details
        messageData : dict | None
            message data to be passed to the function
    
        Raises
        ------
        ValueError
            If function does not return two values
        TypeError
            If the first value returned by the function is not [bool] or
            second value returned by the function is not [dict|None]
    
        Returns
        -------
        [int], dict|None
            reply data to be sent back
        """
        
        #create variables
        hasAccept : int | None = None
        returnData : dict | None = None
        try:
            hasAccept, returnData = function(messageData)
        #if function does not return to values
        except ValueError:
            errorMessage : str = f"\"{type(function)}\" must return to values: [int] and [dict | None]"
            self._logger.error(errorMessage)
            raise ValueError(errorMessage)
        #if function does not return the correct types
        if not isinstance(hasAccept, int):
            errorMessage : str = f"\"{type(function)}\" must return [int] for first value"
            self._logger(errorMessage)
            raise TypeError(errorMessage)
        if not isinstance(returnData, dict) and not isinstance(returnData, None):
            errorMessage : str = f"\"{type(function)}\" must return to values: [int] and [dict | None]"
            self._logger.error(errorMessage)
            raise TypeError(errorMessage)
            
        return hasAccept, returnData

#--------recieveMessage--------------------------
    def _getReply(self, messageRecieved) -> None:
        """
        default processing for reply message

        Parameters
        ----------
        messageRecieved : TYPE
            DESCRIPTION.

        Returns
        -------
        None
            DESCRIPTION.

        """
        logAndPrint : str = "Recieved reply from echo with message \"" + messageRecieved["data"]["message"] + "\"" #message displayed by default print and logger
        self._logger.debug(logAndPrint)
        if "reply" in self._eventsDictionary.keys():
            hasAccept, returnData = self._getFunctionReturns(self._eventsDictionary["reply"],
                                                             messageRecieved["data"])
            if hasAccept == 1:
                print(logAndPrint)
        
        print(logAndPrint)
        return None
        
    def _getAcceptAndDecline(self, messageRecieved : dict) -> dict:
        """
        process accept and decline messages

        Parameters
        ----------
        messageRecieved : dict
            DESCRIPTION.

        Raises
        ------
        TypeError
            DESCRIPTION.

        Returns
        -------
        dict
            DESCRIPTION.

        """
        sentCommand : Command = self._commandIDs[messageRecieved["ID"]] #gets command with the matching ID
        #check if names of the IDs do not match
        if messageRecieved["data"]["recievedCommand"] != sentCommand.getName():
            #create message to add to log for the discrepancy
            recievedCommandName : str = str(messageRecieved["data"]["recievedCommand"])
            recievedCommandID : int = messageRecieved["ID"]
            warningMessage : str = "recieved command \"" + recievedCommandName + f"\" with ID {recievedCommandID} does not currently exist"
            self._logger.warning(warningMessage)
            return {"command" : None, "ID" : None}
        
        #check if message recieved meets any of the cases
        hasAccept : int | None = None
        match messageRecieved["command"]:
            case "accept":
                hasAccept = 1
            case "decline":
                hasAccept = -1
            case "error":
                hasAccept = 0 
            case _:
                hasAccept = 404 #"random" "arbitrary" number that is not being used
                recievedCommandName : str = str(messageRecieved["data"]["recievedCommand"])
                recievedCommandID : int = messageRecieved["ID"]
                errorMessage : str = "recieved command \"" + recievedCommandName + f"\" with ID {recievedCommandID}"\
                    +" does not follow any of the accept/decline protocols"
                self._logger.error(errorMessage)
                raise TypeError(errorMessage)
        del messageRecieved["data"]["recievedCommand"] #makes sure the message name is not being added to the sent command reply information
        sentCommand.reply(hasAccept, messageRecieved["data"])
        return {"command" : sentCommand.getName(), "ID" : sentCommand.getData()} 
    
    def _getCommandMessage(self, messageRecieved : dict) -> None:
        function = None 
        try:
            self._eventsDictionary[messageRecieved["oommand"]]
        except KeyError as e:
            raise e
        hasAccept : int
        returnData : dict | None
        hasAccept, returnData = self._getFunctionReturns(function, messageRecieved["data"])
        hasAccept = 0 if isinstance(hasAccept, None) else hasAccept #make sure has accept always is an int
        self._acceptDecline(messageRecieved, hasAccept, returnData)
        return None
    
    def _setEncodingFromMessage(self, recievedMessage : str):
        if "size" in recievedMessage or "lmf size" in recievedMessage:
            #set variables
            startSizeSubstring = recievedMessage.find("size") + 4
            startEncodingSubstring = recievedMessage.find("code") + 4
            messageEnd = recievedMessage.find(';')
            #
            self._currentMessageSize = int(recievedMessage[startSizeSubstring : startEncodingSubstring - 4])
            self._currentMessageEncoding = recievedMessage[startEncodingSubstring : messageEnd]
            return True
        return False
            
    def recv(self, recievedMessage : str) -> dict | None:
        if self._setEncodingFromMessage(recievedMessage):
            return {"command" : None, "ID" : None}
        returnValue : dict | None = {"command" : None, "ID" : None}
        recvMessage : dict = json.loads(recievedMessage)
        match recvMessage["command"]:
            case "echo":
                self._returnEcho(recvMessage)
                returnValue = None
            case "reply":
                returnValue = self._getReply(recvMessage)
            case "accept":
                returnValue = self._getAcceptAndDecline(recvMessage)
            case "decline":
                returnValue = self._getAcceptAndDecline(recvMessage)
            case "error":
                returnValue = self._getAcceptAndDecline(recvMessage)
                
            case _:
                try:
                    self._getCommandMessage(recvMessage)
                except KeyError:
                    logMessage : str = "\"{commandName}\" does not have a function associated with it."
                    logMessage = logMessage.format(commandName = recvMessage["command"])
                    command : Command = Command("decline", recvMessage["ID"], {"reason" : "No function associated with command"}, recvMessage["hasPriority"])
                    self._logger.warning(logMessage)
        self._currentMessageSize : int = 0
        self._currentMessageEncoding : str = ""
        return returnValue
        
        

        
        
        
        
        
    