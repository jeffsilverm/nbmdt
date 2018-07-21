#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module has the Entities class that provides services common to all entities:
# interfaces, routes, transports
#
#

from enum import Enum, unique
import typing
import datetime
import utilities


@unique                         # a decorator on a class!
class ErrorLevels(Enum):
    """
    From The_Network_Boot_Monitor_Diagnostic_Tool.html


        Normal
    All is well.  The resource is working properly in all respects
        Slow
    The monitor is measuring traffic flow through the resource or the delay required to reach the interface, and it is outside acceptable limits.  The interface is still working.
        Degraded due to an upstream dependency failure.
    The resource is at increased risk of failure because a dependency is down.  However, the dependency has some redundancy so the fact that there is an upstream failure does not mean that this interface is down.  For example, there are multiple DNS servers.  If a single server fails, the resolver will pick a different name server.  So DNS will work, but there will be fewer servers than normal and a greater risk of subsequent failure.
        Down cause unknown
    The resource is flunking a health check for some reason.
        Down due to a missing or failed dependency
    The resource is flunking a health check or is down because something it depends on is down.
        Down Acknowledged
    The resource is down and an operator has acknowledged that the interface is down.  This will only happen while monitoring, never at boot time or while diagnosing or designing
        Changed
    The resource is in the configuration file, but the monitor cannot find it, or the auto configuration methods found a resource that should be in the configuration file, but isn't.  Classic example is a NIC changing its MAC address.
        Other problem
    Something else is wrong that doesn't fit into the above categories.
        unknown
    We genuinely do not know the status of the entity.  This could be because it hasn't been tested yet, or because conditions are such that the test cannot be done correctly

    """

    NORMAL = 1  # Everything is working properly
    SLOW = 2  # Up, but running slower than allowed
    DEGRADED = 3  # Up, but something that this thing partly depends on is down
    DOWN = 4  # It flunks the test, cause unknown
    DOWN_DEPENDENCY = 5  # It flunks the test, but it is known to be due
    # to a dependency
    DOWN_ACKNOWLEDGED = 6  # It flunks the test, but somebody has
    # acknowledged the problem
    CHANGED = 7  # The resource works, but something about it has changed
    OTHER = 8  # A problem that doesn't fit into any of the above categories
    UNKNOWN = 9     # We do not know what the status is


class Entity(object):
    """
    An "entity" is an object in the OSI stack or something network critical that is outside the
       stack. It has a name, a log, a current status.
    An entity can

    """

    def __init__ (self, name : str, layer : utilities.OSILevels) -> None:
        self._name = name
        self._layer =  layer         # layer in the OSI model
        self._log = []
        self._current_status = None     # Prevents an Attribute exception later
        self._log_initialization_time = datetime.datetime.now()
        self.event_record(ErrorLevels.UNKNOWN, "Log list initialized")

    def event_record(self, new_status : Enum, reporter : str ) -> typing.Tuple :
        """
        Record a change in status.  If this isn't actually a change, then don't record anything
        :param new_status:  Errorlevels  This is the new state
        :param reporter:  str   An arbitrary string that the caller can use to annotate the event
        :return: A tuple with the new_status,
        """
        if self._current_status == new_status:
            return
        record = (datetime.datetime.now(), new_status, reporter )
        self._log.append(record)
        self._current_status = new_status
        return

    @property
    def log(self) -> list:
        return self._log

    # Note that there is no setter for the log object.  It's supposed to be immutable

    @property
    def current_status(self) -> int:
        return self._current_status

    # There is no setter for the layer object - it's immutable

    @property
    def name(self) -> str:
        return self._name


if __name__ == "__main__":
    e1 = Entity("xyzzy", layer=0)
    assert e1.name == "xyzzy", f"Entity.name failed, e1.name is {e1.name} should be xyzzy"
    assert e1.current_status == ErrorLevels.UNKNOWN, f"Entity {e1.name} has current status {e1.current_status} should be {ErrorLevels.UNKNOWN} "
    print("Add a test that the time stamps are working properly. Requires timedelta")
    import time
    time.sleep(2.0)
    e1.event_record(ErrorLevels.NORMAL, "testing adding an entry")
    assert e1.current_status == ErrorLevels.NORMAL, f"Entity {e1.name} has current status {e1.current_status} should be {ErrorLevels.NORMAL} "
    assert e1.log[1][1] == ErrorLevels.NORMAL, f"Entity {e1.name} last entry in the log list is {e1.log[1][1]} should be {ErrorLevels.NORMAL} "









