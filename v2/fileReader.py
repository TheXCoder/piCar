#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 16:26:12 2024

@author: goduser
"""

import tkinter.filedialog as fileGUI

def getUserFiles()->str:
    fileList = fileGUI.askopenfiles(filetypes = [("Program Files", ".py .c .cpp .h"), 
                                                 ("python files", ".py"), 
                                                 ("C Files", ".c .cpp .h")])
    return fileList

def openFileByLine(filepath:str):
    with open(filepath, 'r') as file:
        line = file.readline()
        while line:
            yield line
            line = file.readline()
            
if __name__ == '__main__':
    raise RuntimeError("This is not a runable script")
    