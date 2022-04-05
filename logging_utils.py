import logging
from pythonjsonlogger import jsonlogger

def get_logger_and_logFormatter():
    LOG = logging.getLogger()
    formatter = jsonlogger.JsonFormatter()
    return LOG, formatter

def setup_log_stream_handler(logger, formatter):
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

def setup_log_file_handler(filename, logger, formatter):
    fileHandler = logging.FileHandler(filename)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)