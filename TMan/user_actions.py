import configparser
import json
import logging
import os
import uuid

from utility import logging_utils
from utility import serialization_utils
from utility import utils
from task_manager_library.data_storage import DataStorage
from user import User


class UserTools():
    PATH = None
    """
    UserTools class is used to manage users
    """

    @staticmethod
    def validate_login(login):
        """
        :param login:
        :return: if False then login was used before
        """
        #TODO DO GLOBAL PATH_USERS, PATH_TASKS
        if not os.path.exists(DataStorage.PATH+'/users.json'):
            return True
        users = DataStorage.load_users_from_json()
        for user in users:
            if user.login == login:
                return False
        return True

    @staticmethod
    def set_current():
        users = DataStorage.load_users_from_json()
        for user in users:
            if user.current:
                return user
        raise Exception("There is no current user")


    @staticmethod
    def add_user(login, name, surname, tasks=None):
        if not UserTools.validate_login(login):
            raise ValueError("Current user exist!")
        uid = serialization_utils.tid_gen()
        new_user = User(name, surname, uid, login, False, tasks)
        users = DataStorage.save_users_to_json(new_user.__dict__)
        return users


    @staticmethod
    def get_current_user():
        config = configparser.ConfigParser()
        if UserTools.PATH is None:
            raise TypeError("You didn't set UserTools PATH's value")
        if not os.path.exists(UserTools.PATH):
            raise ValueError("There were no Signed Up users before. Please, Sign Up")
        config.read(UserTools.PATH)
        section = "USER"
        login = config.get(section, "current")
        users = DataStorage.load_users_from_json()
        return utils.get_user(login, users)

    @staticmethod
    def set_current_user(login):
        # if login doesn't exit then user was not sign up
        if UserTools.validate_login(login):
            raise Exception("Check login. User doesn't exist")

        config = configparser.ConfigParser()
        section = "USER"
        if not os.path.exists(UserTools.PATH):
            config.read(UserTools.PATH)

        exist = config.has_section(section)
        if not exist:
            config.add_section(section)
        config.set(section, 'current', login)

        with open(UserTools.PATH, 'w+') as f:
            config.write(f)

        return True








