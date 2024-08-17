# -*- coding: utf-8 -*-
"""
Created on Sun May 12 16:26:18 2024

@author: Phatty
"""

import socket, logging
from file_socket import FileSocket
class ClientHandler(FileSocket):
    def __init__(self, eventsDictionary : dict = None,
                 folderToSaveFilesDIR : str = None):
        super(ClientHandler, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                            eventsDictionary, folderToSaveFilesDIR)
        
        