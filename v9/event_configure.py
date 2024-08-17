# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 20:02:52 2024

@author: Phatty
"""
from locked_file import LockedFile
import configparser, os, copy
class ConfigParsePuller:
    def __init__(self):
        self.__data : str = ""
    def write(self, data):
        self.__data += data
    @property
    def data(self):
        return self.__data
    @data.getter
    def data(self):
        returnData = self.__data
        self.__data = ""
        return returnData
    
class LockedFileConfigParseConverter(LockedFile):
    def __init__(self, file : str, password : str | None = None,
                 textEncoding : str = "utf-8"):
        self._config : configparser.ConfigParser = configparser.ConfigParser()
        super(LockedFileConfigParseConverter, self).__init__(file, password, textEncoding)
    
    def load(self, password : str | None = None, encoding : str = "utf-8"):
        self._config.read_string(self.read(password = password, textEncoding=encoding))
    
    def save(self, password : str | None = None, textEncoding : str = "utf-8"):
        password = "" if password is None else password
        passwordGood = self._checkPassword(password, textEncoding)
        if self._checkFolderMode() in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self._checkFolderMode() in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure mode")
            return None
        if self.checkFileMode() in ("r", "rs"):
            raise PermissionError("directory is in a read-only mode")
            return None
        if self.checkFileMode() in ("ws", "s") and not passwordGood:
            raise PermissionError("file is in a secure mode")
            return None
        puller : ConfigParsePuller = ConfigParsePuller()
        self._config.write(puller)
        self.write(puller.data, False, password, textEncoding)
    
    @property
    def config(self) -> configparser.ConfigParser:
        return self._config
    @config.getter
    def config(self) -> dict:
        return {s:dict(self._config.items(s)) for s in self._config.sections()}
    @config.setter
    def config(self, data : tuple):
        self._config[data[0]] = data[1]
        

class EventConfigure:
    _MyMessageConfigDir = "myMessage"
    _configFile = _MyMessageConfigDir + os.sep + "events.ini"
    _configDict : dict = {"commands" : "",
                          "password" : "",
                          "keys" : ""}
    def __init__(self, commandName : str, lockLevel : int = 0):
        self.__lockLevel : int = lockLevel
        self.__commandName : str = commandName
        self._file : LockedFileConfigParseConverter = LockedFileConfigParseConverter(self._configFile)
        print(self.__makeConfigFile())

    def __makeConfigFile(self) -> bool:
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