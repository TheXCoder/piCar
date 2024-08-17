# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 22:06:10 2024

@author: Phatty
"""
import os, json, time
from misc import generateHash, createDirectory, splitHashSalt



class LockedEvent:
    def __init__(self, event : dict):
        """
        Handles events that require a password

        Parameters
        ----------
        event : dict
            an event for the MyMessage library
        
        event
        -----
        items in dictionary requirement {[str] command name : [function(dict | None) -> int, dict|None]} a valid function that has

        Returns
        -------
        instance

        """
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")
        self._command : str | None = None
        self._function = None
        if len(event.items()) == 1:
            self._command = list(event.keys())[0]
            if callable(event[self._command]):
                self._function = event[self._command]
            else:
                raise TypeError("function in event must be callable")
            if not isinstance(self._command, str):
                raise TypeError("command name in event must be a <str>")
                self._command = None
        else:
            raise TypeError("event must be a single {command:function} pair")
        
    
        