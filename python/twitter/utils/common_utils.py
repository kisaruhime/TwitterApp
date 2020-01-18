import os
import configparser

def get_users_names():
    user1 = os.environ['USER1']
    user2 = os.environ['USER2']
    return user1, user2


def get_resource_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(my_path, os.pardir))


def get_config():

    # config = configparser.ConfigParser()
    # print(config.sections())
    #
    # config.read('example.ini')
    config = configparser.ConfigParser()
    config.read(os.path.join(get_resource_path(), "resources\\config.ini"))
    return config

