#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from fdbus import *
from time import sleep


class FDBusServerTest(unittest.TestCase):

    def test_server_path(self):
        self.assertTrue(os.path.exists(server_path))

    def test_server_running(self):
        self.assertTrue(test_server.running) 

    def test_server_pool(self):
        self.assertTrue(len(test_server.clients) == 1)

    def test_server_recvfd(self):
        fdpool = test_server.fdpool.fdobjs
        self.assertTrue(len(fdpool) == 1)

class FDBusClientTest(unittest.TestCase):

    def test_client_connection(self):
        self.assertTrue(test_client.connected)

    def test_client_createfd(self):
        pool = test_client.fdpool
        self.assertTrue(len(pool.fdobjs) == 1)

    def test_client_fdname(self):
        pool = test_client.fdpool
        test_fd = pool.fdobjs[test_fd_name][1]
        self.assertTrue(test_fd.name == test_fd_name)

    def test_client_fdpath(self):
        pool = test_client.fdpool
        test_fd = pool.fdobjs[test_fd_name][1]
        self.assertTrue(test_fd.path == test_fd_path)

    def test_client_fdmode(self):
        pool = test_client.fdpool
        test_fd = pool.fdobjs[test_fd_name][1]
        self.assertTrue(test_fd.mode == O_RDONLY)

class FDBusClientPeersTest(unittest.TestCase):
    pass

class FDBusClientClosingTest(unittest.TestCase):
    pass


if __name__ == '__main__':
    cwd = os.getcwd()
    server_path = '/tmp/fdbus_test_server'
    if os.path.exists(server_path):
        os.unlink(server_path)
    test_server = Server(server_path)
    test_server.start()
    test_fd_name = 'test_fdbus_file'
    test_fd_path = os.path.join(cwd, test_fd_name)
    test_client = Client(server_path) 
    sleep(2)
    test_client.connect()
    with open(test_fd_path, 'w+') as test_file:
        test_file.write('fdbus test file')
    test_client.createfd(test_fd_path, O_RDONLY)
    test_client.loadfd(test_fd_name)
    unittest.main(verbosity=3, exit=False)
    test_client.connected = False
    test_server.running = False
    os.remove(test_fd_path)
