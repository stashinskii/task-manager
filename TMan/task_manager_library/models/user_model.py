"""
This module represents User class which is used for manage division of tasks between users in CLI app


"""
import uuid

class User:

    def __init__(self, login, name, surname, uid=None, tasks=None):
        self.name = name
        self.surname = surname
        if uid is None:
            self.uid = str(uuid.uuid1())
        else:
            self.uid = uid
        self.login = login
        if tasks is None:
            self.tasks = list()
        else:
            self.tasks = tasks







