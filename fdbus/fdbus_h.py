#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import c_int, c_uint, c_longlong, c_ushort, c_char, \
                   c_void_p, c_char_p, POINTER, pointer, cast, \
                   sizeof, Structure, CDLL, get_errno, ARRAY

from threading import Thread
from exceptions.exceptions import *
from collections import defaultdict

from select import poll, POLLIN, POLLHUP, POLLNVAL


libc = CDLL('libc.so.6', use_errno=True)

libc.open.restype = c_int
libc.recv.restype = c_int
libc.send.restype = c_int
libc.close.restype = c_int
libc.unlink.restype = c_int
libc.socket.restype = c_int
libc.accept.restype = c_int
libc.strerror.argtype = c_int
libc.strerror.restype = c_char_p

# set command protocols for communication to server-client
# 
# to start have the send/request of a fd - basic -
# an additional cmd might be to request server status information
# on a multiplex server the cmds will natural become more involved 
#
# commands for client-server communica

LOAD = 0x0
LOAD_RDONLY = 0x0
LOAD_WRONLY = 0x1
LOAD_RDWR   = 0x2

RECV = 0x1
RECV_FD   = 0x1
RECV_PEER = 0x2
RECV_CMD  = 0x4

PASS = 0x10
PASS_FD   = 0x10
PASS_PEER = 0x20

CLOSE = 0x100
CLS_FD  = 0x100
CLS_ALL = 0x200

REFERENCE = 0x200
RET_FD    = 0x100
REFCNT_FD = 0x200

PATH_MAX    = 0x400
FNAME_MAX   = 0x100
CREATED_MAX = 0x10
PROTO_MAX   = 0x8
MODE_MAX    = 0x8 
FD_MAX      = 0x8
# MAX_CLIENTS ...
REQ_MSG_MAX = sum([PATH_MAX, FNAME_MAX, CREATED_MAX, 
                   PROTO_MAX, MODE_MAX, FD_MAX])
 
REQ_BUFFER = ARRAY(c_char, REQ_MSG_MAX - 1)

EVENT_MASK = POLLIN | POLLHUP | POLLNVAL

MSG_FLAGS = c_int(0)
MSG_LEN = c_int(REQ_MSG_MAX)
# protocol number-to-name hash for building the protocol
PROTOCOL_NAMES = {LOAD:'LOAD', RECV:'RECV', PASS:'PASS', 
                  CLOSE:'CLOSE', REFERENCE:'REFERENCE'}

PROTOCOL_NUMBERS = {v:k for k,v in PROTOCOL_NAMES.items()}

COMMAND_NAMES = {LOAD_RDONLY:'LOAD_RDONLY', LOAD_WRONLY:'LOAD_WRONLY', 
                 LOAD_RDWR:'LOAD_RDWR', RECV_FD:'RECV_FD', 
                 RECV_PEER:'RECV_PEER', RECV_CMD:'RECV_CMD', PASS_FD:'PASS_FD',
                 PASS_PEER:'PASS_PEER', CLS_FD:'CLS_FD', CLS_ALL:'CLS_ALL',
                 RET_FD:'RET_FD', REFCNT_FD:'REFCNT_FD'}

COMMAND_NUMBERS = {v:k for k,v in COMMAND_NAMES.items()}

# linux values 
SOCK_ADDRDATA_SZ = 14
UNIX_PATH_MAX    = 108

FDBUS_IOVLEN = 0x1

O_RDONLY = 0x0
O_WRONLY = 0x1
O_RDWR   = 0x2

SCM_RIGHTS = c_int(0x01)
SOL_SOCKET = c_int(0x01)

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

PROTO_DEFAULT = 0
SOCK_STREAM   = 1
AF_UNIX       = 1

DEFAULT_CLIENTS = 3

MSG_CMSG_CLOEXEC = 2 << 29
MSG_SERV = c_int(0)

# conversion of linux data types set to their ctypes size
socklen_t = c_uint
size_t = c_uint
off_t = c_longlong

def get_error_msg():
    errno = get_errno()
    return libc.strerror(c_int(errno))


class peermsg(Structure):

    _fields_ = [('length', c_int), ('peers', c_void_p)]

    def __init__(self, peers=None):
        if peers is None:
            self.length = c_int(0)
            self.peers = c_void_p()
        else:
            peer_length = len(peers)
            peer_array = ARRAY(c_int, peer_length)
            self.length = c_int(peer_length)
            self.peers = cast(c_void_p, peer_array(peers))
            

