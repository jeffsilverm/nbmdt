#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This class provides services for reporting status, logging, etc.

import datetime
import sys
import time


class Status(object):
    def __init__(self, resource_name):
        self.__summary = True
        self.__name = resource_name
        self.__timestamp = datetime.datetime.now()


    @property  # when you do lvar = Status.summary, it will call this function
    def summary(self):
        print("In the getter, __summary is %s" % self.__summary,
              file=sys.stderr)
        return (self.__summary, self.__timestamp)

    @summary.setter  # when you do Status.summary = value, it will call this function
    def summary(self, summary: bool):
        print(
            "In the setter, name is %s will become %s" % (self.__name, summary),
            file=sys.stderr)
        self.__summary = summary
        self.__timestamp = datetime.datetime.now()

    def __str__(self):
        return (f"At {self.__timestamp}, {self.__name} is {self.__summary} ")


if __name__ == "__main__":
    black = Status("black")
    green = Status("green")

    black.summary = True
    time.sleep(.3)
    (state, timestamp) = black.summary
    print(f"At {timestamp}, black was changed to {state} ")
    black.summary = False
    time.sleep(.7)
    (state, timestamp) = black.summary
    print(f"At {timestamp}, black was changed to {state} ")
