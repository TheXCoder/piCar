# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:58:53 2024

@author: Phatty
"""
# To do: fix AES madness 8/27/2024! ✓
# To do: comments and doc strings
import rsa, json, os, random#, logging
from misc import getRandomString, classDocstring
from my_message import MyMessage
from command import Command 
import Cryptodome.Cipher
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2 as AES_PBKDF2
from Cryptodome.Util.Padding import pad as cryptPad, unpad as cryptUnpad

def checkKeyForKeyValue(dictionary : dict, key):
    try:
        return dictionary[key]
    except KeyError:
        return "__keyError__"

_EncryptedMyMessageDocString : str = \
"""
Keeps message data private via encryption

"""
class EncryptedMyMessage(MyMessage):
    """
    A better MyMessage for a better future
    Keeps message private via encryption

    """
    __doc__ += "\n\n" + MyMessage.__doc__
    _AESKESIZE = 32
    _RESKEYSIZE = 2048
    def __init__(self, eventsDictionary : dict | None = None):
        """
        A security class to deal with encryption

        Parameters
        ----------
        eventsDictionary : dict | None, optional
            events can be attached to commands using dictionaries. The default is None.
            see MyMessage __doc__ for more information
        """
        self._nextMessageEncryptionType : str | None = None # determines the recieved message type sent as an addon to the encoding message
        self.__sendKey : rsa.PublicKey | None = None
        self.__recieveKey : rsa.PrivateKey | None = None
        self.__aesKey : bytes | None = None
        self.__aesCipher : Cryptodome.Cipher._mode_cbc.CbcMode | None = None
        self._isBoss : dict = {"currentBossNumber" : None, 
                                "recievedBossNumber" : None,
                                "isBoss" : None}
        
        
        #function to initalize EncryptedMyMessage
        super(EncryptedMyMessage , self).__init__(eventsDictionary)
        self._getNewRSAEncryption()
    
    
         

#-----------whose the boss functions-------------
    def _generateBossNumber(self) -> bool:
        """
        creates a random number to determine which MyMessage instance
        is the current boss of the other

        Returns
        -------
        bool
            True if the boss has not been determined, otherwise false

        """
        if self._isBoss["currentBossNumber"] is not None:
            return False
        self._isBoss["currentBossNumber"] = random.randint(0, self._AESKESIZE**2)
        command : dict = {"command" : "bossID", "ID" : None,
                          "data": { "currentBossNumber" : self._isBoss["currentBossNumber"]},
                          "hasPriority" : True}
        self._commandQue.insert(0, command)
        return True
    
    def _getBossNumber(self, messageRecieved : dict) -> bool | None:
        """
        processes the boss random number sent by the other instance of MyMessage
        and determines if this instance is the boss

        Parameters
        ----------
        messageRecieved : dict
            message recieved from other instance

        Returns
        -------
        bool
            True if this instance is boss
            False if this instance is not the boss
            
            None if this instance and the other instance have the same random
            boss number. It will also resend the boss number if that is the case
        """
        recievedBossNumber : int = messageRecieved["data"]["currentBossNumber"]
        self._isBoss["recievedBossNumber"] = recievedBossNumber
        
        if self._isBoss["currentBossNumber"] is None:
            self._generateBossNumber()
        
        if recievedBossNumber > self._isBoss["currentBossNumber"]:
            self._isBoss["isBoss"] = False
            return False
        elif recievedBossNumber < self._isBoss["currentBossNumber"]:
            self._isBoss["isBoss"] = True
            return True
        else:
            self._isBoss["isBoss"] = None
            self._isBoss["currentBossNumber"] = None
            self._isBoss["recievedBossNumber"] = None
            self._generateBossNumber()
            return None

#---------------RSA encryption and key generation-------------
    def _getNewRSAEncryption(self, encoding : str = "utf-8", hasPriority : bool = True) -> bool:
        """
        makes generates RSA keys and sends them to the othe MyMessage instance
        to create a secure connection

        Parameters
        ----------
        encoding : str, optional
            the encoding of public key. The default is "utf-8".
        hasPriority : bool, optional
            Priority of the command. The default is True.

        Returns
        -------
        bool
            True if newRSA and keys will be generated.
            False if RSA newRSA is already in the que to be sent

        """
        if self.findCommandFromName("newRSA"):
            return False
        publicKey : rsa.PublicKey
        publicKey, self.__recieveKey = rsa.newkeys(self._RESKEYSIZE,poolsize=2)
        data : dict = {"publicKey" : publicKey.save_pkcs1("PEM").decode(encoding),
                       "encoding" : encoding} #created a varible because might possibly add more data
        self.command("newRSA", data, hasPriority)
        return True
    
    def _getRSA(self, messageRecieved : dict):
        """
        recieves and proccess newRSA message from the other MyMessage instance

        Parameters
        ----------
        messageRecieved : dict
            D

        Returns
        -------
        None.

        """
        key : str = messageRecieved["data"]["publicKey"]
        encoding : str = messageRecieved["data"]["encoding"]
        self.__sendKey = rsa.PublicKey.load_pkcs1(key.encode(encoding))
        self._acceptDecline(messageRecieved, 1, None)
        

#-----------Creation of AES encryption and key------------------
    def isBothRSAKeysValid(self):
        try:
            RSADictionary : dict = self.findCommandFromName("newRSA")[0] #command name and ID
            RSAInfo : dict = self.getCommandInfo(RSADictionary)
            if RSAInfo["hasAccept"] == True and self.__sendKey is not None:
                self._commandIDs.pop(RSADictionary["ID"])
                return True
            return False
        except IndexError:
            return False
        
    def _checkCanMakeAES(self):
        if self.__aesKey is not None:
            return False
        if self._isBoss["isBoss"] is None:
            self._generateBossNumber()
            return False
        if self.isBothRSAKeysValid():
            self._generateAESKey()
            return True
        return False
    
    def _generateAESKey(self, saltEndianness : str = 'big'):
        if self._isBoss["isBoss"] is True:
            password = getRandomString(self._AESKESIZE)
            salt : bytes = os.urandom(self._AESKESIZE)
            self.__aesKey = AES_PBKDF2(password, salt, dkLen=self._AESKESIZE)
            self.__aesCipher = AES.new(self.__aesKey,AES.MODE_CBC)
            data : dict = {"password" : password,
                           "salt" : int.from_bytes(salt, saltEndianness),
                           "sLength" : self._AESKESIZE,
                           "sEndian" : saltEndianness}
            self.command("newAES", data)
            return True
        return False
    def _getAES(self, messageRecieved : dict):
        password : str = messageRecieved["data"]["password"]
        salt : bytes | int = (messageRecieved["data"]["salt"])
        salt = salt.to_bytes(messageRecieved["data"]["sLength"],
                             messageRecieved["data"]["sEndian"])
        self.__aesKey = AES_PBKDF2(password, salt,dkLen=self._AESKESIZE)
        self.__aesCipher = AES.new(self.__aesKey,AES.MODE_CBC)
        
    


#------------generate encodingMessage---------------
    def _getEncodingMessage(self, messageOrEncodeMessage : str, **kwargs) ->tuple:
        """
        creates an encoding message determined by the message size and encoding
        will recursively generate messages until encoding message can display
        the correct size

        Parameters
        ----------
        messageOrEncodeMessage : str
            message, usually in the form of a json message
            
            used by function only(or the encoding message for recursive creation)
        **kwargs
        --------
        encryptionType/encryption/encrypt - the message encryption        

        Returns
        -------
        tuple
            the encoding message(s) and the messageOrEncodingMessage variable
        
        Additional Information
        ----------------------
        the encoding message should look like
        size[int]code[str];
        example: "szie256codeutf-8;"
        

        """
        encryptionType : str | None = None
        encryptionType = checkKeyForKeyValue(kwargs, "encryptionType")
        if encryptionType == "__keyError__":
            encryptionType = checkKeyForKeyValue(kwargs, "encryption")
        if encryptionType == "__keyError__":
            encryptionType = checkKeyForKeyValue(kwargs, "encrypt")
        if encryptionType == "__keyError__":
            encryptionType = None
    
        messageSize = len(messageOrEncodeMessage)
        encodingMessage = "size" + str(messageSize) + "code" + self._ENCODINGMESSAGEENCODING +";" #creates encoding message
        if isinstance(encryptionType, str):
            encodingMessage +="encrypt" + encryptionType + ";"
        if len(encodingMessage) > self._ENCODINGMESSAGESIZE: #if encoding message is to big to be a normal encoding message
            encodingMessage = encodingMessage.replace("size", "lmf size") # replace normal encoding with large message format encoding
            return *self._getEncodingMessage(encodingMessage), messageOrEncodeMessage #recursive until an encoding message meets encoding message size
        return encodingMessage, messageOrEncodeMessage

#-----------------encrypt methods----------------------------
    def _sendAESEncrypted(self) -> None:
        command : dict = self._commandQue[0]
        if command["command"] == "newAES":
            for message in tuple(self._sendRSAEncrypted()):
                yield message
            return None
        del self._commandQue[0]
        messageToSend : str | bytes = json.dumps(command)
        debugInfo : str = "sending AES encrypted message \"{commandName}\" with ID {commandID}."
        debugInfo = debugInfo.format(commandName = command["command"], commandID = command["ID"])
        self._logger.debug(debugInfo)
        messageToSend = (' ' * AES.block_size)+ messageToSend
        messageToSend = messageToSend.encode(self._ENCODINGMESSAGEENCODING)
        messageToSend = self.__aesCipher.encrypt(cryptPad(messageToSend, AES.block_size))
        for message in tuple(self._getEncodingMessage(messageToSend, encrypt = "AES")):
            yield message
        return None
        
    
    def _sendRSAEncrypted(self) -> tuple:
        command : dict = self._commandQue.pop(0)
        if command["command"] == "newRSA":
            messageToSend : str = json.dumps(command) # converts sent command as dictionary to json
            for message in tuple(self._getEncodingMessage(messageToSend)):
                yield message
            return None
        messageToSend : str | bytes = json.dumps(command) # converts sent command as dictionary to json
        debugInfo : str = "sending RSA encrypted message \"{commandName}\" with ID {commandID}."
        debugInfo = debugInfo.format(commandName = command["command"], commandID = command["ID"])
        self._logger.debug(debugInfo) # logs that the message is being sent
        messageToSend = messageToSend.encode(self._ENCODINGMESSAGEENCODING)
        messageToSend = rsa.encrypt(messageToSend, self.__sendKey)
        for message in tuple(self._getEncodingMessage(messageToSend, encrypt = "RSA")):
            yield message
        return None
#-----------------decryption methodes------------
    def decryptAES(self, message):
        self._logger.debug("decrypting AES encrypted message")
        iv : bytes = message[0:AES.block_size]
        messageToDecrypt : bytes = message[AES.block_size:]
        decipher : Cryptodome.Cipher._mode_cbc.CbcMode = AES.new(self.__aesKey, AES.MODE_CBC, iv=iv)
        return cryptUnpad(decipher.decrypt(messageToDecrypt), AES.block_size)
        
    def decryptRSA(self, message):
        self._logger.debug("decrypting RSA encrypted message")
        return (rsa.decrypt(message, self.__recieveKey)).decode(self._ENCODINGMESSAGEENCODING)

#-------------send methods--------------------------
    
            
    def send(self):
        while len(self._commandQue):
            messageGenerator = None
            if self.__aesKey is not None:
                messageGenerator = self._sendAESEncrypted()
            elif self.__sendKey is not None:
                messageGenerator = self._sendRSAEncrypted()
            else:
                messageGenerator = self._getMessageToSend()
            for message in messageGenerator:
                yield message
        return None

#-----------------recieve methodes----------------

    def _setEncodingFromMessage(self, recievedMessage : str):
        if not isinstance(recievedMessage, str):
            return False
        if "size" in recievedMessage or "lmf size" in recievedMessage:
            #set variables
            startSizeSubstring : int = recievedMessage.find("size") + 4
            startEncodingSubstring : int = recievedMessage.find("code") + 4
            endEncodingSubstring : int = recievedMessage.find(';')
            #
            self._currentMessageSize = int(recievedMessage[startSizeSubstring : startEncodingSubstring - 4])
            self._currentMessageEncoding = recievedMessage[startEncodingSubstring : endEncodingSubstring]
            if "encrypt" in recievedMessage:
                startEncryptionSubstring : int = recievedMessage.find("encrypt") + 7
                endEncryptionSubstring : int = recievedMessage[startEncryptionSubstring:].find(';') + startEncryptionSubstring
                self._nextMessageEncryptionType = recievedMessage[startEncryptionSubstring: endEncryptionSubstring]
                
            return True
        return False
    
    def _getDecryptedMessage(self, recievedMessage : str) -> str:
        if self._nextMessageEncryptionType == "AES":
            return self.decryptAES(recievedMessage)
        elif self._nextMessageEncryptionType == "RSA":
            return self.decryptRSA(recievedMessage)
        return recievedMessage
    
    def recv(self, recievedMessage : str):
        #checks message encoding
        if self._setEncodingFromMessage(recievedMessage):
            return {"command" : None, "ID" : None} #returns this so that the message settings are not reset look down ↓
        #decrypts message
        if self._nextMessageEncryptionType is not None:
            recievedMessage = self._getDecryptedMessage(recievedMessage)
        
        self._checkCanMakeAES()
        
        #processes recieved message
        returnValue : dict | None = {"command" : None, "ID" : None}
        recvMessage : dict = json.loads(recievedMessage)
        match recvMessage["command"]:
            case "echo":
                self._returnEcho(recvMessage)
                returnValue = None
            case "reply":
                self._getReply(recvMessage)
            #newly added functions
            case "newRSA":
                self._getRSA(recvMessage)
            case "newAES":
                self._getAES(recvMessage)
            case "bossID":
                self._getBossNumber(recvMessage)
            case "accept":
                 returnValue = self._getAcceptAndDecline(recvMessage)
            case "decline":
                returnValue = self._getAcceptAndDecline(recvMessage)
            case "error":
                returnValue = self._getAcceptAndDecline(recvMessage)        
            case _:
                try:
                    self._getCommandMessage(recvMessage)
                except KeyError:
                    logMessage : str = "\"{commandName}\" does not have a function associated with it."
                    logMessage.format(commandName = recvMessage["command"])
                    command : Command = Command("decline", recvMessage["ID"], None, recvMessage["hasPriority"])
                    self._addToQue(command, recvMessage["hasPriority"])
                    self._logger.warning(logMessage)
        #resets message setting so that next message can be sent
        self._currentMessageSize : int = 0
        self._currentMessageEncoding : str = ""
        self._nextMessageEncryptionType = None
        return returnValue