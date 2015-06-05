#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import c_int, c_uint, c_longlong, c_ushort, c_char, c_void_p, \
                   c_char_p, POINTER, pointer, cast, sizeof, Structure, CDLL


libc = CDLL('libc.so.6', use_errno=True)

libc.open.restype = c_int
libc.socket.restype = c_int
libc.accept.restype = c_int
libc.strerror.restype = c_char_p

# set command protocols for communication to server-client
# 
# to start have the send/request of a fd - basic -
# an additional cmd might be to request server status information
# on a multiplex server the cmds will natural become more involved 
#

# linux values 
SOCK_ADDRDATA_SZ = 14
UNIX_PATH_MAX = 108

O_RDONLY = c_int(0)

SCM_RIGHTS = c_int(0x01)
SOL_SOCKET = c_int(0x01)

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

PROTO_DEFAULT = 0
SOCK_STREAM = 1
AF_UNIX = 1

DEFAULT_CLIENTS = 3

MSG_CMSG_CLOEXEC = 2 << 29

# conversion of linux data types set to their ctypes size
socklen_t = c_uint
size_t = c_uint
off_t = c_longlong

# cmsg macros
CMSG_SPACE = lambda container: (CMSG_ALIGN(sizeof(cmsghdr_flex)) + 
                                CMSG_ALIGN(container))

CMSG_LEN = lambda data_type: CMSG_ALIGN(sizeof(cmsghdr_flex)) + data_type

CMSG_ALIGN = lambda data_len: ((data_len + sizeof(c_int) - 1) & 
                               ~(sizeof(c_int) - 1))


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
        self.iov_len = c_uint(len(io_data))

class msghdr(Structure):

    _fields_ = [('msg_name', c_void_p), ('msg_namelen', socklen_t), 
                ('msg_iov', POINTER(iovec)), ('msg_iovlen', size_t),
                ('msg_control', c_void_p), ('msg_controllen', size_t), 
                ('msg_flags', c_int)]

    def __init__(self, fd=None):
        ctrl_msg_len = CMSG_SPACE(sizeof(c_int))
        # If no 'fd' parameter is passed upon initialization, this is a header
        # for a "receiver" call.  Otherwise this will initialized for a
        # "sender" call, which will need a slightly different arrangement of
        # the structure's fields.
        #
        # Of The "sender" and "receiver" 'msghdr's, the "sender" 'iovec' struct
        # will be set with a minimal character array for the transmission over 
        # `sendmsg` and the "receiver" 'iovec' will be initialized with a empty
        # char array large enough to contain that message passed through 
        # `recvmsg`. 
        #
        # With the cmsghdr its the similiar idea, where the "sender" will 
        # have the struct initialized with its data set and the "receiver"
        # will have an empty array assigned to its data field.
        if fd is None:
            iov_base = (c_char * 1)()
            ctrl_msg = (c_char * ctrl_buffer_len)()
        else:
            iov_base = '*'
            ctrl_msg = pointer(cmsghdr(fd))
        self.msg_iov = pointer(iovec(iov_base))
        iovlen = len(self.msg_iov.contents.iov_base)
        self.msg_iovlen = size_t(iovlen)
        self.msg_control = cast(ctrl_msg, c_void_p)
        self.msg_controllen = ctrl_msg_len

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
