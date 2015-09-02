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
        self.assertTrue(len(test_server.clients) == number_of_clients)

    def test_server_recvfd(self):
        self.assertTrue(len(test_server.fdpool) == number_of_clients + 1)


class FDBusClientTest(unittest.TestCase):

    def test_client_connection(self):
        for client in clients:
            self.assertTrue(client.connected)

    def test_client_createfd(self):
        for client in clients:
            self.assertTrue(len(client.fdpool) == 1)

    def test_client_fdname(self):
        for client_number, client in enumerate(clients):
            pool = client.fdpool
            test_fd_name = default_path + str(client_number)
            test_fd = pool.fdobjs[test_fd_name][1]
            self.assertTrue(test_fd.name == test_fd_name)

    def test_client_fdpath(self):
        for client_number, client in enumerate(clients):
            pool = client.fdpool
            test_fd_name = default_path + str(client_number)
            test_fd_path = os.path.join(cwd, test_fd_name)
            test_fd = pool.fdobjs[test_fd_name][1]
            self.assertTrue(test_fd.path == test_fd_path)

    def test_client_fdmode(self):
        for client_number, client in enumerate(clients):
            pool = client.fdpool
            test_fd_name = default_path + str(client_number)
            test_fd = pool.fdobjs[test_fd_name][1]
            self.assertTrue(test_fd.mode == O_RDONLY)

    def test_client_passfd(self):
        for client_number, client in enumerate(clients):
            for peer in client.peers:
                client.passfd(default_path + str(client_number), peer)
                sleep(0.5)
        for client in clients:
            self.assertTrue(len(client.fdpool) == number_of_clients + 1) 

    def test_client_getfd(self):
        for client in clients:
            client.getfd(server_test_file)
            sleep(0.5)
            pool = client.fdpool
            self.assertTrue(pool.fdobjs.get(server_test_file) is not None)
            

class FDBusClientPeersTest(unittest.TestCase):

    def test_client_peers(self):
        for client in clients:
            self.assertTrue(len(client.peers) == (number_of_clients - 1))

        
class FDBusClientClosingTest(unittest.TestCase):
    pass


def create_clients():
    clients = []
    for client in xrange(number_of_clients):
        client_path = default_path + str(client)
        test_path = os.path.join(cwd, client_path)
        c = Client(server_path)
        c.connect()
        with open(client_path, 'w+') as test_file:
            test_file.write(client_path)
        c.createfd(test_path, O_RDONLY)
        c.loadfd(client_path)
        clients.append(c)
    sleep(0.5)
    map(Client.getpeers, clients)
    return clients
         
def create_server_file():
    server_file = os.path.join(cwd, server_test_file)
    with open(server_file, 'w+') as test_file:
        test_file.write(server_file)

if __name__ == '__main__':
    server_path = '/tmp/fdbus_test_server'
    cwd = os.getcwd()
    number_of_clients = 2
    default_path = 'test_fdbus_file'
    server_test_file = 'test_server_file'
    create_server_file()
    if os.path.exists(server_path):
        os.unlink(server_path)
    test_server = Server(server_path)
    test_server.start()
    test_server.createfd(server_test_file, O_RDONLY)
    clients = create_clients()
    sleep(2)
    unittest.main(verbosity=3, exit=False)
    for client_number, client in enumerate(clients):
        os.remove(default_path + str(client_number))
        client.disconnect()
    os.remove(server_test_file)
    test_server.running = False
