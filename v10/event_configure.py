# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 20:02:52 2024

@author: Phatty
"""

from locked_file_config import LockedFileConfigParseConverter
import os, copy
        

class EventConfigure:
    _MyMessageConfigDir = "myMessage"
    _configFile = _MyMessageConfigDir + os.sep + "events.ini"
    _configDict : dict = {"commands" : "",
                          "password" : "",
                          "trustedKeys" : ""}
    def __init__(self, commandName : str, lockLevel : int = 0):
        """
        

        Parameters
        ----------
        commandName : str
            DESCRIPTION.
        lockLevel : int, optional
            DESCRIPTION. The default is 0.


        """
        self.__lockLevel : int = lockLevel
        self.__commandName : str = commandName
        self._file : LockedFileConfigParseConverter = LockedFileConfigParseConverter(self._configFile)
        self.__makeConfigFile()
    

    def __makeConfigFile(self) -> bool:
        """
        Creates a config file for the MyMessage Events
        *used with initilization*

        Returns
        -------
        bool
            True if event config file has been created
            Otherwise False

        """
        if self._file.justCreated():
            levelZeroConfig = copy.deepcopy(self._configDict)
            del levelZeroConfig["password"]
            self._file.config = ("level 0", levelZeroConfig)
            print(self._file.config)
            self._file.save()
            return True
        return False
    
    
    def getCommandName(self) -> str:
        return self.__commandName
    
    def getEventConfig(self) -> dict:
        return copy.deepcopy(self._file.config)
    def getLevels(self) -> tuple:
        return dict(self._file)
        
    
    def isCommandInConfig(self):
        key : str
        value : dict
        for key, value in self._file.config.items():
            if self.__commandName in value["commands"]:
                return key, value
        return None
            
    def newMasterPassword(self, newPassword : str, oldPassword:str | None = None,
                    encoding : str = "utf-8", endienness : str = "big") -> bool | None:
        return self._file.newPassword(newPassword, oldPassword, encoding, endienness)
        
        
    def addCommand(self, password: str, textEncoding : str = "utf-8"):
        if self.isCommandInConfig() is not None:
            return False
        passwordFlag = self._file.checkPassword(password, textEncoding)
        eventConfig : dict = self.getEventConfig()
        if self.__lockLevel == 0 and passwordFlag is True:
            commands : str = eventConfig["level 0"]["commands"]
            newCommands =commands.split("|").append(self.__commandName)
            commands = str.join("|", newCommands)
            eventConfig["level 0"]["commands"] = commands
            self._file.config = ("level 0", eventConfig["level 0"])
            return True
        else:
            ...
        
    def __addCommandHelper(self, eventConfig: dict, password : str, encoding : str = "utf-8"):
        for key in eventConfig.keys():
            if key == "level " + str(self._level):
                ...
    def __checkLevelPassword(self, level : int):
        eventConfig : dict = self.getEventConfig()
        if "level " + str(self._level) not in eventConfig.keys():
            ...
        eventConfig 