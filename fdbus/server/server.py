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
        self.server_event_poll = poll()
        self.running = True
        self.sock = self.socket()
        signal(SIGINT, self.server_interrupt)

    @property
    def listen(self):
        return libc.listen(self.sock, DEFAULT_CLIENTS)

    @property
    def bind(self):
        server_address = pointer(sockaddr_un(AF_UNIX, self.path))
        self.serv_sk_addr = cast(server_address, POINTER(sockaddr))
        server_size = sizeof(sockaddr_un)
        return libc.bind(self.sock, self.serv_sk_addr, server_size)

    def accept(self):
        libc.accept.restype = c_int
        client_size = c_int(sizeof(sockaddr_un))
        client_size_ptr = pointer(client_size)
        client = libc.accept(self.sock, self.serv_sk_addr, client_size_ptr)
        if client == -1:
            errno = get_errno()
            raise AcceptError(errno)
        self.server_event_poll.register(client, POLLIN | POLLHUP)
        self.clients[client] = PyCClientWrapper(client)
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
        ret = libc.unlink(self.path)
        if ret == -1:
            errno = get_errno()
            raise UnlinkError(errno)
        if any(ret == -1 for ret in map(libc.close, self.clients)):
            errno = get_errno()
            raise CloseError(errno)
        ret = libc.close(self.sock)
        if ret == -1:
            errno = get_errno()
            raise CloseError(errno)
        self.close_pool()

    def server_interrupt(self, sig, frame):
        self.running = False
        self.shutdown()
        
    @property
    def current_clients(self):
        return self.clients.dump()

    def remove_client(self, client):
        self.clients.remove(client)

    def run(self):
        # poll for incoming messages to shutdown
        if self.bind == -1:
            errno = get_errno()
            raise BindError(errno)
        if self.listen == -1:
            errno = get_errno()
            raise ListenError(errno)
        self.server_event_poll.register(self.sock, POLLIN | POLLHUP)
        while self.running:
            events = self.server_event_poll.poll(2)
            if events:
                if events[0][0] == self.sock:
                    self.accept()            
                else:
                    self.client_ev(*events[0])
        self.shutdown()

# have a clients name/id themselves (str's)
class ClientPool(object):
        
    def __init__(self):
        self.fd_pool = {} 

    def remove(self, client):
        try:
            del self.fd_pool[client]
        except KeyError:
            raise UnKnownFileDescriptorError(client)

    def dump(self):
        return self.fd_pool.keys()

    def __iter__(self):
        for fd in self.fd_pool:
            yield fd

    def __setitem__(self, item, value):
        self.fd_pool[item] = value

    def __getitem__(self, item):
        try:
            client = self.fd_pool[item]
        except KeyError:
            raise UnKnownFileDescriptorError(item)
        return client

    def __len__(self):
        return len(self.fd_pool)


class PyCClientWrapper(object):
    # specify / name -> each client ...?
    # provide more detailed info on each client.
    # or more decoupled client to fds 
    def __init__(self, client_c_fd):
        self.fd = client_c_fd
