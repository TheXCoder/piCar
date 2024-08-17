# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 17:08:13 2024

@author: Phatty
"""
import os, io
class EncryptFile():
    
    def __init__(self, filename : str):
        self._filename : str = filename
        self.file : io.TextIOWrapper | None = None 
        self._password : str = ''
        self._hash : bytes = bytes()
        if not self._doesFileExist():
            file = open(self._filename, 'x')
            file.close()
    def _doesFileExist(self) -> bool:
        return os.path.exists(self._filename)