#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from time import sleep
from fdbus import *


class FdbusTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.cwd = os.getcwd()
        self.server_path = '/tmp/fdbus_test_server'
        if os.path.exists(self.server_path):
            os.unlink(self.server_path)
        self.test_server = Server(self.server_path)
        self.test_server.start()
        self.test_fd_name = 'test_fdbus_file'
        self.test_fd_path = os.path.join(self.cwd, self.test_fd_name)
        self.test_client = Client(self.server_path) 
        self.test_client.connect()
        
    def test_server_path(self):
        self.assertTrue(os.path.exists(self.server_path))
   
    def test_server_running(self):
        self.assertTrue(self.test_server.running) 

    def test_client_connection(self):
        self.assertTrue(self.test_client.connected)

    def test_client_createfd(self):
        with open(self.test_fd_path, 'w+') as test_file:
            test_file.write('fdbus test file')
        self.test_client.createfd(self.test_fd_path, O_RDONLY)
        fdpool = self.test_client.local_fds
        self.assertTrue(len(fdpool.fdobjs) == 1)

    def test_client_fdname(self):
        pool = self.test_client.local_fds
        test_fd = pool.fdobjs[self.test_fd_name][1]
        self.assertTrue(test_fd.name == self.test_fd_name)

    def test_client_fdpath(self):
        pool = self.test_client.local_fds
        test_fd = pool.fdobjs[self.test_fd_name][1]
        self.assertTrue(test_fd.path == self.test_fd_path)

    def test_client_fdmode(self):
        pool = self.test_client.local_fds
        test_fd = pool.fdobjs[self.test_fd_name][1]
        self.assertTrue(test_fd.mode == O_RDONLY)

    def test_server_pool(self):
        pool = self.test_server.clients
        self.assertTrue(len(pool.fd_pool) == 1)

    def test_client_loadfd(self):
        self.test_client.loadfd(self.test_fd_name)

    def test_server_recvfd(self):
        fdpool = self.test_server.fdpool.fdobjs
        self.assertTrue(len(fdpool) == 1)

    def test_server_clientfd_pool(self):
        client = self.test_server.fdpool.client_fdobjs
        self.assertTrue(len(client) == 1)

    @classmethod
    def tearDownClass(self):
        self.test_server.running = False
        os.unlink(self.test_fd_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
