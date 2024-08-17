#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 15:05:52 2024

@author: goduser
"""

class Message:
    def __init__(self, messageSize : int = 4096, messageEncoding : str = 'utf-8'):
        """
        

        Parameters
        ----------
        messageSize : int, optional
            DESCRIPTION. The default is 4096.
        messageEncoding : str, optional
            DESCRIPTION. The default is 'utf-8'.

        Returns
        -------
        None.

        """
        self.__messageSize__ : int = 32 if messageSize < 32 else messageSize
        self.__messageEncoding__ : str= messageEncoding
        self.__newMessageSize__ : int = None
        self.__newMessageEncoding__ : str = None
    
    def generateMessage(self, text:str):
        """
        

        Parameters
        ----------
        text : str
            DESCRIPTION.

        Raises
        ------
        ValueError
            DESCRIPTION.

        Returns
        -------
        str or None
            DESCRIPTION.

        """
        if len(text) > self.__messageSize__:
            raise ValueError("message is greater then alloted size")
            return None
        return text.format(self.__messageEncoding__)
    
    def generateEncodingMessage(self, messageSize : int = 4096, messageEncoding : str = 'utf-8'):
        encodingMessage = "prot:size="
        self.__newMessageSize__ = 32 if messageSize < 32 else messageSize
        self.__newMessageEncoding__ = messageEncoding
        encodingMessage += str(self.__newMessageSize__) + ';' + "code=" +self.__newMessageEncoding__ + ';'
        if len(encodingMessage) > self.__messageSize__:
            raise ValueError("message is greater then alloted size")
            return None
        return encodingMessage.format(self.__messageEncoding__)
    def generateClosingMessage(self):
        closingMessage = "entr:"
        return closingMessage.format(self.__messageEncoding__)
    
    def isEncodingMessageAccepted(self, acceptStatus: bool):
        if acceptStatus:
            self.__messageSize__ = self.__newMessageSize__
            self.__messageEncoding__ = self.__newMessageEncoding__
            return True
        return False
    
    def decodeMessage(self, text:str):
        reply : str = ''
        if text.find("prot:") == 0:
            return self.__commandProtocol(text)
        
    def getClassStats(self):
        return {"size" : self.__messageSize__, "encoding" : self.__messageEncoding__}
    
    def getMessageSize(self):
        return self.__messageSize__
    
    def getMessageEncoding(self):
        return self.__messageEncoding__
    
    def __commandProtocol(self, text :str):
        reply : str = ''
        if text.find("size=") != -1:
            parseRange = stringParseRange(text, "size=", ';', True)
            self.__newMessageSize__ = int(text[parseRange[0]+5:parseRange[1]]) if parseRange[1] != -1 else int(text[parseRange[0]+5:]) 
            if self.__newMessageSize__ < 32:
                return self.generateMessage("dec:")
            else:
                reply = self.generateMessage("acc:")
                self.__messageSize__ = self.__newMessageSize__
                
        if text.find("code=") != -1:
            parseRange = stringParseRange(text, "code=", ';', True)
            reply = self.generateMessage("acc:")
            if parseRange[1] == -1:
                self.__newMessageEncoding__ = text[parseRange[0]+5:]
            else:
                self.__newMessageEncoding__ = text[parseRange[0]+5:parseRange[1]]
        return reply
                
                

def stringParseRange(text : str, startSubString : str, endSubString : str, inOrder = False):
    """
    returns the location of the two substrings
    to for ranges

    Parameters
    ----------
    text : str
        the string to be indexed
    startSubString : str
        the first string you want to find in the text variable
    endSubString : str
        the last string ypu want to find in the text variable

    Returns
    -------
    begining : int
        DESCRIPTION.
    ending : int
        DESCRIPTION.

    """
    begining : int = text.find(startSubString)
    if inOrder:
        ending : int = text.find(endSubString, begining)
    else:
        ending : int = text.find(endSubString)
    return (begining, ending)
        
if __name__ == '__main__':
    test = Message()
    print(test.getClassStats())
    print(test.generateEncodingMessage(8947))
    print(test.getClassStats())
    test.isEncodingMessageAccepted(True)
    print(test.getClassStats())
    print(test.decodeMessage("prot:code=utf-16;size=800"))
    print(test.getClassStats())