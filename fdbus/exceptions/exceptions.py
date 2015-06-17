#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..fdbus_h import *


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


class FileDescriptorError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        a FileDescriptor class method.

        This will be proprogated from the above libc calls down to the callee.
    """
    # XXX pass this more descriptive error or further propagations
    def __init__(self, fdobj):
        self.fdobj = fdobj

    def __str__(self):
        return "FileDescriptor error: %s" % repr(self.fdobj)


class MsghdrError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        a msghdr class.

        This error is from supplying a file descriptor argument without a
        command argument to specify an action the server is to take.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "Msghdr error: %s" % self.msg


class UnlinkError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.unlink.

        The errno is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, errno):
        self.errno = errno

    def __str__(self):
        return "libc.unlink error: %s" % libc.strerror(c_int(self.errno))


class UnknownDescriptorError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        a method that handles file descriptors.

        This error occurs whenever a reference to unknown descriptor is made 
        (i.e. it has not been created yet or has been removed.).
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "UnknownDescriptor: %s" % self.name
