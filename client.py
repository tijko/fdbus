#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
from socket import *
from select import *

from fdbus_h import *


class Client(object):

    def __init__(self, path):
        self.path = path
        self.client = libc.socket(AF_UNIX, SOCK_STREAM, PROTO_DEFAULT) 

    def connect(self):
        self.client_address = pointer(sockaddr_un(AF_UNIX, self.path))
        self.client_address.contents.sun_family = AF_UNIX
        self.client_address.contents.sun_path = self.path
        libc.connect(self.client, cast(self.client_address, POINTER(sockaddr)), 
                     sizeof(sockaddr_un))

    def recvmsg(self):
        client_msghdr = pointer(msghdr())
        libc.recvmsg(self.client, client_msghdr, MSG_CMSG_CLOEXEC)
        ctrl_msg = client_msghdr.contents.msg_control
        client_cmsghdr = cast(ctrl_msg, POINTER(cmsghdr))
        fd = client_cmsghdr.contents.cmsg_data
        return fd           

    def sendmsg(self):
        pass

    def writefd(self):
        pass

    def closefd(self):
        pass

    def openfd(self):
        pass

    def createfd(self):
        pass

    def passfd(self):
        pass

    def getpeers(self):
        pass

    def readfd(self, fd):
        rd_buffer = (c_char * 2048)()
        rd_buffer_len = 2048 - 1
        libc.read(c_int(fd), rd_buffer, rd_buffer_len)
        return rd_buffer
