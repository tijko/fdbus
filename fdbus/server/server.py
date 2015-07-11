#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import ctime
from threading import Thread
from signal import signal, SIGINT
from select import poll, POLLIN, POLLHUP, POLLNVAL

from ..fdbus_h import *
from ..exceptions.exceptions import *
from ..fdobjects.fdobjects import FileDescriptorPool, FileDescriptor, FDBus


class Server(FDBus):#, Thread):

    def __init__(self, path):
        super(Server, self).__init__(path)
        self.clients = ClientPool() 
        self.server_event_poll = poll()
        self.running = True
        self.sock = self.socket()
        self.event_mask = POLLIN | POLLHUP | POLLNVAL
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
            error_msg = get_error_msg()
            raise AcceptError(error_msg)
        self.server_event_poll.register(client, self.event_mask)
        self.clients[client] = PyCClientWrapper(client)
        # have the server create an id, not just the fd of the client 
        # connection.  then send it back to client

    def client_ev(self, client, ev):
        if ev & (POLLHUP | POLLNVAL):
            # set up array of functions to take
            # point to which one occured
            libc.close(client)
            self.server_event_poll.unregister(client)
            self.clients.remove(client)
        else:
            self.recvmsg(client, RECV_CMD)

    def shutdown(self):
        libc.close.restype = c_int
        libc.unlink.restype = c_int
        ret = libc.unlink(self.path)
        if ret == -1:
            error_msg = get_error_msg()
            raise UnlinkError(error_msg)
        if any(ret == -1 for ret in map(libc.close, self.clients)):
            error_msg = get_error_msg()
            raise CloseError(error_msg)
        ret = libc.close(self.sock)
        if ret == -1:
            error_msg = get_error_msg()
            raise CloseError(error_msg)
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
            error_msg = get_error_msg()
            raise BindError(error_msg)
        if self.listen == -1:
            error_msg = get_error_msg()
            raise ListenError(errno)
        self.server_event_poll.register(self.sock, self.event_mask)
        while self.running:
            events = self.server_event_poll.poll(1)
            if events:
                if events[0][0] == self.sock:
                    self.accept()            
                else:
                    self.client_ev(*events[0])
        self.shutdown()

# have a clients name/id themselves (str's)
class ClientPool(object):
        
    def __init__(self):
        self.fdpool = {} 

    def remove(self, client):
        del self.fdpool[client]
    
    def dump(self):
        return self.fdpool.keys()

    def __len__(self):
        return len(self.fdpool)

    def __iter__(self):
        for fd in self.fdpool:
            yield fd

    def __setitem__(self, item, value):
        self.fdpool[item] = value

    def __getitem__(self, item):
        try:
            client = self.fdpool[item]
        except KeyError:
            raise UnknownDescriptorError(item)
        return client

    def __len__(self):
        return len(self.fdpool)

    def __str__(self):
        return str(self.fdpool)


class PyCClientWrapper(object):
    # specify / name -> each client ...?
    # provide more detailed info on each client.
    # or more decoupled client to fds 
    def __init__(self, client_c_fd):
        self.fd = client_c_fd
