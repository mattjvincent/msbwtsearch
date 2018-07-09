# -*- coding: utf-8 -*-
"""Useful generic utilities for the package.
"""
from collections import OrderedDict
import bz2
import gzip
import logging
import os
import random
import string


logging.basicConfig(format='[ENsimpl] [%(asctime)s] %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def format_time(start, end):
    """
    Format length of time between start and end.

    Args:
        start (long): the start time
        end (long): the end time

    Returns:
        str: a formatted string of hours, minutes, and seconds
    """
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


class ReverseProxied(object):
    """
    Wrap the application in this middleware and configure the
    front-end server (Apaccto add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    http://flask.pocoo.org/snippets/35/

    In apache:

    <Proxy http://server:port>
        Header add X_FORWADED_PATH "/myprefix"
        RequestHeader set X_FORWARDED_PATH "/myprefix"
    </Proxy>

    ProxyPass /myprefix http://server:port disablereuse=On
    ProxyPassReverse /myprefix http://server:port

    In nginx:

    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    """
    def __init__(self, app):
        """
        Constructor.

        Args:
            app: the application
        """
        self.app = app

    def __call__(self, environ, start_response):
        """
        Middleware call.

        Args:
            environ (dict): application environment
            start_response (Response.start_response): response method

        Returns:
            application
        """
        script_name = environ.get('HTTP_X_FORWARDED_PATH', '')

        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')

        if scheme:
            environ['wsgi.url_scheme'] = scheme

        return self.app(environ, start_response)


def get_logger():
    """Get the logger.

    Returns:
        logger: the logging object
    """
    return logging.getLogger(__name__)


def configure_logging(level=0):
    """Configure the logger with the specified level.

        0 = logging.WARNING is informational
        1 = logging.INFO is user debug
        2> = logging.DEBUG is developer debug

    Args:
        level (int): the logging level; defaults to 0
    """
    if level == 0:
        get_logger().setLevel(logging.WARN)
    elif level == 1:
        get_logger().setLevel(logging.INFO)
    elif level > 1:
        get_logger().setLevel(logging.DEBUG)


def dictify_row(cursor, row):
    """Turns the given row into a dictionary where the keys are the column names.

    Args:
        cursor (sqlite3.Cursor): the database cursor
        row (dict): the current row

    Returns:
        OrderedDict: dictionary with keys being column names
    """
    d = OrderedDict()
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]
    return d


def dictify_cursor(cursor):
    """
    Converts all cursor rows into dictionaries where keys are the column names.

    Args:
        cursor (sqlite3.Cursor): the database cursor

    Returns:
        list: list of ``OrderedDict`` objects with keys being column names
    """
    return [dictify_row(cursor, row) for row in cursor]


def format_time(start, end):
    """Format length of time between start and end.

    Args:
        start (float): the start time
        end (float): the end time

    Returns:
        str: a formatted string of hours, minutes, and seconds
    """
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


def str2bool(val):
    """Convert a string into a boolean.

    Args:
        val (str): a string representing True

    Returns:
        bool: True if ``val`` is 'true', '1', 't', 'y', or 'yes'
    """
    return str(val).lower() in ['true', '1', 't', 'y', 'yes']



def get_file_name(url, directory=None):
    """Get the last part of the file name.

    Args:
        url (str): url of file
        directory: (optional) directory name

    Returns:
        str: full path of file
    """
    download_file_name = url.split('/')[-1]
    local_directory = directory if directory else os.getcwd()
    return os.path.abspath(os.path.join(local_directory, download_file_name))


def is_url(url):
    """Check if this is a URL or not by just checking the protocol

    Args:
        url (str): a string in the form of a url

    Returns:
        bool: True if it has a valid protocol
    """
    if url and url.startswith(('http://', 'https://', 'ftp://')):
        return True

    return False


def delete_file(file_name):
    """ Delete specified ``file_name``.

    Args:
        file_name (str): name of file to delete
    """
    try:
        os.remove(file_name)
    except:
        pass


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy.

    Args:
        x (dict): a dictionary
        y (dict): a dictionary

    Returns:
        merged dictionary
    """
    z = x.copy()
    z.update(y)
    return z


def create_random_string(size=6, chars=string.ascii_uppercase + string.digits):
    """Generate a random string.

    Args:
        size (int): defaults to 6 characters
        chars (list): ``list`` of characters to use

    Returns:
        a random genereated string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def get_files_in_dir(directory, file_extensions=None):
    """Get a list of all files in ``directory``.

    Args:
        directory (str): The directory to search.
        file_extensions: A list of file extensions to match, None means all.

    Returns:
        list: A list of all matching files.
    """
    matches = []

    for root, directories, filenames in os.walk(directory):
        for filename in filenames:
            if file_extensions:
                for ext in file_extensions:
                    if filename.lower().endswith(ext.lower()):
                        matches.append(os.path.join(root, filename))
            else:
                matches.append(os.path.join(root, filename))
        # for directory in directories:
        #    print(os.path.join(root, directory))

    return matches


def get_dirs_in_dir(directory):
    """Get a list of all directories in ``directory``.

    Args:
        directory (str): The directory to search.

    Returns:
        list: A list of all matching files.
    """
    matches = []

    for root, directories, filenames in os.walk(directory):
        for directory in directories:
            matches.append(os.path.join(root, directory))

    return matches

