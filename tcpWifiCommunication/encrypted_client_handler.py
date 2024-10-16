# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 16:22:40 2024

@author: Phatty
"""
from encrypted_socket_handler import EncryptedSocketHandler
from misc import findDevice, getConnected
import socket, copy

class EncryptedClientHandler:
    _hostDict = {"name" : None,
                 "IP Address" : None,
                  "comm" : None,
                  "port" : None
                  }
    def __init__(self, eventDictionary : dict | None = None):
        self._socket : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host : dict | None = None
        self._eventDictionary = eventDictionary
    def __del__(self):
        if self._host is None:
            self._socket.close()
    
    
    def connect(self, deviceNameOrIP : str, port : int, isLocal = True,
                numberIntervals : int = 5, intervalWaitTime : float = 1):
        if self._host is not None:
            raise RuntimeError("client has already connected to a host")
            return None
        hostName : str; hostIP : str
        hostName, hostIP = findDevice(deviceNameOrIP, isLocal=isLocal, 
                                      numberIntervals=numberIntervals, 
                                      intervalWaitTime=intervalWaitTime)
        if hostName == "" or hostIP == "":
            errorMessage : str = f"cannot find host \" {deviceNameOrIP}\""
            if isLocal:
                errorMessage = errorMessage + " on local connection"
            errorMessage = errorMessage + '.'
            raise ConnectionError()
            return None
        if not getConnected(hostIP, self._socket, port, numberIntervals=numberIntervals,
                        intervalWaitTime=intervalWaitTime):
            errorMessage : str = f"Cannot connect to \"{hostName} on port, {port}."
            errorMessage = errorMessage + "Make sure that the current port is correct"
            raise ConnectionRefusedError(errorMessage)
            return None
        
        self._host = copy.deepcopy(self._hostDict)
        self._host["name"] = hostName
        self._host["IP Address"] = hostIP
        self._host["comm"] = EncryptedSocketHandler(self._socket, self._eventDictionary)
        self._host["port"] = port
        return hostName, hostIP, port
    
    def getHost(self):
        if self._host is None:
            return None
        return self._host
        
            