import click
import logging
import TManLibrary


class Console:
    """Класс для организации работы с терминалом."""

    @staticmethod
    def create_new_user(users):
        login = input("Login: ")
        if (TManLibrary.validate_login(users, login)):
            name = input("Name: ")
            surname = input("Surname: ")
            TManLibrary.add_user(users, name, surname, login, {"simple": [], "task": [], "event": []})

    @staticmethod
    def import_users():
        return TManLibrary.data_from_json("User", None)

    @staticmethod
    def set_current(users, chuser):
        return TManLibrary.change_user(users, chuser)

    @staticmethod
    def show_current(users):
        current_user = TManLibrary.set_current(users)
        print("login: {}\nUID: {}".format(current_user.login, current_user.uid))

    @staticmethod
    def import_all_data(users):
        current_user = TManLibrary.set_current(users)
        simple_tasks = TManLibrary.data_from_json("TODO", current_user)
        tracked_tasks = TManLibrary.data_from_json("Task", current_user)
        return (current_user, simple_tasks, tracked_tasks)

    @staticmethod
    def add_task(current_user, tracked_tasks):
        """
        Добавление новой задачи трекера. Возвращает измененную коллекцию с новым элементом
        """
        try:
            if current_user is None:
                raise Exception("There is no current user. Choose")
            title = input("Input title: ")
            start = input("Choose start date: ")
            end = input("Choose end date: ")
            description = input("Add some info about task: ")
            dash = input("Choose dashboard: ")
            tag = input("Add #tag to this task: ")
            observers = None  # TODO здесь указать объект пользователя в системе или его uid
            executor = None  # TODO здесь указать объект пользователя в системе или его uid
            priority = input("Choose priority: ")
            author = current_user.uid
            reminder = input("Reminder: ")
            tid = TManLibrary.tid_gen()
            return TManLibrary.add_tracked_task(
                tracked_tasks, tid, title, description, start,
                end, tag, dash, author, observers, executor, True, False, reminder, priority, [])
        except ValueError:
            logging.warning("ValueError: some troubles while adding task")

    @staticmethod
    def add_subtask(current_user, tracked_tasks, subtask):

        """subtask -  параметр Click, номер подзадачи"""

        title = input("Input title: ")
        start = input("Choose start date: ")
        end = input("Choose end date: ")
        description = input("Add some info about task: ")
        dash = input("Choose dashboard: ")
        tag = input("Add #tag to this task: ")
        observers = None  # TODO здесь указать объект пользователя в системе или его uid
        executor = None  # TODO здесь указать объект пользователя в системе или его uid
        priority = input("Choose priority: ")
        author = current_user.uid
        reminder = input("Reminder: ")
        return TManLibrary.add_subtask(tracked_tasks, subtask, title, description, start,
                                                end, tag, dash, author, observers, executor, True, False, reminder,
                                                priority)

    @staticmethod
    def add_simple_task(users, current_user, simple_tasks):
        try:
            title = input("Input title: ")
            date = input("Choose date (YYYY-MM-DD): ")
            #year, month, day = map(int, date.split('-'))
            #date = datetime.date(year, month, day)
            description = input("Add some info about task: ")
            priority = input("Choose priority: ")
            tag = input("Add #tag to this task: ")
            tid = TManLibrary.tid_gen()
            permission = None
            is_completed = False
            return TManLibrary.add_simple_task(users, current_user, simple_tasks, title, date,
                                                   description, priority, tid, permission, is_completed, tag)
        except TypeError as e:
            logging.warning("Trouble while input data at todo")
            print("Trouble while input data at todo")
        except Exception as e:
            print(e)

    @staticmethod
    def list_todo(simple_tasks):
        task_gen = TManLibrary.show_simple_task(simple_tasks)
        for task in task_gen:
            print(task)

    @staticmethod
    def list_task(tracked_tasks):
        task_gen = TManLibrary.show_tracked_task(tracked_tasks)
        for task in task_gen:
            click.echo("[" + task[0] + "] - " + task[1] + " - " + click.style(
                "Subtasks: " + task[2], bold=True, fg='yellow') + " - " + click.style(task[3], bold=True, bg='green'))

    @staticmethod
    def done_todo(todo, simple_tasks):
        try:
            if (todo - 1) > len(simple_tasks):
                raise IndexError("Выход за границы списка")
            simple_tasks = TManLibrary.complete_simple_task(simple_tasks, todo)
        except IndexError as e:
            logging.warning("Out of range")
            print(e)

    @staticmethod
    def delete_todo(todo, simple_tasks):
        try:
            if (todo - 1) > len(simple_tasks):
                raise IndexError
            simple_tasks = TManLibrary.delete_simple_task(simple_tasks, todo)
        except IndexError as e:
            logging.warning("Out of range while deleting. Index was: {}".format(todo))
            print(e)
        except Exception as e:
            print(e)
            logging.warning("Something done wrong while deleting. Index was: {}".format(todo))

    @staticmethod
    def info_todo(todo, simple_tasks):
        try:
            if (todo - 1) > len(simple_tasks):
                raise IndexError("Такой задачи не существует. Выход за границы списка")
            selected_task = TManLibrary.show_simple_info(simple_tasks, todo)
            click.echo(click.style("TODO Task description: \t\t\t", bold=True, blink=True, bg='green'))
            click.echo("Title: "+click.style(str('\t\t' + selected_task.title), fg='white', bold=True))
            click.echo("Description: " + click.style(str('\t' + selected_task.description), fg='yellow'))
            click.echo("Date: " + click.style(str('\t\t' + selected_task.date), fg='yellow'))
            click.echo("Tag: " + click.style(str('\t\t' + selected_task.tag), fg='yellow'))
            click.echo("Is completed: " + click.style('\t' + str(selected_task.is_completed), fg='yellow'))
        except IndexError as e:
            logging.warning("Out of range while showing todo task info. Index was: {}".format(todo))
            print(e)