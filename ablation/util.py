import json
import logging
import os

from pkg_resources import resource_string


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

    DIRNAME = os.path.dirname(__file__)
    config_file = json.loads(resource_string(__name__, './config.json'))

    index_path = os.path.join(DIRNAME, config_file['coco_classes_index'])
    distil_index_path = os.path.join(DIRNAME, config_file['coco_classes_index_distil'])
    distil_model_path = os.path.join(DIRNAME, config_file['fasttext_model_distil'])


    if os.path.exists(index_path):
        config_file['coco_classes_index'] = index_path
        config_file['coco_classes_index_distil'] = distil_index_path
        config_file['fasttext_model_distil'] = distil_model_path

        return config_file
