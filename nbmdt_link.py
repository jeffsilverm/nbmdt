#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#
# This file provides a class and methods for dealing with links
#


from subprocess import Popen, PIPE, run

DEBUG = True

def main():
    link_list = Link.get_list_of_links()
    links_names_list = main()
    for link_name in links_names_list:
        print(link_name )
        link_obj =

    return link_list


class Link ( object ):

    # This dictionary caches the strings from the get_list_of_links, so that there is no need to spawn a subprocess
    # if this class already knows about the link
    links_str_dict = {}

    def __init__ ( self, link_name, **kwargs ):
        self.link_name = link_name
        for a in kwargs.keys():
            self.__setatter__(a, kwargs[a])



    @classmethod
    def get_link_parameters ( self, link_name ):
        """This method uses the ip command to get all of the attributes of a link.  This is a class method because it
         creates a Link class object.

         :param link_name   The name of the link to create

         :returns   an object of class Link

         """
# effs@jeffs-laptop:~ $ /usr/sbin/ip --oneline link show
# 1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
# 2: enp0s25: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN mode DEFAULT group default qlen 1000\    link/ether 00:24:e8:f3:72:11 brd ff:ff:ff:ff:ff:ff
# 3: wlp12s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DORMANT group default qlen 1000\    link/ether 00:21:6a:53:14:10 brd ff:ff:ff:ff:ff:ff
# 4: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 1000\    link/ether 52:54:00:67:63:84 brd ff:ff:ff:ff:ff:ff
# 5: virbr0-nic: <BROADCAST,MULTICAST> mtu 1500 qdisc fq_codel master virbr0 state DOWN mode DEFAULT group default qlen 1000\    link/ether 52:54:00:67:63:84 brd ff:ff:ff:ff:ff:ff

        global links_str_dict

        if link_name not in links_str_dict:
            with Popen(["/usr/sbin/ip", "--oneline", "link", "show", "dev", link_name ], stdout=PIPE) as proc:
                results = proc.stdout.read()
# jeffs@jeffs-laptop:~/nbmdt (development)*$ /usr/sbin/ip --oneline link show enp0s25
# 2: enp0s25: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state DOWN mode DEFAULT group default qlen 1000\
            #  link/ether 00:24:e8:f3:72:11 brd ff:ff:ff:ff:ff:ff

            parameters = results.split()
            links_str = results.split(b"\n")[:-1]
            fields = links_str.split()
            link_name = fields[1]
            links_str_dict[link_name] = fields
            self.__init__(link_name, {'flags':fields[2], 'mtu':fields[4], 'state': fields[8]} )
            p=Dict()
            p['] =



             =
             =
            mode = fields[10]
            group = fields[12]
            qlen = fields[14]
            mac_addr = fields[16]
            brd_addr = fields[18]


            links_str_dict[]

        self.__init__(self, link_name=link_name, )


        return None

    @classmethod
    def get_list_of_links(self):
        """This method returns a list of all of the links current visible to the ip command

        :returns a list of the names of the links"""

        with Popen(["/usr/sbin/ip", "--oneline", "link", "show"], stdout=PIPE) as proc:
            results = proc.stdout.read()
        links_strs = results.split(b"\n")[:-1]
        links_name_list=[]
        link_str_dict={}
        for link in links_strs:
            link_line = link.split()
            link_name = link_line[1]
            links_name_list.append( link_name )
            link_str_dict[link_name]=link_line[2:]
        return links_name_list



if __name__ == "__main__" :
    main()





