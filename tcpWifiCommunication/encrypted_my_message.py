# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:58:53 2024

@author: Phatty
"""
# To do: fix AES madness 8/27/2024! ✓
# To do: check if EncryptedMyMessage is compatible with parent MyMessage messages
# To do: add a reset whos the boss function(s) and command
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
    _RESKEYSIZE = 2048 #*2 
    _MAXENCRYPTIONSENDTIMES = 3
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
        self._numberOfTimesTriedToSendEncryption : int = 0
        
        self._sendKey : rsa.PublicKey | None = None
        self._recieveKey : rsa.PrivateKey | None = None
        self._rsaEstablished : bool = False
        
        self._encryptionMode = None
        
        self._aesKey : bytes | None = None
        self._aesCipher : Cryptodome.Cipher._mode_cbc.CbcMode | None = None
        self._isBoss : dict = {"currentBossNumber" : None, 
                                "recievedBossNumber" : None,
                                "isBoss" : None}
        
        
        #function to initalize MyMessage parent
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
        print("generating boss number...")
        if self._isBoss["currentBossNumber"] is not None:
            print("there is already a generated boss number")
            return False
        self._isBoss["currentBossNumber"] = random.randint(0, self._AESKESIZE**2)
        command : dict = {"command" : "bossID", "ID" : None,
                          "data": { "currentBossNumber" : self._isBoss["currentBossNumber"]},
                          "hasPriority" : True}
        self._commandQue.insert(0, command)
        print("added boss number to que")
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
        print("recieved a boss number")
        recievedBossNumber : int = messageRecieved["data"]["currentBossNumber"]
        self._isBoss["recievedBossNumber"] = recievedBossNumber
        if self._isBoss["currentBossNumber"] is None:
            print("this instance does not yet have a boss number to compare to")
            self._generateBossNumber()
        if recievedBossNumber > self._isBoss["currentBossNumber"]:
            print("This instance is not the boss")
            self._isBoss["isBoss"] = False
            return False
        elif recievedBossNumber < self._isBoss["currentBossNumber"]:
            print("this instance is the boss")
            self._isBoss["isBoss"] = True
            return True
        else:
            print("received and generated the same number. Restarting whos the boss protocol")
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
        print("creating new RSA keys")
        if self.findCommandFromName("newRSA"):
            return False
        publicKey : rsa.PublicKey
        publicKey, self._recieveKey = rsa.newkeys(self._RESKEYSIZE,poolsize=2)
        data : dict = {"publicKey" : publicKey.save_pkcs1("PEM").decode(encoding),
                       "encoding" : encoding} #created a varible because might possibly add more data
        super(EncryptedMyMessage, self).command("newRSA", data, hasPriority)
        print("RSA keys created")
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
        print("recieving an RSA key")
        key : str = messageRecieved["data"]["publicKey"]
        encoding : str = messageRecieved["data"]["encoding"]
        self._sendKey = rsa.PublicKey.load_pkcs1(key.encode(encoding))
        self._encryptionMode = "RSA"
        self._acceptDecline(messageRecieved, 1, None)
        print("sending a accepting message and converting to RSA")
    
    def _RSAExists(self) -> bool:
        return False if self._sendKey is None else True
        

#-----------Creation of AES encryption and key------------------
    def isBothRSAKeysValid(self):
        """
        checks if the full rsa encryption has been established

        Returns
        -------
        bool
            DESCRIPTION.

        """
        try:
            assert self._encryptionMode is not None
            RSADictionary : dict = self.findCommandFromName("newRSA")[0] #command name and ID
            RSAInfo : dict = self.getCommandInfo(RSADictionary)
            if RSAInfo["hasAccept"] == True and self._sendKey is not None:
                print("Two way RSA has been established")
                self._commandIDs.pop(RSADictionary["ID"])
                self._rsaEstablished = True
                
                return True
            return False
        except IndexError:
            return self._rsaEstablished
        except AssertionError:
            return False
        
    def _checkCanMakeAES(self):
        """
        checks if AES encryption can be established here are the rules:
            1) Uses the isBothRSAKeysValid function to check if RSA has been Established
            2) Generates a boss number that determines which of the two device will generate the key
            3) Sends or recieves a generated key
        Returns
        -------
        bool
            DESCRIPTION.

        """
        if self._aesKey is not None:
            return False
        if self.isBothRSAKeysValid():
            if self._isBoss["isBoss"] is None:
                self._generateBossNumber()
                return False
            self._generateAESKey()
            return True
        return False
    
    def reGenAESKey(self):
        if self.isBothRSAKeysValid():
            self._generateAESKey()
    
    def _generateAESKey(self, saltEndianness : str = 'big'):
        if self._isBoss["isBoss"] is True:
            print("generating AES key...")
            password = getRandomString(self._AESKESIZE)
            salt : bytes = os.urandom(self._AESKESIZE)
            self._aesKey = AES_PBKDF2(password, salt, dkLen=self._AESKESIZE)
            self._aesCipher = AES.new(self._aesKey,AES.MODE_CBC)
            data : dict = {"password" : password,
                           "salt" : int.from_bytes(salt, saltEndianness),
                           "sLength" : self._AESKESIZE,
                           "sEndian" : saltEndianness}
            super(EncryptedMyMessage, self).command("newAES", data)
            print("AES key generated and add to the que to be sent...")
            return True
        return False
    
    def _getAES(self, messageRecieved : dict):
        print("recieved AES command")
        password : str = messageRecieved["data"]["password"]
        salt : bytes | int = (messageRecieved["data"]["salt"])
        salt = salt.to_bytes(messageRecieved["data"]["sLength"],
                             messageRecieved["data"]["sEndian"])
        self._aesKey = AES_PBKDF2(password, salt,dkLen=self._AESKESIZE)
        self._aesCipher = AES.new(self._aesKey,AES.MODE_CBC)
        print("AES encryption added")
        self._acceptDecline(messageRecieved, 1 , {"boss number" : self._isBoss["currentBossNumber"]})
        #can send the accepting message as AES because the sender of the newAES command already has
        #the encryption key and can decrypted the accepting message without prior understanding
        self._encryptionMode = "AES"
    
    def _AESExists(self) -> bool:
        return False if self._aesKey is None else True
        
        
    


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
        print("Encrypting message using the AES protocol...")
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
        messageToSend = self._aesCipher.encrypt(cryptPad(messageToSend, AES.block_size))
        print("message encrypted")
        for message in tuple(self._getEncodingMessage(messageToSend, encrypt = "AES")):
            yield message
        return None
        
    
    def _sendRSAEncrypted(self) -> tuple:
        print("Encrypting message using the RSA protocol...")
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
        messageToSend = rsa.encrypt(messageToSend, self._sendKey)
        print("message encrypted.")
        for message in tuple(self._getEncodingMessage(messageToSend, encrypt = "RSA")):
            
            yield message
        return None
#-----------------decryption methodes------------
    def decryptAES(self, message):
        self._logger.debug("decrypting AES encrypted message...")
        iv : bytes = message[0:AES.block_size]
        messageToDecrypt : bytes = message[AES.block_size:]
        decipher : Cryptodome.Cipher._mode_cbc.CbcMode = AES.new(self._aesKey, AES.MODE_CBC, iv=iv)
        return cryptUnpad(decipher.decrypt(messageToDecrypt), AES.block_size)
        
    def decryptRSA(self, message):
        self._logger.debug("decrypting RSA encrypted message...")
        return (rsa.decrypt(message, self._recieveKey)).decode(self._ENCODINGMESSAGEENCODING)

#----------------command method------------------------
    def command(self, commandName : str, data : dict | None,  hasPriority : bool = False) -> dict | None:
        match commandName:
            case "newRSA":
                self._getNewRSAEncryption()
                return {"command" : "newRSA", "ID" : None}
            case "newAES":
                if self._checkCanMakeAES():
                    return {"command" : "newAES", "ID" : None}
                self._logger.warning("AES encryption cannot be created until communication through RSA has been established")
                return {"command" : None, "ID" : None}
            case "bossID":
                self._logger.warning("\"bossID\" command cannot be used since it is being used for a builtin command.")
                return {"command" : None, "ID" : None}
            case _:
                return super(EncryptedMyMessage, self).command(commandName, data, hasPriority)
            

#-------------send methods--------------------------
    
            
    def send(self):
        while len(self._commandQue):
            self._checkCanMakeAES()
            messageGenerator = None
            if self._aesKey is not None and self._encryptionMode == "AES":
                messageGenerator = self._sendAESEncrypted()
            #fix this
            elif self._sendKey is not None and self._encryptionMode == "RSA":
                messageGenerator = self._sendRSAEncrypted()
            else:
                if self._numberOfTimesTriedToSendEncryption <= self._MAXENCRYPTIONSENDTIMES:
                    self._logger.warning("Messages cannot be encrypted. Anyone can view the message")
                messageGenerator = self._getMessageToSend()
            for message in messageGenerator:
                yield message
        return None

#-----------------recieve methodes----------------

    def _setEncodingFromMessage(self, recievedMessage : str):
        self._logger.debug("recieved an encoding message")
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
                 if "newAES" == returnValue["command"]:
                     print("The other instance excepted the AES encryption")
                     self._encryptionMode = "AES"
            case "decline":
                returnValue = self._getAcceptAndDecline(recvMessage)
                if "newRSA" == returnValue["command"] and self._numberOfTimesTriedToSendEncryption < self._MAXENCRYPTIONSENDTIMES:
                    self._encryptionMode = None
                    self._getNewRSAEncryption()
                    self._numberOfTimesTriedToSendEncryption += 1
                    
                
            case "error":
                returnValue = self._getAcceptAndDecline(recvMessage)    
                if "newRSA" == returnValue["command"] and self._numberOfTimesTriedToSendEncryption < self._MAXENCRYPTIONSENDTIMES:
                    self._encryptionMode = None
                    self._getNewRSAEncryption()
                    self._numberOfTimesTriedToSendEncryption += 1
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