#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 00:26:34 2024

@author: goduser
"""

import threading

class MyThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=(), Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self.__returnValue__ = None
    def run(self):
        if self.target != None:
            self.__returnValue__ = self.target(*self.__args, **self.__kwargs)
    
    @property
    def returnValue(self, value):
        return self.__returnValue__