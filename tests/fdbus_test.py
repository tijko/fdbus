#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from fdbus import *


class FdbusTest(unittest.TestCase):

    def setUp(self):
        self.server_path = '/tmp/fdbus_server'
        self.test_server = Server(self.server_path)
        self.test_server.start()

    def tearDown(self):
       self.test_server.running = False

    def test_server_path(self):
        self.assertTrue(os.path.exists('/tmp/fdbus_server'))
   
    def test_server_running(self):
        self.assertTrue(self.test_server.running) 


if __name__ == '__main__':
    unittest.main()
