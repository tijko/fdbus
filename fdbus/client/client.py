#!/usr/bin/env python
# -*- coding: utf-8 -*-

from select import *

from ..fdbus_h import *
from ..exceptions.exceptions import *
from ..fdobjects.fdobjects import FileDescriptor, FileDescriptorPool, FDBus


class Client(FDBus):

    def __init__(self, path):
        super(Client, self).__init__(path)
        self.client = self.socket() 
        self.connected = False

    def connect(self):
        self.client_address = pointer(sockaddr_un(AF_UNIX, self.path))
        self.client_address.contents.sun_family = AF_UNIX
        self.client_address.contents.sun_path = self.path
        if (libc.connect(self.client, cast(self.client_address, 
                         POINTER(sockaddr)), sizeof(sockaddr_un)) == -1):
            errno = get_errno()
            raise ConnectError(errno)
        self.connected = True
       
    def writefd(self):
        pass

    def closefd(self):
        pass

    def passfd(self, fd, peer):
        # to a specific peer
        pass

    def loadfd(self, name):
        fdobj = self.fdpool.fdobjs.get(name)
        if fdobj is None:
            raise UnknownDescriptorError(name)
        mode = fdobj[1].mode
        self.sendmsg(LOAD, mode, fdobj[1])

    def getpeers(self):
        pass

    def readfd(self, fd):
        rd_buffer = (c_char * 2048)()
        rd_buffer_len = 2048 - 1
        libc.read(c_int(fd), rd_buffer, rd_buffer_len)
        return rd_buffer
