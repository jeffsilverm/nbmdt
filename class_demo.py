#! /usr/bin/env python3

class MyClass ( object ):

  instance_list = []  

  def __init__ ( self, arg1, arg2):
    self.arg1 = arg1
    self.arg2 = arg2

  @classmethod
  def make_instances( cls ):
    for a1 in range(1,4):
      for a2 in range(1,3):
        cls.instance_list.append( MyClass( a1, a2 ) )

  @classmethod
  def dump_instance_list ( cls ):
    for instance in cls.instance_list:
      print( "arg1= %d\targ2= %d" % ( instance.arg1, instance.arg2) )

if __name__ == "__main__" :
  MyClass.make_instances()
  MyClass.dump_instance_list()
  an_instance = MyClass(14, 22)
  print("An instance: %d, %d" % (an_instance.arg1, an_instance.arg2))