class sockaddr(Structure):

    _fields_ = [('sa_family', c_ushort), 
                ('sa_data', c_char * SOCK_ADDRDATA_SZ)]


class sockaddr_un(Structure):

    _fields_ = [('sun_family', c_ushort), 
                ('sun_path', c_char * UNIX_PATH_MAX)]

    def __init__(self, family, path):
        self.sun_family = c_ushort(family)
        self.sun_path = path


class iovec(Structure):

    _fields_ = [('iov_base', c_void_p), ('iov_len', size_t)]

    def __init__(self, io_data):
        self.iov_base = cast(io_data, c_void_p) 
        self.iov_len = size_t(sizeof(c_char) * FDBUS_IOVLEN)


class msghdr(Structure):

    _fields_ = [('msg_name', c_void_p), ('msg_namelen', socklen_t), 
                ('msg_iov', POINTER(iovec)), ('msg_iovlen', size_t),
                ('msg_control', c_void_p), ('msg_controllen', size_t),
                ('msg_flags', c_int)]

    def __init__(self, protocol, cmd, payload=None, client=None):
        # If no 'fd' parameter is passed and no 'cmd' parameter is passed upon 
        # initialization, this is a header for a "receiver" call.  Otherwise 
        # this will initialized for a "sender" call, which will need a slightly 
        # different arrangement of the structure's fields.
        #
        # Of The "sender" and "receiver" 'msghdr's, the "sender" 'iovec' struct
        # will be set with a command protocol number inside of 'iovec' struct 
        # base field array for the transmission over `sendmsg` and the 
        # "receiver" 'iovec' will be initialized with a empty int array large 
        # enough to contain that message passed through  `recvmsg`. 
        #
        # With the cmsghdr its the similiar idea, where the "sender" will 
        # have the struct initialized with its data set and the "receiver"
        # will have an empty array assigned to its data field.
        if protocol == RECV or protocol == CLOSE or protocol == REFERENCE:
            ctrl_msg = CTRL_MSG_RECV()
            if cmd == RECV_PEER:
                pass
            elif cmd == CLS_ALL or cmd == RECV_CMD:
                pass
            else:
                pass
        else:
            if cmd == PASS_PEER or cmd == RECV_PEER:
                pass
            else:
                ctrl_msg = pointer(cmsghdr(payload))
        iov_base = c_char_p('^')
        self.msg_iov = pointer(iovec(iov_base))
        self.msg_iovlen = size_t(FDBUS_IOVLEN)
        self.msg_control = cast(ctrl_msg, c_void_p)
        self.msg_controllen = CTRL_MSG_LEN


class cmsghdr(Structure):

    _fields_ = [('cmsg_len', size_t), ('cmsg_level', c_int),
                ('cmsg_type', c_int), ('cmsg_data', c_int)]

    def __init__(self, fd):
        self.cmsg_len = CMSG_LEN(sizeof(c_int))
        self.cmsg_level = SOL_SOCKET
        self.cmsg_type = SCM_RIGHTS
        self.cmsg_data = fd


class cmsghdr_flex(Structure):

    # This is a custom cmsghdr to use with the CMSG macros.  The only difference 
    # between this struct and the cmsghdr struct above is that the 'cmsg_data' 
    # field isn't in the former.  This is to account for the 'cmsg_data' field
    # being a flex array and the macros calculating the size.

    _fields_ = [('cmsg_len', c_int), 
                ('cmsg_level', c_int), 
                ('cmsg_type', c_int)]


# cmsg macros
CMSG_SPACE = lambda container: (CMSG_ALIGN(sizeof(cmsghdr_flex)) + 
                                CMSG_ALIGN(container))

CMSG_LEN = lambda data_type: CMSG_ALIGN(sizeof(cmsghdr_flex)) + data_type

CMSG_ALIGN = lambda data_len: ((data_len + sizeof(c_int) - 1) & 
                               ~(sizeof(c_int) - 1))

CMSG_DATA = lambda msg: cast(msg, POINTER(cmsghdr)).contents.cmsg_data

CTRL_MSG_LEN = CMSG_SPACE(sizeof(c_int))
CTRL_MSG_RECV = c_char * CTRL_MSG_LEN
