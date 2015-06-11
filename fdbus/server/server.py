#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import ctime
from threading import Thread
from signal import signal, SIGINT
from collections import defaultdict
from select import poll, POLLIN, POLLHUP

from ..fdbus_h import *
from ..exceptions.exceptions import *
from ..fdobjects.fd_object import FileDescriptorPool


class Server(Thread):

    def __init__(self, path):
        super(Server, self).__init__()
        self.clients = ClientPool() 
        self.server_event_poll = poll()
        self.path = path
        self.running = True
        self.server = self.socket()
        self.cmd_funcs = {LOAD:self.ld_cmdmsg, PASS:self.pass_cmdmsg,
                          CLOSE:self.cls_cmdmsg, REFERENCE:self.ref_cmdmsg}
        signal(SIGINT, self.server_interrupt)

    def socket(self):
        libc.socket.restype = c_int
        server = libc.socket(AF_UNIX, SOCK_STREAM, PROTO_DEFAULT)
        if server == -1:
            errno = get_errno()
            raise SocketError(errno)
        return server

    @property
    def listen(self):
        return libc.listen(self.server, DEFAULT_CLIENTS)

    @property
    def bind(self):
        server_address = pointer(sockaddr_un(AF_UNIX, self.path))
        self.serv_sk_addr = cast(server_address, POINTER(sockaddr))
        server_size = sizeof(sockaddr_un)
        return libc.bind(self.server, self.serv_sk_addr, server_size)

    def accept(self):
        libc.accept.restype = c_int
        client_size = c_int(sizeof(sockaddr_un))
        client_size_ptr = pointer(client_size)
        client = libc.accept(self.server, self.serv_sk_addr, client_size_ptr)
        if client == -1:
            errno = get_errno()
            raise AcceptError(errno)
        py_client = PyCClientWrapper(client) 
        self.server_event_poll.register(client, POLLIN | POLLHUP)
        self.clients.add(py_client)

    def client_ev(self, client, ev):
        if ev == POLLHUP:
            libc.close(client)
            del self.clients[client]
        else:
            self.recvmsg(client)

    def shutdown(self):
        # check for errors
        libc.close(self.server)
        libc.unlink(self.path)
        # call a close on client pool

    def server_interrupt(self, sig, frame):
        self.running = False
        self.shutdown()
        
    def current_clients(self):
        pass

    def recvmsg(self, client):
        msg = pointer(msghdr())
        # set up a poll timout -- client disconnects -- will this call block indefin?
        if libc.recvmsg(client, msg, MSG_SERV) == -1:
            errno = get_errno()
            raise RecvmsgError(errno)
        self.get_cmdmsg(msg)            

    def sendmsg(self):
        pass

    def get_cmdmsg(self, msg):
        mhdr = msg.contents
        iovhdr = msg.contents.msg_iov.contents
        iovlen = msg.contents.msg_iovlen # another future recvmsg call
        cmd_vec = cast(iovhdr.iov_base, POINTER(c_int))
     
    def ld_cmdmsg(self, cmd, msg):
        pass

    def pass_cmdmsg(self, cmd, msg):
        pass

    def cls_cmdmsg(self, cmd, msg):
        pass

    def ref_cmdmsg(self, cmd, msg):
        pass

    def run(self):
        # poll for incoming messages to shutdown
        if self.bind == -1:
            errno = get_errno()
            raise BindError(errno)
        if self.listen == -1:
            errno = get_errno()
            raise ListenError(errno)
        self.server_event_poll.register(self.server, POLLIN | POLLHUP)
        while self.running:
            events = self.server_event_poll.poll(2)
            if events:
                if events[0][0] == self.server:
                    self.accept()            
                else:
                    self.client_ev(*events[0])
        self.shutdown()

class ClientPool(object):
        
    def __init__(self):
        self.fd_pool = {} 

    def add_client(self, client):
        self.fd_pool[client.fd] = client
        self.client_fds[client.name]

    def add_client_fdobj(self, name, fdobj):
        self.client_fds[name].append(fdobj)

    def remove(self, client):
        pass

    def dump(self):
        pass

class PyCClientWrapper(object):

    def __init__(self, client_c_fd):
        self.fd = client_c_fd
