# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 11:21:12 2024

@author: Phatty
"""

from encrypted_my_message import EncryptedMyMessage
class SecureMyMessage(EncryptedMyMessage):
    def __init__(self, eventsDictionary : dict | None = None, securedEvents : dict | None = None):
        """
        

        Parameters
        ----------
        eventsDictionary : dict | None, optional
            DESCRIPTION. The default is None.
        securedEvents : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        super(SecureMyMessage,self).__init__(eventsDictionary)
        