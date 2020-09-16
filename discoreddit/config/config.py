"""
Project-wide configuration variables.

.. note::
    This configuration architecture is ugly and might be changed in the Future
    for a leaner one.
"""

import os
import importlib
import logging

MAX_TRIES = 4
MAX_MEDIA_SIZE = 20000000
MAX_POST_LENGTH = 500
MAX_TITLE_LENGTH = 200
REDDIT_DOMAINS = ["reddit.com", "redd.it", "reddit.app.link"]