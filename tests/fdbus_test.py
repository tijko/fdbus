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


class FDBusServerClosingTest(unittest.TestCase):

    def test_server_removeclient(self):
        pool_w_client = test_server.current_clients
        client = pool_w_client[0]
        test_server.remove_client(client)
        pool_wo_client = test_server.current_clients
        self.assertTrue(client not in pool_wo_client)


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

    def test_client_peers(self):
        test_client.getpeers()
        peers = test_client.peers
        self.assertTrue(len(peers) == 1)


class FDBusClientClosingTest(unittest.TestCase):

    def test_server_remove_clientfd(self):
        test_client.remove(test_fd_name)
        sleep(1)
        pool = test_server.fdpool.fdobjs
        self.assertTrue(len(pool) == 0)


def display_test_errors(errors):
    for error in errors:
        print ''.join(['\n' + str(error[0]) + '\n'] + list(error[1:]))

def run_test(test):
    suite = unittest.TestSuite()
    result = unittest.TestResult()
    result.buffer = True
    suite.addTest(test)
    suite.run(result)
    print result
    map(display_test_errors, [result.errors, result.failures])
    

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
    test_client.connect()
    with open(test_fd_path, 'w+') as test_file:
        test_file.write('fdbus test file')
    test_client.createfd(test_fd_path, O_RDONLY)
    test_client.loadfd(test_fd_name)
    client = unittest.TestLoader()
    server = unittest.TestLoader()
    clientcls = unittest.TestLoader()
    servercls = unittest.TestLoader()
    suiteClient = client.loadTestsFromTestCase(FDBusClientTest)
    suiteServer = server.loadTestsFromTestCase(FDBusServerTest)
    suiteClientcls = clientcls.loadTestsFromTestCase(FDBusClientClosingTest)
    suiteServercls = servercls.loadTestsFromTestCase(FDBusServerClosingTest)
    tests = [suiteServer, suiteClient, suiteClientcls, suiteServercls]
    for test in tests:
        sleep(1)
        run_test(test)
    test_server.running = False
    os.remove(test_fd_path)
