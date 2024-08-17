# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 13:37:30 2024

@author: Phatty
"""

from socket_handler import SocketHandler
import socket, rsa, logging, json

class RSASocketHandler(SocketHandler):
    __RSAENCRYPTIONTYPE = 1024
    def __init__(self, deviceSocket : socket.socket, eventsDictionary : dict = None):
        super(RSASocketHandler,self).__init__(deviceSocket, eventsDictionary)
        self._logger.info("Generating Keys...")
        
        #for receiving encyrpted messages
        self.__publicKey : rsa.PublicKey;
        self.__privateKey : rsa.PrivateKey;
        self.__encryptRecv : bool = False
        self.__publicKey, self.__privateKey = rsa.newkeys(RSASocketHandler.__RSAENCRYPTIONTYPE)
        
        #for sending encrypted message
        self.__sendPublicKey : rsa.PublicKey = None
        self.__encryptSend : bool = False
        
        
        self.__sendPublicKey()
        
    
    def __sendPublicKey(self) -> None:
        """
        generates a message to be sent with the current public key

        Returns
        -------
        None
            DESCRIPTION.

        """
        self.command("nKey", self.__publicKey)
        return None
    
#--------sending methods---------------#
    def encryptMessage(self, message : str, messageEncoding : str = "utf-8"):
        if not self.__encryptRecv:
            raise TypeError("message cannot be encrypted")
        if not isinstance(self.__recvPublicKey, rsa.PublicKey):
            ...
    def nextMessage(self):
        # while True:
        #     try:
        #         assert self._socket is not None
        #         message : str; encoding : str
        #         message, encoding = next(super(SocketHandler, self).nextMessage())
        #         self._socket.send(message.encode(encoding))
                
        #         #termanates self if accepted the end communication
        #         try:
        #             messageData = json.loads(message)
        #             if messageData["command"] == "acct":
        #                 if messageData["data"]["command"] == "endc":
        #                     self._closeSocket()
        #                     return None
        #         except json.JSONDecodeError:
        #             ...
        #         yield True
        #     except StopIteration: 
        #         ...
        #     except AssertionError:
        #         self._logger.error("socket cannot send messages because it has been terminated within the instance or has never existed")
        #         raise RuntimeError("socket does not exist within the instance")
        #     return False
        while True:
            try:
                assert self._socket is not None
                message : str; encoding : str
                message, encoding = next(super(SocketHandler, self).nextMessage())
                self._socket.send(message.encode(encoding))
                
                #termanates self if accepted the end communication
                try:
                    messageData = json.loads(message)
                    if messageData["command"] == "acct":
                        if messageData["data"]["command"] == "endc":
                            self._closeSocket()
                            return None
                except json.JSONDecodeError:
                    ...
                yield True
            except StopIteration: 
                ...
            except AssertionError:
                self._logger.error("socket cannot send messages because it has been terminated within the instance or has never existed")
                raise RuntimeError("socket does not exist within the instance")
            return False
    
    
    
    