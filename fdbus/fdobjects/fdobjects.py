#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from os import fstat as stat
from time import ctime

from ..fdbus_h import *
from ..exceptions.exceptions import *

# a client name/id field (i.e. a process name or identifier/pid)
fdobj = namedtuple('File_Descriptor', ('name', 'path', 'fd', 'mode', 
                                                'client', 'created'))


class FileDescriptorPool(object):

    def __init__(self):
        self.fdobjs = {}
        self.client_fdobjs = defaultdict(list)

    def add(self, client, fdobj):
        self.fdobjs[fdobj.name] = [client, fdobj]
        self.client_fdobjs[client].append(fdobj)

    def remove(self, fdobj):
        pass

    def retrieve(self, fdobj):
        pass

    def bypath(self):
        pass

    def byfileno(self):
        pass

    def byfname(self):
        pass

    def __iter__(self):
        pass


class FileDescriptor(object):

    def __new__(self, **kwargs):
        path = kwargs.get('path')
        if path is None:
            raise FileDescriptorError(self)
        name = path.split('/')[-1]
        mode = kwargs.get('mode')
        if mode is None:
            raise FileDescriptorError(self)
        fd = kwargs.get('fd')
        if fd is None:
            fd = FileDescriptor.fopen(path, mode)
        client = kwargs.get('client')
        created = ctime()
        return _FileDescriptor(name, path, fd, mode, client, created)

    @staticmethod
    def fopen(path, mode):
        libc.open.restype = c_int
        fd = libc.open(path, mode)
        if fd == -1:
            errno = get_errno()
            raise OpenError(errno)
        return fd

class _FileDescriptor(fdobj):

    def __init__(self, name, path, fd, mode, client, created):
        super(_FileDescriptor, self).__init__(name, path, fd, mode, 
                                                   client, created)
        self.refcnt = 1

    def fsize(self):
        try:
            file_size = stat(self.fd).st_size
        except NameError: # handle different errors
            # raise
            print "File is not open"
        return file_size

    def fpos(self): # handle errors below
        offset = libc.lseek(self.fd, 0, SEEK_CUR)
        return offset

    def fstart(self):
        # handle errors
        offset = libc.lseek(self.fd, 0, SEEK_SET)

    def fend(self):
        # handle errors
        offset = libc.lseek(self.fd, 0, SEEK_END)

    def fset(self, pos):
        # handle errors
        c_pos = off_t(pos)
        offset = libc.lseek(self.fd, c_pos, SEEK_SET)

    def fclose(self):
        # handle errors
        ret = libc.close(self.fd)

    def __enter__(self):
        # handle errors
        return self.fd

    def __exit__(self, exc_type, exc_value, traceback):
        # handle errors
        self.fclose()


class FDBus(object):

    def __init__(self, path):
        super(FDBus, self).__init__()
        self.path = path
        self.fdpool = FileDescriptorPool() 
        self.cmd_funcs = {LOAD:self.ld_cmdmsg, PASS:self.pass_cmdmsg,
                          CLOSE:self.cls_cmdmsg, REFERENCE:self.ref_cmdmsg}

    def socket(self):
        libc.socket.restype = c_int
        sock = libc.socket(AF_UNIX, SOCK_STREAM, PROTO_DEFAULT)
        if sock == -1:
            errno = get_errno()
            raise SocketError(errno)
        return sock

    def close_pool(self):
        pass

    def recvmsg(self, sock):
        msg = pointer(msghdr(RECV))
        # set up a poll timout -- client disconnects -- will this call block indefin?
        if libc.recvmsg(sock, msg, MSG_SERV) == -1:
            errno = get_errno()
            raise RecvmsgError(errno)
        self.get_cmdmsg(sock, msg)
        
    def sendmsg(self, proto, cmd, fdobj=None):
        msg = pointer(msghdr(proto, cmd, fdobj))
        if libc.sendmsg(self.client, msg, MSG_SERV) == -1:
            errno = get_errno()
            raise SendmsgError(errno)      

    def createfd(self, path, mode):
        fdobj = FileDescriptor(path=path, mode=mode, client=self)
        self.fdpool.add(self, fdobj)

    def get_cmdmsg(self, sock, msg):
        msg = msg.contents
    	fmsg = cast(msg.msg_iov.contents.iov_base, POINTER(fdmsg)).contents
        protocol = fmsg.protocol
        self.cmd_funcs[protocol](sock, fmsg.command, msg)

    def ld_cmdmsg(self, sock, cmd, msg):
        fd_msg = cast(msg.msg_iov.contents.iov_base, POINTER(fdmsg)).contents
        name = fd_msg.name
        path = fd_msg.path
        mode = cmd
        created = fd_msg.created
        fd = CMSG_DATA(msg.msg_control)
        fdobj = FileDescriptor(name=name, path=path, fd=fd, mode=mode, 
                               client=sock, created=created)
        self.fdpool.add(sock, fdobj) 

    def pass_cmdmsg(self, sock, cmd, msg):
        pass

    def cls_cmdmsg(self, sock, cmd, msg):
        pass

    def ref_cmdmsg(self, sock, cmd, msg):
        pass