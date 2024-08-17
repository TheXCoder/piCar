# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 11:16:51 2024

@author: Phatty
"""
import logging
import datetime
class MyLogger:
    _MASTERCONFIG = {
        "version":1,
        "disable_existing_loggers" : False,
        "handlers" : {...},
        "loggers" : {...}
        }
    _masterLogger : logging.Logger = None
    
    def __init__(self, name : str = None, fileToLog : str = None):
        if name is None:
            currentTime = datetime.datetime.now()
            name = "logger__"
            name += str(currentTime.month) + '_' + str(currentTime.date) + '_' + str(currentTime.year)
            name += '__' + str(currentTime.hour) + '_' + str(currentTime.min) + '_' + str(currentTime.second)
        fileToLog =  name + '.log' if fileToLog is None else fileToLog
        self._name = name
        self._fileToLog = fileToLog
        self._logger : logging.Logger = logging.getLogger(name)
        self._logger
    def printInfo(self, msg):
        print(msg)
        self._logger.info("info printed to console")
        self._logger.info(msg)
        
    