#!/usr/bin/env python
# -*- coding: utf-8 -*-

from select import *

from ..fdbus_h import *
from ..exceptions.exceptions import *
from ..fdobjects.fd_object import FileDescriptor, FileDescriptorPool


class Client(object):

    def __init__(self, path):
        self.path = path
        self.client = libc.socket(AF_UNIX, SOCK_STREAM, PROTO_DEFAULT) 
        if self.client == -1:
            errno = get_errno()
            raise SocketError(errno)
        self.local_fds = FileDescriptorPool() 
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

    def openfd(self, fdobj):
        try:
            fdobj.fopen()
        except OpenError:
            raise FileDescriptorError(fdobj)
        return

    def createfd(self, path, mode):
        name = path.split('/')[-1]
        fdobj = FileDescriptor(path=path, mode=mode, name=name)
        self.openfd(fdobj)
        self.local_fds.add(fdobj)
        return
 
    def passfd(self):
        pass

    def getpeers(self):
        pass

    def readfd(self, fd):
        rd_buffer = (c_char * 2048)()
        rd_buffer_len = 2048 - 1
        libc.read(c_int(fd), rd_buffer, rd_buffer_len)
        return rd_buffer
