#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

from fdbus import *


class FdbusTest(unittest.TestCase):

    def setUp(self):
        self.server_path = '/tmp/fdbus_server'
        self.test_server = Server(self.server_path)

    def tearDown(self):
       self.test_server.running = False
 
    def test_server(self):
        self.assertTrue(os.path.exists('/tmp/fdbus_server'))


if __name__ == '__main__':
    unittest.main()
