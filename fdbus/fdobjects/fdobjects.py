#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from os import fdopen, fstat as stat
from time import ctime, time

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

    def __len__(self):
        return len(self.fdobjs)

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
        created = time()
        return _FileDescriptor(name, path, fd, mode, client, created)

    @staticmethod
    def fopen(path, mode):
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
        ret = libc.close(self.fd)
        if ret == -1:
            error_msg = get_error_msg()
            raise CloseError(error_msg)

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
        self.proto_funcs = {LOAD:self.ld_protomsg, PASS:self.pass_protomsg,
                            RECV:self.recv_protomsg, CLOSE:self.cls_protomsg, 
                            REFERENCE:self.ref_protomsg}

    def socket(self):
        sock = libc.socket(AF_UNIX, SOCK_STREAM, PROTO_DEFAULT)
        if sock == -1:
            error_msg = get_error_msg()
            raise SocketError(error_msg)
        return sock

    def close_pool(self):
        fdpool = self.fdpool.fdobjs
        client_fdpool = self.clients.fdpool
        for fd in fdpool:
            fdpool[fd][1].fclose()
        for fd in client_fdpool:
            libc.close(fd)
        
    def get_fd(self, name):
        fdobj = self.fdpool.fdobjs.get(name)
        if fdobj is None:
            raise UnknownDescriptorError(name)
        return fdobj

    def send_fd(self, name, recepient=None):
        fdobj = self.get_fd(name)[1]
        cmd = fdobj.mode
        payload = [name, fdobj.path] + \
                   map(str, [fdobj.fd, fdobj.mode, fdobj.created])
        request = self.build_msg(LOAD, cmd, *payload) 
        recepient = recepient if recepient else self.sock
        ret = libc.send(recepient, cast(request, c_void_p), 
                         MSG_LEN, MSG_FLAGS)
        if ret == -1:
            error_msg = get_error_msg()
            raise SendError(error_msg)
        self.sendmsg(LOAD, cmd, fdobj.fd, recepient)

    def remove_fd(self, name):
        # XXX build protocol send, no need for sendmsg
        fdobj = self.get_fd(name)
        self.sendmsg(CLOSE, CLS_FD, fdobj[1])

    def recvmsg(self, sock, cmd, payload=None):
        msg = pointer(msghdr(RECV, cmd, payload))
        # set up a poll timout -- client disconnects -- will this call block indefin?
        if libc.recvmsg(sock, msg, MSG_SERV) == -1:
            error_msg = get_error_msg()
            raise RecvmsgError(error_msg)
        return msg

    def sendmsg(self, protocol, cmd, payload=None, client=None):
        receipent = client if client is not None else self.sock
        msg = pointer(msghdr(protocol, cmd, payload, client))
        if libc.sendmsg(receipent, msg, MSG_SERV) == -1:
            error_msg = get_error_msg() 
            raise SendmsgError(error_msg) 

    def build_msg(self, protocol, cmd, *payload):
        req_buffer = REQ_BUFFER()
        request = (PROTOCOL_NAMES[protocol], COMMAND_NAMES[cmd]) + payload
        req_buffer.value = ':'.join(request)
        return req_buffer

    def createfd(self, path, mode, fd=None, client=None, created=None):
        client = client if client else self.sock
        fdobj = FileDescriptor(path=path, mode=mode, fd=fd,
                               client=client, created=created)
        self.fdpool.add(client, fdobj)

    def extract_fd(self, msg): 
        fd = CMSG_DATA(msg.contents.msg_control)
        return fd
        
    def ld_protomsg(self, sock, cmd, msg):
        path, created = msg[3], float(msg[6]) 
        msg = self.recvmsg(sock, cmd)
        fd = self.extract_fd(msg)
        self.createfd(path, cmd, fd, sock, created)

    def recv_protomsg(self, sock, cmd, msg):
        if cmd == RECV_PEER:
            self.client_peer_req(sock)
        elif cmd == RECV_FD:
            pass
        elif cmd == RECV_CMD:
            self.recvmsg(sock, RECV_CMD, msg)
        
    def pass_protomsg(self, sock, cmd, msg):
        if cmd == PASS_PEER:
            self.recvpeers(msg)
        elif cmd == PASS_FD:
            self.passfd(*msg[2:])

    def cls_protomsg(self, sock, cmd, msg):
        if cmd == CLS_FD:
            vector = self.unpack_vector(msg)
            self.fdpool.remove(vector.name)
        elif cmd == CLS_ALL:
            pass
        else:
            raise InvalidCmdError(cmd)

    def ref_protomsg(self, sock, cmd, msg):
        if cmd == RET_FD:
            pass
        elif cmd == REFCNT_FD:
            pass
        else:
            raise InvalidCmdError(cmd)
