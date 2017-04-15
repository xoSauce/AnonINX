import logging
import os

def log_init(filename='example.log'):
    log_dir= 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    filename = "%s/%s" % (log_dir, filename)
    logging.basicConfig(filename=filename,level=logging.DEBUG)
    log_info("--- Starting new logging session ---")

def log_debug(msg):
    logging.debug(msg)
def log_info(msg):
    logging.info(msg)
def log_warning(msg):
    logging.warn(msg)
