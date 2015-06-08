#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from time import sleep
from fdbus import *


class FdbusTest(unittest.TestCase):

    def setUp(self):
        self.server_path = '/tmp/fdbus_test_server'
        self.test_server = Server(self.server_path)
        self.test_server.start()
        sleep(.4)
        self.test_client = Client(self.server_path) 
        self.test_client.connect()
        
    def test_server_path(self):
        self.assertTrue(os.path.exists(self.server_path))
   
    def test_server_running(self):
        self.assertTrue(self.test_server.running) 

    def test_client_connection(self):
        self.assertTrue(self.test_client.connected)

    def tearDown(self):
       self.test_server.running = False

if __name__ == '__main__':
    unittest.main()
