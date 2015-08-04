#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..fdbus_h import *


class SocketError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.socket

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.socket error: %s" % self.msg


class ListenError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.listen

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.listen error: %s" % self.msg
    

class BindError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.bind

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.bind error: %s" % self.msg


class AcceptError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.accept

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.accept error: %s" % self.msg


class SendmsgError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.sendmsg

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.sendmsg error: %s" % self.msg


class SendError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.send

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.send error: %s" % self.msg


class ConnectError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.connect

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.connect error: %s" % self.msg


class RecvError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.recv

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.recv.error: %s" % self.msg


class RecvmsgError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.recvmsg

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.recvmsg error: %s" % self.msg


class ReadError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.read

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.read error: %s" % self.msg


class WriteError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.write

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.write error: %s" % self.msg


class OpenError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.open

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.open error: %s" % self.msg


class CloseError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.close

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.close error: %s" % self.msg


class LseekError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.lseek

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.lseek error: %s" % self.msg


class StatError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.stat

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.stat error: %s" % self.msg


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


class InvalidCmdError(Exception):

    """
        Exception class raised in the event of an invalid cmd passed through
        a protocol message.

        This error is from supplying a protocol function call with an invalid
        command argument to specify an action the caller is to take.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "InvalidCmdError error: %s" % self.msg


class InvalidProtoError(Exception):

    """
        Exception class raised in the event of an invalid protocol passed 
        through a protocol message.

        This error is from supplying a protocol function call with an invalid
        protocol argument to specify an action the caller is to take.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "InvalidProtoError error: %s" % self.msg


class UnlinkError(Exception):

    """
        Exception class raised in the event of an error returned from a call to
        libc.unlink.

        The msg is propagated from the system call giving a more descriptive
        reason for the fail.
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "libc.unlink error: %s" % self.msg


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
