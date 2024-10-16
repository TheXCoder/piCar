# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:11:19 2024

@author: Phatty
"""
#✓
# To do:  
import os, logging, rsa
from unlocked_file import UnlockedFile
from config_file_maker import ConfigFileMaker
from misc import checkHashSalt, convertStrToBytes
class SecureEvents:
    def __init__(self, password : str | None = None, encoding : str = "utf-8"):
        """
        This class process the name of the command and checks it against the event config

        Parameters
        ----------
        password : str | None, optional
            password for the directory. The default is None.
        encoding : str, optional
            the encoding of the text. The default is "utf-8".

        """
        self._eventDirectory : str = os.path.abspath("events" + os.sep + "events.ini")
        self._file : UnlockedFile = UnlockedFile(self._eventDirectory)
        self._config : ConfigFileMaker() = ConfigFileMaker()
        self._logger : logging.Logger = logging.getLogger("SecureEvents for \"" + self._eventDirectory + "\"")
        self._file.unlock(password, encoding)
        
    def _readConfig(self, password : str | None = None, encoding : str = "utf-8") -> bool:
        """
        uses the unlocked file class to read data from the event config file

        Parameters
        ----------
        password : str | None, optional
            password for the directory. The default is None.
        encoding : str, optional
            encoding for the directory. The default is "utf-8".

        Returns
        -------
        bool
            True if any data could be read from the config file
            otherwise False

        """
        data : str | None = self._file.read(password = password, encoding = encoding)
        if data is None:
            self._logger.warning("There is no data stored in the config file. This will be detrimental later. ;)")
            return False
        self._config.recieve(data)
        return True
    
    def findLevel(self, commandName : str) -> str:
        """
        Find the level with the command

        Parameters
        ----------
        commandName : str
            the name of the command

        Returns
        -------
        str
            the security level name 

        """
        self._readConfig()
        section : str | None = None
        data : dict | None = None
        for section, data in self._config:
            try:
                assert commandName not in data["commands"]
            except TypeError:
                continue
            except AssertionError:
                break
        else:
            return None
        return section
                
    
    def checkCommand(self, command : str, password : str | None = None, deviceName : str | None = None,
                     encryptedDeviceSigniture : str | None = None, encoding : str = "utf-8") -> bool:
        """
        check the command to see if the command can be run with the given security parameters
        
        different levels have different requirements for security
        
        level 0 requires that all the security parameters must be filled in order to run the command

        Parameters
        ----------
        command : str
            name of the command
        password : str | None, optional
            Password for the security level (a security parameter). The default is None.
        deviceName : str | None, optional
            The name of the device that sent the command (a security parameter). The default is None.
        encryptedDeviceSigniture : str | None, optional
            The custom signiture for the device that sent the command (a security parameter). The default is None.
        encoding : str, optional
            the encoding of the text. The default is "utf-8".

        Returns
        -------
        bool
            True if command can be ran
            Otherwise False

        """
        self._readConfig()
        level : str = self.findLevel(command)
        if level is None:
            self._logger.warning("There is no command in any of the security levels with this name.")
            return None
        #level 0 checker
        if level == "level 0":
            if None in (password, deviceName, encryptedDeviceSigniture, encoding):
                return False
            return self.__checkLevelZeroCommand(password = password, deviceName=deviceName,
                                                encryptedDeviceSigniture=encryptedDeviceSigniture, encoding = encoding)
        #other levels
        return self.__checkLevelCommand(level = level, password = password, deviceName = deviceName,
                                        encryptedDeviceSigniture=encryptedDeviceSigniture, encoding=encoding)
    
    def __checkLevelCommand(self, level : str, password : str | None = None, deviceName : str | None = None,
                     encryptedDeviceSigniture :str | None = None, encoding : str = "utf-8") -> bool:
        """
        check the not level 0 command to see if the command can be run with the given security parameters

        Parameters
        ----------
        level : str
            the level of the command
        password : str | None, optional
            Password for the security level (a security parameter). The default is None.
        deviceName : str | None, optional
            The name of the device that sent the command (a security parameter). The default is None.
        encryptedDeviceSigniture : str | None, optional
            The custom signiture for the device that sent the command (a security parameter). The default is None.
        encoding : str, optional
            the encoding of the text. The default is "utf-8".

        Returns
        -------
        bool
            True if command can be ran
            Otherwise False

        """
        
        #if a the signiture of the level is incorrect and there is no password for current level
        #then the function will return false
        #if there is no signiture and there is no password specified the function will look in the lower levels for
        # a password. 
        
        #check this level's signiture
        signitureFlag : bool | None = self.__checkSigniture(level = level, deviceName = deviceName,
                                                            encryptedDeviceSigniture=encryptedDeviceSigniture)
        if signitureFlag is True:
            self._logger.debug("signiture flag has been raised for current level")
            return True
        #check this level's password
        passwordFlag : bool | None = self.__checkLevelPassword(level = level, password = password, encoding = encoding)
        if passwordFlag is not None:
            self._logger.debug("password flag has been raised for current level")
            return passwordFlag
        
        #moves on to looking for passwords and signitures in other levels of security
        
        #checks if the signiture of the device is in a lower numbered security level
        if signitureFlag is not True:
            self._logger.debug("checking lower numbered security levels for their signiture")
            higherSignitureFlag : bool | None = None # flag for checking the lower numbered security level
            for section in self._config.getSections():
                if int(section[6]) < int(level[6]):
                    higherSignitureFlag = self.__checkSigniture(level= section, deviceName = deviceName,
                                                                encryptedDeviceSigniture=encryptedDeviceSigniture)
                    #the device must be in a lower numbered security level in order to pass this 
                    if higherSignitureFlag is True:
                        self._logger.debug("device signiture matches a lower numbered security level")
                        return True
        #if device signiture does not match the current or lower numbered security level
        #i.e device signiture sets the signitureFlag to false and 
        #has not set the higherSignitureFlag to True, the function will return a False
        if signitureFlag == False:
            self._logger.debug("device signiture matches does not match the current level or any of the lower numbered security levels")
            return False
        
        #if there is no device signiture present i.e the signitureFlag being set to None
        #the function will look for higher numbered levels of security passwords that may the current password
                    
        
        #check for higher numbered security levels' password
        section : str
        for section in self._config.getSections():
            if int(section[6:]) > int(level[6:]):
                passwordFlag = self.__checkLevelPassword(level = section, password = password, encoding=encoding)
                if passwordFlag is not None:
                    self._logger.debug("a match password that satisfies the requirements of the current security level has been found "\
                          +"Applying it to the current level...")
                    return passwordFlag
                if self._config[section]["trustedDevices"] is not None:
                    self._logger.debug(f"There is a higher numbered security level, {section}, with a trustedDevice, "\
                          +"since no higher number level before this level could not satify the requirements. "\
                          +"The program will assume that level cannot be accessed... ;)")
                    return False
        self._logger.debug("There are no current security requirements that satisfy the current level. Assuming that the level requires no security... >:O")
        return True
    
    def __checkSigniture(self, level : str, deviceName : str | None = None,
                         encryptedDeviceSigniture : str | None = None) -> bool | None:
        """
        checks device name and signiture for the security level (basically to see if the device is a trusted device)
        Parameters
        ----------
        level : str
            the level of the command.
        deviceName : str | None, optional
            The name of the device that sent the command (a security parameter). The default is None.
        encryptedDeviceSigniture : str | None, optional
            The custom signiture for the device that sent the command (a security parameter). The default is None.

        Returns
        -------
        bool | None
            True if the deviceName and encryptedDeviceSigniture matches the requirements for the level
            None if level does not have a trusted device
            False if the requirements aren't met
            also False if the level has a trusted device and one or of the parameters is missing

        """
        if self._config[level]["trustedDevices"] is None:
            return None
        if None in (deviceName, encryptedDeviceSigniture):
            return False
        
        if deviceName not in self._config[level]["trustedDevices"].keys():
            self._logger.debug()
            return False
        try:
            trustedDevice : dict = self._config[level]["trustedDevices"][deviceName]
            eSig: bytes = convertStrToBytes(encryptedDeviceSigniture) # signiture as bytes
            keyEncoding : str = self._config[level]["encoding"]
            key : str = trustedDevice["privateKey"]
            privateKey : rsa.PrivateKey =rsa.PrivateKey.load_pkcs1(key.encode(keyEncoding))
            deviceSigniture : str = rsa.decrypt(eSig, privateKey).decode(keyEncoding) #I don't know wiether to get the encoding from the level or from the user. I chose from the level
            if deviceSigniture == trustedDevice["signiture"]:
                return True
        except rsa.DecryptionError:
            self._logger.warning("Decryption for the device signiture has failed. Assuming that device signiture is incorrect...")
            return False
        return False
    
        
        
        # if encryptedDeviceSigniture is not None and self._config[level]["trustedDevices"] is not None:
        #     deviceSigniture : str | None = None
        #     key : str = self._config[level][]
        #     keyEncoding : str = self._config[level]["encoding"]
        #     privateKey : rsa.PrivateKey =rsa.PrivateKey.load_pkcs1(key.encode(keyEncoding))
        #     deviceSigniture = rsa.decrypt(encryptedDeviceSigniture.encode("utf-8"), privateKey).decode(encoding)
        #     if deviceSigniture in self._config[level]["trustedDevices"]:
        #         return True
        #     return False
        # return None
    def __checkLevelPassword(self, level : str, password : str | None = None, encoding : str = "utf-8") -> bool | None:
        """
        checks the password for the security level

        Parameters
        ----------
        level : str
            the level of the command.
        password : str | None, optional
            the password for the security level. The default is None.
        encoding : str, optional
            the encoding of the text. The default is "utf-8".

        Returns
        -------
        bool | None
            True if the password matches the requirements for the level
            None if either the level does not have a password 
            False if the requirements aren't met
            also False if the level has a password and parameter for the password is missing

        """
        if self._config[level]["password"] is not None:
            if password is None:
                return False
            password = "" if password is None else password
            byteSize : int = self._config[level]["byteSize"]
            endienness : str = self._config[level]["endienness"]
            hashSalt : bytes = self._config[level]["password"].to_bytes(byteSize, byteorder = endienness)
            passwordsMatch : bool = checkHashSalt(password, hashSalt, self._config[level]["saltSize"], encoding)
            return passwordsMatch
        return None
            
    def __checkLevelZeroCommand(self, password : str = None, deviceName : str = None,
                                encryptedDeviceSigniture : str | None = None, encoding : str = "utf-8"):
        """
        

        Parameters
        ----------
       password : str | None, optional
           Password for the security level (a security parameter). The default is None.
       deviceName : str | None, optional
           The name of the device that sent the command (a security parameter). The default is None.
       encryptedDeviceSigniture : str | None, optional
           The custom signiture for the device that sent the command (a security parameter). The default is None.
       encoding : str, optional
           the encoding of the text. The default is "utf-8".

       Returns
       -------
       bool
           True if command can be ran
           Otherwise False
        """
        if self.__checkLevelPassword("level 0", password, encoding) and self.__checkSigniture("level 0", deviceName, encryptedDeviceSigniture) is True:
            self._logger.debug("This device and password match the level 0 requirement")
            return True
        self._logger.debug("Either the password or the signiture does not match the level 0 requirement")
        return False
    