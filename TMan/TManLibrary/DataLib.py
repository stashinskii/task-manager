from .TaskLib import *
from .LoggingConfig import *
import logging
import json
import uuid
import os
from datetime import datetime


#при отсутствии такой директории - создаем её
data_dir = os.environ['HOME']+'/tmandata'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


# задаем конфигурацию логгирования
format_info, file_info = loggingConfig.get_logging_config(logging.INFO)
logging.basicConfig(filename=file_info, level=logging.INFO,
                    format=format_info)
print(file_info)
format_warning, file_warning = loggingConfig.get_logging_config(logging.WARNING)
logging.basicConfig(filename=file_warning, level=logging.WARNING,
                    format=format_warning)


def tid_gen():
    """Генерирует task id"""
    return str(uuid.uuid1())


def check_date(ctx, date):
    """
    Проверка даты
    :param ctx: параметр, для
    :param date:
    :return:
    """
    time_format_one = "%Y-%m-%d"
    if (date is None):
        raise ValueError

    try:
        date = datetime.strptime(date, time_format_one)
    except ValueError:
        date = datetime.now()
    return date


def check_time(ctx, mytime):

    time_format = "%H:%M"
    mytime = datetime.strptime(mytime, time_format)
    return mytime


def data_from_json(type, current):
    """Загрузка задач из файла"""
    tracked_tasks = []
    users = []
    all_tasks = []
    all_users_tasks = []
    files = ['/trackedtasks.json', '/users.json']
    for file in files:
        if not os.path.isfile(data_dir+file):
            f = open(data_dir+file, "w+")
            f.write('[]')
            f.close()

    try:
        if type=="Task":
            with open(data_dir+'/trackedtasks.json', 'r') as task_file:
                task_data = json.load(task_file)

            for task_dict in task_data:
                title = task_dict['title']
                start = check_date(None, task_dict['start'])
                end = check_date(None, task_dict['end'])
                description = task_dict['description']
                tag = task_dict['tag']
                observers = task_dict['observers']
                executor = task_dict['executor']
                priority = Priority[Priority(int(task_dict['priority'])).name]
                author = task_dict['author']
                reminder = check_time(None, task_dict['reminder'])
                is_completed = task_dict['is_completed']
                parent = task_dict['parent']
                tid = task_dict['tid']
                subtasks = task_dict['subtasks']
                planned = task_dict['planned']
                changed = task_dict['changed']

                new_task = TrackedTask(
                        tid,
                        title,
                        description,
                        start,
                        end,
                        tag,
                        author,
                        observers,
                        executor,
                        is_completed,
                        reminder,
                        priority,
                        parent,
                        subtasks,
                        changed,
                        planned
                    )
                if task_dict['parent'] is None:
                    if task_dict['tid'] in current.tasks['task']:
                        tracked_tasks.append(new_task)
                        all_tasks.append(new_task)
                    all_users_tasks.append(new_task)
                else:
                    all_tasks.append(new_task)
                    all_users_tasks.append(new_task)
            return tracked_tasks, all_tasks, all_users_tasks

        elif type == "User":
            with open(data_dir+'/users.json', 'r') as file:
                data = json.load(file)

            for data_dict in data:
                name = data_dict['name']
                surname = data_dict['surname']
                login = data_dict['login']
                uid = data_dict['uid']
                tasks = data_dict['tasks']
                current = data_dict['current']
                user = User(name, surname, uid, tasks, login, current)
                users.append(user)
            return users


    except FileNotFoundError:
        logging.warning("File not exist")
        return []


def data_to_json(collect, object):
    """
    Сохраняем состояние коллекции файле. В качестве аргумента передаем готовый слоаврь объекта
    В зависимости от типа передаваемого объекта, выбираем конкретные файлы для загрузки
    """
    files = [data_dir+'/trackedtasks.json', data_dir+'/users.json']
    if object.__class__.__name__ == 'TrackedTask':
        filename = files[0]
    elif object.__class__.__name__ == 'User':
        filename = files[1]
    else:
        raise Exception("Unknown type of object")

    object = object.__dict__

    try:
        with open(filename, 'r') as objfile:
            collection = json.load(objfile)

    except FileNotFoundError:
        collection = []
        logging.warning("Can't load json file")
    collection.append(object)

    with open(filename, 'w') as objfile:
        json.dump(collection, objfile, indent=2, ensure_ascii=False)

    return collection


# Далее работа с Трекером дел
def add_tracked_task(all_tasks, tid, title, description, start, end, tag,
                    author,observers, executor, is_completed,
                    reminder, priority, users, current, parent, subtasks, changed, planned):
    from TManLibrary import Sync
    if observers != "":
        observers = observers.split(",")
    else:
        observers = []
    if start > end:
        raise ValueError("ERROR! Start date GT end date")
    all_tasks.append(TrackedTask(
        tid,
        title,
        description,
        str(start.year)+"-"+str(start.month)+"-"+str(start.day),
        str(end.year) + "-" + str(end.month) + "-" + str(end.day),
        tag,
        author,
        observers,
        executor,
        is_completed,
        str(reminder.hour) +":"+str(reminder.minute),
        priority,
        parent,
        subtasks,
        changed,
        planned
    ))
    resave_tracked_json(all_tasks)
    from TManLibrary import UserLib
    #data_to_json(all_tasks, all_tasks[-1])
    add_user_task(users, current, tid, "Task")
    for us in observers:
        if us!=current.login:
            user = UserLib.get_user(us, users)
            add_user_task(users, user, tid, "Task")


def resave_tracked_json(tracked_tasks):
    """Пересохранение данных после изменения"""
    data = []
    for task in tracked_tasks:
        if isinstance(task.start, datetime):
            task.start = str(task.start.year)+"-"+str(task.start.month)+"-"+str(task.start.day)
        if isinstance(task.end, datetime):
            task.end = str(task.end.year) + "-" + str(task.end.month) + "-" + str(task.end.day)
        if isinstance(task.reminder, datetime):
            task.reminder = str(task.reminder.hour) +":"+str(task.reminder.minute)
        if isinstance(task.priority, Priority):
            task.priority = str(task.priority.value)
        data.append(task.__dict__)

    with open(data_dir+'/trackedtasks.json', 'w') as taskfile:
        json.dump(data, taskfile, indent=2, ensure_ascii=False)


def show_tracked_task(tracked_tasks, all_tasks):
    """Вывод всех заданий с отметкой о статусе выполения и номером"""
    try:
        if tracked_tasks is None:
            raise TypeError("Task collection is not list")
        for task in tracked_tasks:
            subtasks = []
            for subtask in all_tasks:
                if subtask.parent == task.tid:
                    subtasks.append(subtask.tid)

            if task.is_completed:
                marker = "X"
            else:
                marker = " "
            # Возвращаем строку со списком задач и их состоянием
            yield (marker, str(tracked_tasks.index(task)+1),str(len(subtasks)), str(task.title))
    except TypeError as e:
        logging.warning('Unable to show tasks')


def str_to_uuid(str_id):
    """UUID строку в UUID"""
    return uuid.UUID(str_id)


def uuid_to_datetime(uuid_id):
    """UUID в объект datetime"""
    return datetime.fromtimestamp((uuid_id.time - 0x01b21dd213814000)*100/1e9)
