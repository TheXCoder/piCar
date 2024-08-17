# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 11:16:51 2024

@author: Phatty
"""
import logging
import datetime
class CarLogger:
    _MASTERCONFIG = {
        "version":1,
        "disable_existing_loggers" : False,
        "handlers" : {
            "stdout" : {
                "class" : "logging.StreamHandler"}
            },
        "loggers" : {...},
        "formatters" : {
            "basic" : "carLogger%(levelname)s: %(message)"}
        }
    _masterLogger : logging.Logger = logging.getLogger("carLogger")
    
    