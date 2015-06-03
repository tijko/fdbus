#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SocketError(Exception):
    pass

class ListenError(Exception):
    pass

class BindError(Exception):
    pass

class AcceptError(Exception):
    pass

class SendmsgError(Exception):
    pass

class ConnectError(Exception):
    pass

class RecvmsgError(Exception):
    pass

class ReadError(Exception):
    pass

class WriteError(Exception):
    pass

class OpenError(Exception):
    pass

class CloseError(Exception):
    pass

class LseekError(Exception):
    pass

class StatError(Exception):
    pass
