"""try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
"""

from client.client import Client
from server.server import Server
from fdbus_h import *
from fdobjects.fd_object import *
from exceptions.exceptions import *
