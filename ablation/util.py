import json
import logging

def get_logger(logger_name):

    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def load_config():

    with open("./config.json") as fp:
        return json.load(fp)
