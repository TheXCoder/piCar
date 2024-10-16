# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:40:52 2024

@author: Phatty
"""

from encrypted_socket_handler import EncryptedSocketHandler
from misc import findDevice, checkTypeHard
import socket, copy

class EncryptedServerHandler():
    _deviceDict = {"name" : None,
                   "IP Address" : None,
                  "comm" : None,
                  "port" : None
                  }
    def __init__(self, port : int, amountOfClients : int = 1, eventDictionary : dict | None = None):
        self._listeningPort : int = port
        self._hostname : int = socket.gethostname()
        self._hostIP : int = socket.gethostbyname(self._hostname)
        self._devices : dict = {}
        self._eventDictionary : dict | None = eventDictionary
        
        self._listeningSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listeningSocket.bind((self._hostIP, self._listeningPort))
        self._listeningSocket.listen(amountOfClients)
    
    def __del__(self):
        self._listeningSocket.close()
    def acceptADevice(self):
        clientSocket : socket.socket; clientInfo : tuple
        clientSocket, clientInfo = self._listeningSocket.accept()
        clientPort : int; clientIP : str; clientName : str
        clientIP, clientPort = clientInfo
        clientName, _ = findDevice(clientIP)
        if clientName in self._devices.keys():
            if isinstance(self._devices[clientName], list):
                self._devices[clientName] = [*self._devices[clientName],copy.deepcopy(self._deviceDict)]
            else:
                self._devices[clientName] = [self._devices[clientName],copy.deepcopy(self._deviceDict)]
            self._devices[clientName][-1]["name"] = clientName
            self._devices[clientName][-1]["IP Address"] = clientIP
            self._devices[clientName][-1]["comm"] = EncryptedSocketHandler(clientSocket, self._eventDictionary)
            self._devices[clientName][-1]["port"] = clientPort
            
        else:
            self._devices[clientName] = copy.deepcopy(self._deviceDict)
            self._devices[clientName]["name"] = clientName
            self._devices[clientName]["IP Address"] = clientIP
            self._devices[clientName]["comm"] = EncryptedSocketHandler(clientSocket, self._eventDictionary)
            self._devices[clientName]["port"] = clientPort
        return clientName, clientIP, clientPort
    def getDevice(self, deviceName : str, port : int = None) -> dict:
        """
        gets device data using the name

        Parameters
        ----------
        deviceName : str
            name of the device

        Returns
        -------
        device : dict
            device data as dictionary
            {"IP Address" : [str] the device's IP address,
             "comm" : [EncryptedSocketHandler] the communication for the device,
             "port" : int the port to which the device is being hosted at}

        """
        if deviceName not in self._devices.keys():
            return None
        if not isinstance(self._devices[deviceName], list):
            return self._devices.pop(deviceName)
        if port is None:
            return self._devices.pop(deviceName).pop(0)
        if not checkTypeHard(port, int) and port < 0:
            return None
        deviceData : list
        for index, deviceData in enumerate(self._devices[deviceName]):
            if deviceData["port"] == port:
                return self._devices[deviceName].pop(index)
        return None
    
    def nextDevice(self):
        for deviceName, deviceData in self._devices.items():
            if isinstance(deviceData, list):
                deviceData : list;
                for devicePortData in deviceData:
                    yield deviceName, devicePortData
            else:
                yield deviceName, deviceData
        return None
        
        
    
    def __enter__(self):
        return self