#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 00:49:24 2024

@author: goduser
"""

import tkinter.filedialog as fileGUI

def getUserFiles()->str:
    fileList = fileGUI.askopenfiles(filetypes = [("Program Files", ".py .c .cpp .h"), 
                                                 ("python files", ".py"), 
                                                 ("C Files", ".c .cpp .h")])
    for filePath in fileList:
        yield filePath.name

def openFileByLine(filepath:str):
    with open(filepath, 'r') as file:
        line = file.readline()
        while line:
            yield line
            line = file.readline()
            
if __name__ == '__main__':
    x = getUserFiles()
    next(x)
    