# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 10:52:54 2024

@author: Phatty
"""

import json, io, copy, logging
from misc import checkTypeHard
class ConfigFileMaker:
    def __init__(self):
        self._data : dict = {}
        self._logger : logging.Logger = logging.getLogger("ConfigFileLogger")
        self._sectionCounter : int = 0
        
    def __len__(self) -> int:
        """
        gets count of all sections

        Returns
        -------
        int
            number of section

        """
        return len(self._data.keys())
    
    def __iter__(self) -> tuple:
        """
        returns an iterable with the section and data associated with section as tuple

        Yields
        ------
        tuple
            (section : str, value : dict)

        """
        key : str
        value : dict
        for key, value in self._data.items():
            yield (key, value)
        return None
    
    def __getitem__(self, section : str) -> dict | None:
        """
        gets values with associated IDs from the section

        Parameters
        ----------
        section : str
            section name as string

        Returns
        -------
        dict | None
            values with their ID

        """
        if not checkTypeHard(section, str):
            return None
        try:
            return self._data[section]
        except KeyError:
            message : str = "there is no section with name {section}."
            message = message.format(section = section)
            self._logger.error(message)
            return None
    
    def __setitem__(self, section : str, data : dict) -> dict | None:
        """
        

        Parameters
        ----------
        section : str
            DESCRIPTION.
        data : dict
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if not checkTypeHard(section, str):
            return None
        if not checkTypeHard(data, dict):
            return None
        if section not in self._data.keys():
            message : str = "there was no section with name {section}. Creating section to compensate"
            message = message.format(section = section)
            self._logger.warning(message)
        self._data[section] = data.copy()
    
    def __delitem__(self, section) -> bool:
        try:
            del self._data[section]
            return True
        except KeyError:
            message : str = "there is no section {section}"
            message = message.format(section = section)
            self._logger.error(message)
            raise KeyError(message)
            return False
    
    def __contains__(self, valueKey) -> bool | int:
        value : dict
        count : int = 0
        for value in self._data.values():
            if valueKey in value:
                count+=1
        if count == 1:
            return True
        if count > 1:
            return count
        return False
    
    def __next__(self) -> dict:
        try:
            value = self._data.values()[self._sectionCounter]
            self._sectionCounter += 1
            return value
        except IndexError:
            raise GeneratorExit()
            return None
        
        
    
    def __missing__(self, section : str) -> None:
        message : str = "there was no section with name {section}. Creating section to compensate"
        message = message.format(section = section)
        self._data[section] = None
        self._logger.warning(message)
        return None
        
    
    def addSection(self, section : str):
        """
        adds a section to the config file

        Parameters
        ----------
        section : str
            name of new section

        Returns
        -------
        bool
            returns True if section has been added
            otherwise False

        """
        if checkTypeHard(section, str):
            if section in self._data.keys():
                return False
            self._data[section] = None
            return True
        return False
    
    def getSections(self) -> tuple:
        """
        gets the sections stored in instance as tuple

        Returns
        -------
        tuple
            a tuple of the section names

        """
        return copy.deepcopy(tuple(self._data.keys()))
    
    def addData(self, section : str, data : dict):
        """
        add data to a section

        Parameters
        ----------
        section : str
            section name
        data : dict
            data as dictionary

        Returns
        -------
        bool
            DESCRIPTION.

        """
        if not checkTypeHard(section, str):
            return False
        if not checkTypeHard(data, dict):
            return False
        if section not in self._data.keys():
            message : str = "there was no section with name {section}. Creating section to compensate"
            message = message.format(section = section)
            self._logger.warning(message)
            self._data[section] = data.copy()
            return True
        if self._data[section] == None:
            self._data[section] = data.copy()
            return True
        self._data[section].update(data)
        return True
    
    def getData(self, section : str, dataID : object | None = None):
        try:
            return self._data[section][dataID]
        except KeyError:
            message : str = "There is no data with section, \"{section}\", and ID, \"{dataID}\", combination"
            message = message.format(section = section, dataID = dataID)
            self._logger.warning(message)
            raise KeyError(message)
    
    
    
    def write(self, file : io.TextIOWrapper)-> True:
        dataAsJson : str = json.dumps(self._data)
        file.write(dataAsJson)
        return True
    def send(self) -> str:
        return json.dumps(self._data)
    
    def read(self, file : io.TextIOWrapper)-> bool:
        self._data = json.loads(file.read())
        return True
    
    def recieve(self, dataAsJsonString : str) -> bool:
        try:
            self._data = json.loads(dataAsJsonString)
            return True
        except json.JSONDecodeError:
            message : str = "\"" + str(dataAsJsonString) + "\" is not a valid json string"
            self._logger.error(message)
            return False