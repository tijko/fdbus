#!/usr/bin/env python
# -*- coding: utf-8 -*-

from select import *

from ..fdbus_h import *
from ..exceptions.exceptions import *
from ..fdobjects.fdobjects import FileDescriptor, FileDescriptorPool, FDBus


class Client(FDBus, Thread):

    def __init__(self, path):
        super(Client, self).__init__(path)
        self.sock = self.socket() 
        self.connected = False
        self.peers = None

    def connect(self):
        self.client_address = pointer(sockaddr_un(AF_UNIX, self.path))
        self.client_address.contents.sun_family = AF_UNIX
        self.client_address.contents.sun_path = self.path
        if (libc.connect(self.sock, cast(self.client_address, 
                         POINTER(sockaddr)), sizeof(sockaddr_un)) == -1):
            error_msg = get_error_msg()
            raise ConnectError(error_msg)
        self.connected = True
        self.start()
   
    def writefd(self):
        pass

    def closefd(self):
        pass

    def remove(self, name):
        self.remove_fd(name)        

    def passfd(self, name, peer):
        self.send_fd(PASS, name, peer)

    def loadfd(self, name):
        # depending on function, protocol is not needed for formatting
        # of the request message.
        #
        # with loadfd the name (if a valid fdobj) can reference the fd
        # attributes and affiliated data.
        #
        # 'LOAD:LOAD_RDONLY:testfile:/home/tijko/testfile/created:1233492.3929' 
        self.send_fd(LOAD, name)

    def getpeers(self):
        self.sendmsg(PASS, PEER_DUMP)
        self.recvmsg(self.sock, RECV, RECV_PEER)

    def readfd(self, fd):
        rd_buffer = (c_char * 2048)()
        rd_buffer_len = 2048 - 1
        libc.read(c_int(fd), rd_buffer, rd_buffer_len)
        return rd_buffer

    def client_msg(self, ev):
        if ev & (POLLHUP | POLLNVAL):
            libc.close(self.sock)
            self.connected = False
        else:
            client_msg_buffer = cast(REQ_BUFFER(), c_void_p)
            ret = libc.recv(self.sock, client_msg_buffer, MSG_LEN, MSG_FLAGS)
            if ret == -1:
                error_msg = get_error_msg()
                raise RecvError(error_msg)
            msg_raw = cast(client_msg_buffer, c_char_p).value
            msg = msg_raw.split(':')
            self.proto_funcs[PROTOCOL_NUMBERS[msg[0]]](self.sock, msg[1], msg)

    # will locking be needed on handling the incoming messages?
    def run(self):
        self.client_msg_queue = poll()
        self.client_msg_queue.register(self.sock, EVENT_MASK)
        while self.connected:
            events = self.client_msg_queue.poll(1)
            if events:
                self.client_msg(events[0][1])
        self.client_msg_queue.unregister(self.sock)
