#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import ctime
from threading import Thread
from signal import signal, SIGINT
from select import poll, POLLIN, POLLHUP

from ..fdbus_h import *
from ..exceptions.exceptions import *
from ..fdobjects.fdobjects import FileDescriptorPool, FileDescriptor, FDBus


class Server(FDBus, Thread):

    def __init__(self, path):
        super(Server, self).__init__(path)
        self.clients = ClientPool() 
        self.fdpool = FileDescriptorPool() 
        self.server_event_poll = poll()
        self.running = True
        self.server = self.socket()
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
        # have the server create an id, not just the fd of the client 
        # connection.  then send it back to client

    def client_ev(self, client, ev):
        if ev == POLLHUP:
            libc.close(client)
            del self.clients[client]
        else:
            self.recvmsg(client)

    def shutdown(self):
        libc.close.restype = c_int
        libc.unlink.restype = c_int
        ret = libc.close(self.server)
        if ret == -1:
            errno = get_errno()
            raise CloseError(errno)
        ret = libc.unlink(self.path)
        if ret == -1:
            errno = get_errno()
            raise UnlinkError(errno)
        self.close_pool()

    def server_interrupt(self, sig, frame):
        self.running = False
        self.shutdown()
        
    def current_clients(self):
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

# have a clients name/id themselves (str's)
class ClientPool(object):
        
    def __init__(self):
        self.fd_pool = {} 

    def add(self, client):
        self.fd_pool[client.fd] = client

    def remove(self, client):
        pass

    def dump(self):
        pass


class PyCClientWrapper(object):
    # specify / name -> each client ...?
    # provide more detailed info on each client.
    # or more decoupled client to fds 
    def __init__(self, client_c_fd):
        self.fd = client_c_fd
