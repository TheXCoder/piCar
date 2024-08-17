# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:28:20 2024

@author: Phatty
"""
import socket, time 

#========list mathing functions============

def checkIdentityOrEquality(target, item, checkIdentity : bool):
    if checkIdentity:
        return item is target
    return item == target
def countMatchingItems(list1 : list, list2 : list, checkIdentity : bool = False, isOrdered : bool = True) -> int:
    smallSize = len(list1) if len(list1) < len(list2) else len(list2)
    if isOrdered:
        count : int = 0
        for index in range(smallSize):
            if not checkIdentityOrEquality(list1[index], list2[index], checkIdentity):
                return count
            count += 1
    return sum([checkIdentityOrEquality(list1[index], list2[index], checkIdentity) for index in range(smallSize)])


#========string matching functions==================================
def countMatchingLetters(string1 : str, string2 : str, isOrdered : bool = True) -> int:
    """
    Counts how many letters are matching between the two string

    Parameters
    ----------
    string1 : str
        first string
    string2 : str
        the second strings
    isOrdered : bool, optional
        Makes it so matching is depended on if previous characters matching, for example:
            string1 = "HelloWorld"
            string2 = "HelloWraldo"
            When isOrder is True:
                matching letters counted (H)(e)(l)(l)(o)(W)
                function will return 6
            when isOrder is False:
                matching letters counted (H)(e)(l)(l)(o)(W)(l)(d)
                function will return 8
        The default is True.

    Returns
    -------
    int
        how many letters in the two strings were matching

    """
    smallestTextSize = len(string1) if len(string1) < len(string2) else len(string2) #the value is determined by which text is smaller size
    if isOrdered:
        count : int = 0
        for isMatch in [string1[index] == string2[index] for index in range(smallestTextSize)]:
            if not isMatch:
                break
            count +=1
        return count
    return sum([string1[index] == string2[index] for index in range(smallestTextSize)])
    
def rankMatchString(stringToMatch : str, itemsList : list, isOrdered : bool = True) -> dict:
    """
    ranks strings from specified list based on how close they resemble stringToMatch

    Parameters
    ----------
    stringToMatch : str
        the target string that that the strings in the list should match with
    itemsList : list
        a list of strings to be ranked
    isOrdered : bool, optional
        Makes it so matching is depended on if previous characters matching, for example:
            string1 = "HelloWorld"
            string2 = "HelloWraldo"
            When isOrder is True:
                matching letters counted (H)(e)(l)(l)(o)(W)
                function will return 6
            when isOrder is False:
                matching letters counted (H)(e)(l)(l)(o)(W)(l)(d)
                function will return 8
        The default is True.

    Returns
    -------
    dict
        {rank [int], matchingString(s) [str|list]}
        a dictionary of strings with their ranks with as keys

    """
    stringRanks = [countMatchingLetters(stringToMatch, string) for string in itemsList]
    stringDict : dict = {}
    for index, rank in enumerate(stringRanks):
        # string(s) have been assigned the rank
        try:
            # only a single string has the rank
            if isinstance(stringDict[rank], list):
                stringDict[rank].append(itemsList[index])
            # multiple strings has the rank
            else:
                stringDict[rank] = [stringDict[rank], itemsList[index]]
        # no string(s) have been assigned the rank
        except KeyError:
            stringDict[rank] = itemsList[index]
    return stringDict

def orderByRank(itemsRanked : dict, reverse : bool = False) -> list:
    """
    creates a list of ordered items based off of rank

    Parameters
    ----------
    itemsRanked : dict
        {rank [int], items [TYPE]}
        a dictionary of items with their ranks with as keys
    reverse : bool, optional
        True is decending order False is accending order. The default is False.

    Returns
    -------
    list
        a list of ordered items based off of rank

    """
    itemsList : list = []
    for rank in sorted(itemsRanked.keys(), reverse=reverse):
        if isinstance(itemsRanked[rank], list):
            itemsList += itemsRanked[rank]
        else:
            itemsList.append(itemsRanked[rank])
    return itemsList
    


#===========socket helper functions=================================

def findDevice(device_IPOrName : str, isLocal : bool = True, numberIntervals : int = 5, intervalWaitTime : float = 1) -> tuple:
    """
    Find the name and ip of host by using name or ip

    Parameters
    ----------
    host_IPOrName : str
        IP example: 64.233.160.5
        the system name of device you want to find
    isLocal : bool, optional
        Binary value to determine weither to look for
        the device on the local area network, or on the internet
        this value only matters if using a name to search for device
        The default is True.
    numberIntervals : int, optional
        How many times the function will try to look for the device. 
        The default is 5.
    intervalWaitTime : float, optional
        Wait period in between search cycles.
        The measurement is in seconds The default is 1 for 1 second

    Raises
    ------
    ConnectionError
        if device cannot be located

    Returns
    -------
    tuple(str, str)
        tuple(host name, hostIP).

    """
    deviceIP : str = device_IPOrName * int((device_IPOrName[0]).isnumeric())
    deviceName : str =  device_IPOrName * int(deviceIP=="") 
    print(deviceName)
    for count in range(numberIntervals):
        try:
            if deviceIP != "":
                deviceIP = socket.gethostbyaddr(deviceIP)[0]
            #this block will never get ran if the the first if statement ran
            elif deviceName != "":
                print(deviceName + (".local" * isLocal))
                deviceIP = socket.gethostbyname(deviceName + (".local" * isLocal))
            return deviceName, deviceIP
        except socket.gaierror or socket.herror:
            time.sleep(intervalWaitTime)
    error : str = ""
    if deviceName == "":
        error = "host"
    else:
        error = "local" * int(isLocal)
        error += f"host named \"{deviceName}\""
    if deviceIP != "":
        error += " with IP \"{deviceIP}\""
    error += " cannot be found"
    raise ConnectionError(error)
    return "", ""

def getConnected(serverIP : str, clientsocket,  port : int = 5050, numberIntervals : int = 5,  intervalWaitTime : float = 1):
    for _ in range(numberIntervals):
        if _ == numberIntervals -1:
            print("Last try before giving up")
        else:
            print("Server has refused to connect. Trying again")
        try:
            clientsocket.connect((serverIP,5050))
            print("Connected to server")
            return clientsocket
        except ConnectionRefusedError:
            time.sleep(intervalWaitTime)
            
    print("System has failed to connect with the server.")
    return None