#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import fstat as stat


class FileDescriptor(object):
    # have client fds
    def __init__(self, path):
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
