from .cache import cachely
from .loader import Loader

VERSION = (0, 1, 0)

def get_version():
    return '.'.join(map(str, VERSION))