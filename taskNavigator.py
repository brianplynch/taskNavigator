#!/usr/bin/env python3
"""
Task Navigator: A tool for managing and navigating tasks and their artifacts.
"""

import logging
from configparser import ConfigParser
from ux.markdownTaskNavigatorUI import MainApplication, WindowGeometry
from pathlib import Path


# Configure the application
configurable_attributes = ConfigParser()
configurable_attributes.read('taskNavConfig.ini')

vault: str = configurable_attributes['general']['vault']
top_level_filename: str = configurable_attributes['general']['top_level_filename']
installation_path: str = configurable_attributes['general']['installation_path']
window_width: int = int(configurable_attributes['general']['window_width'])
window_height: int = int(configurable_attributes['general']['window_height'])
debug_on: int = int(configurable_attributes['general'].getboolean('debug'))
logging_level = [logging.INFO, logging.DEBUG][debug_on]


# Configure the logger
_log_path = Path(__file__).parent.joinpath('_error_messages.log')

logging.basicConfig(
    force=True,
    level=logging.DEBUG, #logging_level, # Minimum level of messages to log
    format='%(asctime)s - %(levelname)s - %(message)s', # Format of log messages
    filename=_log_path, # File to write log messages to
    filemode='w' # Mode to open the log file ('w' to overwrite, 'a' to append)
)

my_app = MainApplication(
    vault = vault,
    top_level_file = top_level_filename,
    installation_path = Path(installation_path),
    window_geometry = WindowGeometry(window_width, window_height)
)

my_app.start()
