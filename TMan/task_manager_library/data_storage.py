"""
This module represents DataStorage class which is contains methods to manage tasks, schedulers,
users and store them in their json files.

To use DataStorage, primarily user need to set up PATH and CURRENT_USER for current work of application.

All methods in DataStorage are static

All methods describes logic of resaving and loading files from JSON
"""
import json
import os
from datetime import datetime
import configparser

from task_manager_library import utils, serialization_utils
from task_manager_library.models.task_model import Tag, Priority
from task_manager_library.models.user_model import User


class Storage:
    def __init__(self, configuration=None, external_user=None):
        if configuration is not None and configuration.get('storage_path') is not None:
            self.path = configuration.get('storage_path')
        else:
            self.path = os.path.dirname(__file__) + "/tmandata/"
        if external_user is not None:
            self.current_uid = external_user
        else:
            try:
                utils.check_files(self.path, '/users.json')
                utils.check_files(self.path, '/current.ini')
                config = configparser.ConfigParser()
                config.read(self.path+'current.ini')
                section = "USER"
                uid = config.get(section, "uid")
                self.current_uid = uid
            except Exception as e:
                self.current_uid = None
        self.tasks = []
        self.user_tasks = []

    # region Loading data

    def load_users_from_json(self):
        utils.check_files(self.path, '/users.json')
        with open(self.path + '/users.json', 'r') as file:
            data = json.load(file)
        users = list()

        for data_dict in data:
            user = serialization_utils.dict_to_user(data_dict)
            users.append(user)
        return users

    def load_user(self, uid):
        users = self.load_users_from_json()
        for user in users:
            if user.uid == uid:
                return user

    def chage_user_config(self, login):
        users = self.load_users_from_json()
        user_uid = next((user.uid for user in users if user.login == login), None)
        config = configparser.ConfigParser()
        section = "USER"
        config.read(self.path+'/current.ini')
        exist = config.has_section(section)
        if not exist:
            config.add_section(section)
        config.set(section, 'uid', user_uid)

        with open(self.path+'/current.ini', 'w+') as f:
            config.write(f)

    def load_tasks_from_json(self):
        utils.check_files(self.path, '/tasks.json')

        if self.tasks:
            return

        with open(self.path + 'tasks.json', 'r') as task_file:
            task_data = json.load(task_file)

        for task_dict in task_data:
            loaded_task = serialization_utils.dict_to_task(task_dict)
            self.tasks.append(loaded_task)

    def load_user_tasks(self):
        if not self.user_tasks:
            self.load_tasks_from_json()

        if self.user_tasks:
            return

        current_user = self.load_user(self.current_uid)
        for task in self.tasks:
            if task.tid in current_user.tasks:
                self.user_tasks.append(task)
    # endregion

    # region Tasks actions
    def add_task(self, task):
        self.load_tasks_from_json()
        self.tasks.append(task)
        self.write_tid_to_user(task.tid, self.current_uid)
        if task.observers:
            self.give_task_permission(task.observers, task.tid)
        self.resave()

    def resave(self):
        data = []
        for task in self.tasks:
            task = serialization_utils.task_to_dict(task)
            data.append(task.__dict__)

        with open(self.path + '/tasks.json', 'w') as taskfile:
            json.dump(data, taskfile, indent=2, ensure_ascii=False)

    def delete(self, tid):
        self.load_tasks_from_json()
        if len(self.tasks) == 0:
            raise IndexError("Nothing to delete")
        index = utils.get_task_index(tid, self)
        del self.tasks[index]
        self.resave()

    def edit(self, tid, **kwargs):
        self.load_tasks_from_json()
        index = utils.get_task_index(tid, self)

        title = kwargs.get('title')
        if title is not None:
            self.tasks[index].title = title

        description = kwargs.get('description')
        if description is not None:
            self.tasks[index].description = description

        priority = kwargs.get('priority')
        if priority is not None:
            self.tasks[index].priority = Priority[priority]

        tag = kwargs.get('tag')
        if priority is not None:
            self.tasks[index].tag = Tag[tag]

        end = kwargs.get('end')
        if end is not None:
            self.tasks[index].end = utils.str_to_date(end)

        self.resave()

    def link(self, first_id, second_id):
        first_index = utils.get_task_index(first_id, self)
        second_index = utils.get_task_index(second_id, self)

        self.tasks[first_index].connection.append(second_id)
        self.tasks[second_index].connection.append(first_id)

        self.resave()

    def give_task_permission(self, observers, tid):
        for observer in observers:
            if observer != self.current_uid:
                self.write_tid_to_user(tid, observer)

    def write_tid_to_user(self, tid, uid):
        users = self.load_users_from_json()
        current_user = self.load_user(self.current_uid)

        index = utils.get_user_index(uid, users)
        del users[index]

        current_user.tasks.append(tid)
        users.append(current_user)

        users = [user.__dict__ for user in users]

        with open(self.path + '/users.json', 'w') as userfile:
            json.dump(users, userfile, indent=2, ensure_ascii=False)

    # endregion

    # region Changing status
    def complete_task(self, tid):
        self.load_tasks_from_json()
        index = utils.get_task_index(tid, self)
        self.tasks[index].complete()
        self.resave()

    def uncomplete_task(self, tid):
        self.load_tasks_from_json()
        index = utils.get_task_index(tid, self)
        self.tasks[index].uncomplete()
        self.resave()

    def begin_task(self, tid):
        self.load_tasks_from_json()
        index = utils.get_task_index(tid, self)
        self.tasks[index].begin()
        self.resave()

    # endregion

    # region User actions

    def save_new_user_to_json(self, user):
        users = self.load_users_from_json()
        users.append(user)
        self.resave_users(users)

    def resave_users(self, users):
        users = [user.__dict__ for user in users]
        with open(self.path + '/users.json', 'w') as taskfile:
            json.dump(users, taskfile, indent=2, ensure_ascii=False)

    # enregion

    # region Notifications actions
    pass
    # endregion

    # region Scheduler actions
    pass
    # endregion

