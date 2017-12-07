#! /usr/bin/python
#
# From https://stackoverflow.com/questions/797771/python-protected-attributes
from __future__ import print_function
import sys

class Stock(object):

    def __init__(self, stockName):

        # '_' is just a convention and does nothing
        self.__stockName  = stockName   # private now


    @property # when you do Stock.name, it will call this function
    def name(self):
        print("In the getter, __stockName is %s" % self.__stockName, file=sys.stderr)
        return self.__stockName

    @name.setter # when you do Stock.name = x, it will call this function
    def name(self, name):
        print("In the setter, name is %s will become %s" % ( self.__stockName, name), file=sys.stderr)
        self.__stockName = name

if __name__ == "__main__":
    myStock = Stock("stock111")

    try:
        myStock.__stockName  # It is private. You can't access it.
    except AttributeError as a:
        print("As expect, raised AttributeError", str(a), file=sys.stderr )
    else:
        print("myStock.__stockName did did *not* raise an AttributeError exception")


    #Now you can myStock.name
    myStock.name = "Murphy"
    N = float(input("input to your stock: " + str(myStock.name)+" ? "))
    print("The value of %s is %s" % (myStock.name, N) )



