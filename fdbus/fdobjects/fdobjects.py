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

    def remove(self, name):
        try:
            fdobj = self.fdobjs[name]
            self.client_fdobjs[fdobj[0]].remove(fdobj[1])
            del self.fdobjs[name]
        except KeyError:
            raise UnknownDescriptorError(name)

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
            error_msg = get_error_msg()
            raise OpenError(error_msg)
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
            error_msg = get_error_msg()
            raise SocketError(error_msg)
        return sock

    def close_pool(self):
        pool = self.fdpool.fdobjs
        for fd in pool:
            pool[fd][1].fclose()
        for fd in self.fdpool.client_fdobjs:
            libc.close(fd)

    def get_fd(self, name):
        fdobj = self.fdpool.fdobjs.get(name)
        if fdobj is None:
            raise UnknownDescriptorError(name)
        return fdobj

    def send_fd(self, name, proto, recepient=None):
        fdobj = self.get_fd(name)
        cmd = fdobj[1].mode if recepient is None else PASS_FD
        self.sendmsg(proto, cmd, fdobj[1], recepient)

    def remove_fd(self, name):
        fdobj = self.get_fd(name)
        self.sendmsg(CLOSE, CLS_FD, fdobj[1])

    def recvmsg(self, sock, cmd=None):
        msg = pointer(msghdr(RECV, cmd))
        # set up a poll timout -- client disconnects -- will this call block indefin?
        if libc.recvmsg(sock, msg, MSG_SERV) == -1:
            error_msg = get_error_msg()
            raise RecvmsgError(error_msg)
        self.get_cmdmsg(sock, msg)
        
    def sendmsg(self, proto, cmd, fdobj=None, client=None):
        msg = pointer(msghdr(proto, cmd, fdobj, client))
        receipent = client if client else self.sock
        if libc.sendmsg(receipent, msg, MSG_SERV) == -1:
            error_msg = get_error_msg() 
            raise SendmsgError(error_msg) 

    def createfd(self, path, mode):
        fdobj = FileDescriptor(path=path, mode=mode, client=self)
        self.fdpool.add(self, fdobj)

    def get_cmdmsg(self, sock, msg):
        msg = msg.contents
    	fmsg = cast(msg.msg_iov.contents.iov_base, POINTER(fdmsg)).contents
        protocol = fmsg.protocol
        self.cmd_funcs[protocol](sock, fmsg.command, msg)

    def unpack_vector(self, msg):
        vector = cast(msg.msg_iov.contents.iov_base, POINTER(fdmsg)).contents
        return vector

    def extract_fd(self, cmd, msg):
        vector = self.unpack_vector(msg)
        name = vector.name
        path = vector.path
        client = vector.client
        mode = cmd
        created = vector.created
        fd = CMSG_DATA(msg.msg_control)
        fdobj = FileDescriptor(name=name, path=path, fd=fd, mode=mode, 
                               client=client, created=created)
        return fdobj
        
    def ld_cmdmsg(self, sock, cmd, msg):
        fdobj = self.extract_fd(cmd, msg)
        self.fdpool.add(sock, fdobj) 

    def pass_cmdmsg(self, sock, cmd, msg):
        if cmd == PEER_DUMP:
            peers = self.fdpool.client_fdobjs.keys()
            self.sendmsg(PASS, PEER_RECV, peers, sock)
        elif cmd == PEER_RECV:
            vector = self.unpack_vector(msg)
            self.peers = vector.fdobj
        else:
            fdobj = self.extract_fd(cmd, msg)
            self.sendmsg(RECV, cmd, fdobj, fdobj.client)

    def cls_cmdmsg(self, sock, cmd, msg):
        if cmd == CLS_FD:
            vector = self.unpack_vector(msg)
            self.fdpool.remove(vector.name)
        # add check for cls all else error

    def ref_cmdmsg(self, sock, cmd, msg):
        pass
