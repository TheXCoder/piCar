66666646# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 17:56:45 2024

@author: Phatty
"""

import logging

commandLogger = logging.getLogger("commandLogger")


class Command:
    """"""
    def __init__(self, commandName : str, idNumber : int | None, data : dict | None = None, hasPriority : bool = False):
        """
        Commands for MyMessage class to make it easier to access and use commands the right way

        Parameters
        ----------
        commandName : str
            name of command
        idNumber : int | None
            command ID
        data : dict | None, optional
            data associated with the command. The default is None.

        Returns
        -------
        Command
            command instance
        """
        self.__COMMANDNAME : str = commandName
        self.__IDNUMBER : int | None = idNumber
        
        # None if command has not recieved an accept/decline command
        # 1 if command recieves an accept command
        # -1 if a command recieves a decline command
        # 0 if message needs to be resent
        self.__hasAccept : int | None = None
        self.__commandSent : bool = False
        
        self.__data : dict = data
        self.__replyData : dict | None = None
        self.__hasPriority : bool = hasPriority
        


#----operator methods-------------------------------------------    
    def __iter__(self) -> tuple:
        """
        Converts instance to an iterable list that can be used in a dictionary

        Yields
        ------
        tuple
            command information

        """
        
        for item in {
         "command" : self.__COMMANDNAME,
         "ID" : self.__IDNUMBER,
         "data" : self.__data,
         "commandSent" : self.__commandSent,
         "hasAccept" : self.__hasAccept,
         "replyData" : self.__replyData,
         "hasPriority" : self.__hasPriority 
         }.items():
            yield item[0], item[1]
    
        
#---------get attributes of instance methods-------------------------
    
    def getName(self) -> str:
        """
        gets name of the command

        Returns
        -------
        str
            name of the command

        """
        return self.__COMMANDNAME
    def getID(self) -> int | None:
        """
        gets command idenification

        Returns
        -------
        int
            ID of command

        """
        return self.__IDNUMBER
    
    def checkAccept(self) -> int | None:
        """
        gets the status of recieved accept/decline command (if applicable)

        Raises
        ------
        AttributeError
            if the command has not been sent

        Returns
        -------
        int | None
            None if command has not recieved an accept/decline command
            None also if command has not been sent
            1 if command recieves an accept command
            -1 if a command recieves a decline command
            -2 not accessable, the reciever does not have access to that command so don't even bother trying again
            0 for undefined (usually requires the command to be resent)
            
            

        """
        if self.__commandSent:
            return self.__hasAccept
        raise AttributeError("command has not been sent")
        return None
    
    def checkcommandSent(self) -> bool:
        """
        check to see if the command has been sent

        Returns
        -------
        bool
            True if command has been sent
            Otherwise False

        """
        return self.__commandSent
    
    
#------get data methods-----------------------------------
    
    def getData(self) -> dict:
        """
        gets data as dictionary

        Returns
        -------
        dict
            Data associated with the command

        """
        return self.__data
    def getReplyData(self) ->dict | None:
        #only raise attribute when the command is waiting for a valid reply or to be sent
        if self.__hasAccept is None:
            raise AttributeError("command has not recieved a valid accept/decline message")
        if self.__hasAccept == 0:
            raise AttributeError("The command must be resent")
            
        #Although disgusting the reply message being unproccessable is a valid response
        if self.__hasAccept == -2:
            commandLogger.error("The reciever cannot process this command. Don't bother trying again!")
        return self.__replyData

#------recieve reply method---------------------------

    def reply(self, hasAccepted : int, replyData : dict | None) -> bool:
        """
        recieves accept/decline command with its associated data

        Parameters
        ----------
        hasAccepted : int
            If command acct this should be 1
            if command decl this should be -1
            if command needs resent this should be 0
            if command is not accessable to the reciever this should be -2
        replyData : dict | None
            data associated with the reply

        Raises
        ------
        AttributeError
            if the command has already recieved a valid accept/decline
        TypeError
            if hasAccept is not an instance of an int

        Returns
        -------
        bool
            True if reply is valid and can be stored

        """
        if self.__hasAccept == 0:
            commandLogger.warning("accept/decline message shows that this command needs to be resent")
            self.__commandSent = False
            return False
        if self.__hasAccept is not None:
            commandLogger.error(f"command \"{self.____COMMANDNAME}\" with ID:{self.__IDNUMBER} has already recieved reply data")
            raise AttributeError(f"command \"{self.____COMMANDNAME}\" with ID:{self.__IDNUMBER} has already recieved reply data")
            return False
        if not isinstance(hasAccepted, int):
            raise TypeError("\"hasAccepted\" must be value of integer type")
            return False
        self.__hasAccept = hasAccepted
        self.__replyData = replyData
        return True


#--------send message method------------------------------- 
    def send(self) -> dict | None:
        """
        converts message to json-able dictionary that can be sent

        Raises
        ------
        AttributeError
            If the message has been sent and is waiting for a reply

        Returns
        -------
        dict | None
            None if message has been sent and is waiting for a reply
            {"command" : [str] the command name
             "ID" : [int] the command ID,
             "data" : [dict] the data associated with the said command}

        """
        if self.__commandSent:
            raise AttributeError("message has already been sent")
            return None
        self.__commandSent = True
        return {"command" : self.__COMMANDNAME,
                "ID" : self.__IDNUMBER,
                "data" : self.__data,
                "hasPriority" : self.__hasPriority}
    
    
        
        