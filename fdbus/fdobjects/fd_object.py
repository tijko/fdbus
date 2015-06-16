#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from os import fstat as stat
from time import ctime

from ..fdbus_h import *
from ..exceptions.exceptions import *

# a client name/id field (i.e. a process name or identifier/pid)
fdobj = namedtuple('File_Descriptor', ('name', 'path', 'fd', 'mode', 
                                                'client', 'created'))


class FileDescriptorPool(object):

    def __init__(self):
        self.fdobjs = {}
        self.client_fdobjs = defaultdict(list)

    def add(self, client, fdobj):
        self.fdobjs[fdobj.name] = [client, fdobj]
        self.client_fdobjs[client].append(fdobj)

    def remove(self, fdobj):
        pass

    def retrieve(self, fdobj):
        pass

    def bypath(self):
        pass

    def byfileno(self):
        pass

    def byfname(self):
        pass

    def __iter__(self):
        pass


class FileDescriptor(object):

    def __new__(self, **kwargs):
        path = kwargs.get('path')
        if path is None:
            raise FileDescriptorError(self)
        name = path.split('/')[-1]
        mode = kwargs.get('mode')
        if mode is None:
            raise FileDescriptorError(self)
        fd = kwargs.get('fd')
        if fd is None:
            fd = FileDescriptor.fopen(path, mode)
        client = kwargs.get('client')
        created = ctime()
        return _FileDescriptor(name, path, fd, mode, client, created)

    @staticmethod
    def fopen(path, mode):
        libc.open.restype = c_int
        fd = libc.open(path, mode)
        if fd == -1:
            errno = get_errno()
            raise OpenError(errno)
        return fd

class _FileDescriptor(fdobj):

    def __init__(self, name, path, fd, mode, client, created):
        super(_FileDescriptor, self).__init__(name, path, fd, mode, 
                                                   client, created)
        self.refcnt = 1

    def fsize(self):
        try:
            file_size = stat(self.fd).st_size
        except NameError: # handle different errors
            # raise
            print "File is not open"
        return file_size

    def fpos(self): # handle errors below
        offset = libc.lseek(self.fd, 0, SEEK_CUR)
        return offset

    def fstart(self):
        # handle errors
        offset = libc.lseek(self.fd, 0, SEEK_SET)

    def fend(self):
        # handle errors
        offset = libc.lseek(self.fd, 0, SEEK_END)

    def fset(self, pos):
        # handle errors
        c_pos = off_t(pos)
        offset = libc.lseek(self.fd, c_pos, SEEK_SET)

    def fclose(self):
        # handle errors
        ret = libc.close(self.fd)

    def __enter__(self):
        # handle errors
        return self.fd

    def __exit__(self, exc_type, exc_value, traceback):
        # handle errors
        self.fclose()
