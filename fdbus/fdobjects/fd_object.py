#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import fstat as stat
from fdbus_h import *


class ClientContainer(object):

    def __init__(self):
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
    # have client fds
    def __init__(self, path, fd=None):
        self.path = c_char_p(path)

    def fopen(self):
        libc.open.restype = c_int
        self.fd = libc.open(self.path, O_RDONLY)
        if (self.fd == -1):
            # raise exception
            print "Error in open"
        return self.fd

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
