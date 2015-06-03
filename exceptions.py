#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fdbus_h import *


class SocketError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.socket

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.socket error: %s" % libc.strerror(c_int(self.errno))

class ListenError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.listen

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.listen error: %s" % libc.strerror(c_int(self.errno))
    
class BindError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.bind

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.bind error: %s" % libc.strerror(c_int(self.errno))

class AcceptError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.accept

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.accept error: %s" % libc.strerror(c_int(self.errno))

class SendmsgError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.sendmsg

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.sendmsg error: %s" % libc.strerror(c_int(self.errno))

class ConnectError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.connect

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.connect error: %s" % libc.strerror(c_int(self.errno))

class RecvmsgError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.recvmsg

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.recvmsg error: %s" % libc.strerror(c_int(self.errno))

class ReadError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.read

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.read error: %s" % libc.strerror(c_int(self.errno))

class WriteError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.write

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.write error: %s" % libc.strerror(c_int(self.errno))

class OpenError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.open

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.open error: %s" % libc.strerror(c_int(self.errno))

class CloseError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.close

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.close error: %s" % libc.strerror(c_int(self.errno))

class LseekError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.lseek

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.lseek error: %s" % libc.strerror(c_int(self.errno))

class StatError(Exception):
    """
        Exception class raised in the event of an error returned from a call to
        libc.stat

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.stat error: %s" % libc.strerror(c_int(self.errno))
