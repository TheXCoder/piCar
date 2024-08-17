# -*- coding: utf-8 -*-
"""
Created on Sun May 12 16:26:18 2024

@author: Phatty
"""

import socket, logging, time
from file_socket import FileSocket
from misc import *
class ClientHandler(FileSocket):
    def __init__(self, eventsDictionary : dict = None,
                 folderToSaveFilesDIR : str = None):
        #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super(ClientHandler, self).__init__(None, eventsDictionary, folderToSaveFilesDIR)
                
        
        
        