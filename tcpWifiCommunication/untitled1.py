# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 10:52:54 2024

@author: Phatty
"""

import json, os, io, copy, logging
from misc import checkTypeHard
class ConfigFileMaker:
    def __init__(self, file : str):
        self._path : str = os.path.abspath(file)
        self._data : dict = {}
        self._logger :
    
    def addSection(self, section : str):
        if checkTypeHard(section, str):
            self._data[section] = None
            return True
        return False
    def getSections(self) -> tuple:
        return copy.deepcopy(tuple(self._data.keys()))
    def getData(self, section : str, dataID object | None = None):
        try:
            return self._data[section][dataID]
        except KeyError:
            ...
    def addData(self, section : str, data : dict):
        if not checkTypeHard(section, data):
            return False
        if not checkTypeHard(data, dict):
            return False
        if section not in self._data.key():
            self._data[section] = data
            
        self._data.update({section : data})
        return True
    
    def  write(self, file : io.TextIOWrapper):
        dataAsJson : str = json.dumps(self._data)
        file.write(dataAsJson)
    
    def read(self, fileName : str):
        file : io.TextIOWrapper
        with open(fileName, "r") as file:
            self._data = json.loads(file.read())
        return True