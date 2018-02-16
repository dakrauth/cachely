import os
import random
import logging
import requests
from importlib import import_module


USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
    'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
)

logger = logging.getLogger(__name__)


def default_cachely_dirname():
    dirname = os.environ.get('CACHELY_DIR')
    if not dirname:
        default = os.path.join(os.path.expanduser('~'), '.cache')
        dirname = os.path.join(
            os.environ.get('XDG_CACHE_HOME', default),
            'cachely'
        )

    return dirname


def read_url(url, user_agent='random', extra_headers=None):
    '''
    A very simplified get request to the given ``url``.
    
    Returns a 2-tuple of (content_bytes, content_type)
    '''
    headers = {'accept-language': 'en-US,en'}
    if user_agent:
        headers['User-Agent'] = (
            random.choice(USER_AGENTS)
            if user_agent == 'random'
            else user_agent
        )
    
    if extra_headers:
        headers.update(extra_headers)

    r = requests.get(url, headers=headers)
    if not r.ok:
        raise requests.HTTPError('URL {}: {}'.format(r.reason, url))
        
    return (r.content, r.headers.get('content-type'))


def absolute_filename(filename):
    '''
    Do all those annoying things to arrive at a real absolute path.
    '''
    return os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))


def write_file(filename, data, encoding='utf8'):
    '''
    Write ``data`` to file ``filename``. ``data`` should be bytes, but if data
    is type str, it will be encode using ``encoding``.
    '''
    logger.debug('Writing file: {}'.format(filename))
    get_directory(os.path.dirname(filename))
    filename = absolute_filename(filename)
    if isinstance(data, str):
        data = data.encode(encoding)

    with open(filename, 'wb') as fp:
        fp.write(data)


def read_file(filename, encoding='utf8'):
    '''
    Read ``data`` from file ``filename``.
    '''
    filename = absolute_filename(filename)
    logger.debug('Reading file: {}'.format(filename))
    with open(filename, 'rb') as fp:
        data = fp.read()
    
    return data.decode(encoding) if encoding else data


def get_directory(pth):
    if not os.path.exists(pth):
        logger.debug('Creating directory {}'.format(pth))
        os.makedirs(pth)
    
    return pth


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        error_msg = '{} is not a module path'.format(dotted_path)
        logger.debug(error_message='')
        raise ImportError(error_msg)

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        error_msg = 'Module "{}" does not define a "{}" class'.format(
            module_path,
            class_name
        )
        logger.debug(error_msg)
        raise ImportError(error_msg)

