from console_lib import *
import task_manager_library
import os


@click.group(invoke_without_command=True)
def cli():
    click.clear()

# region User actions


@cli.command()
def current():
    try:
        current = task_manager_library.UserTools.get_current_user()
        click.echo("Login: {}".format(current.login))
        click.echo("Full name: {} {}".format(current.name, current.surname))
        click.echo("UID: {}".format(current.uid))
    except Exception as e:
        print(e)


@cli.command()
@click.option('--login', type=str, default=None,
              help='Unique login of new user')
@click.option('--name', type=str, default='UserName',
              help='Name of new user')
@click.option('--surname', type=str, default='UserName',
              help='surname of new user')
def add_user(login, name, surname):
    task_manager_library.UserTools.add_user(login, name, surname)


@cli.command()
@click.option('--login', type=str,
              help='Login to switch the users')
def change_user(login):
    """
    Set user as current
    :param login: str object
    :return:
    """
    task_manager_library.UserTools.change_user(login)

# endregion

# region Task actions

@cli.command()
@click.option('--task', is_flag=True,
              help='Опция для добавления задачи в трекер задач')
@click.option('--subtask', type=int,
              help='Опция для добавления подзадачи')
@click.option('--plan', is_flag=True,
              help='Задать конфигурацию планировщика')
@click.option('-sd', type=str, callback=task_manager_library.check_date,
              help='Начало')
@click.option('-ed', type=str, callback=task_manager_library.check_date,
              help='Конец')
@click.option('-tg', type=str,
              help='Тег')
@click.option('-de', type=str,
              help='Описание')
@click.option('-ti', type=str,
              help='Название')
@click.option('-re', type=str, callback=task_manager_library.check_time,
              help='Название')
@click.option('-ob', type=str,
              help='Наблюдатели')
@click.option('-pr', type=str,
              help='Приоритет')
def add(task, subtask, plan, sd, ed, tg, de, ti, re, ob, pr):
    if task:
        Console.add_task(sd, ed, tg, de, ti, re, ob, pr)
    elif subtask:
        Console.add_subtask(current_user, all_tasks, all_users_tasks, tracked_tasks, users, subtask,
                                       sd, ed, tg, de, ti, re, ob, pr)
    elif plan:
        Console.add_scheduler()


@cli.command()
@click.option('--task', is_flag=True,
              help='Опция для просмотра задач')
def list(task):

    if task:
        import task_manager_library
        task_gen = task_manager_library.show_tracked_task()
        for task in task_gen:
            click.echo("[" + task[0] + "] - " + task[1] + " - " + click.style(
                "Subtasks: " + task[2], bold=True, fg='yellow')
                + " - " + click.style(task[3], bold=True, bg='green'))


@cli.command()
@click.option('--task', type=int,
              help='Опция для выполнения задачи')
@click.option('--subtask', type=int,
              help='Опция для выполнения подзадачи')
def done(task, subtask):
    global simple_tasks, tracked_tasks, calendar_events, all_users_tasks, all_tasks
    try:
        if task:
            import task_manager_library
            task_manager_library.done_task(task)

        elif subtask:
            Console.done_subtask(subtask, all_tasks, tracked_tasks, all_users_tasks)

    except Exception as e:
        print(e)
        logging.warning("Troubles while trying to done task")


@cli.command()
@click.option('--task', type=int,
              help='Опция для просмотра задач')
@click.option('--event', type=int,
              help='Опция для просмотра события в календаре')
def info(task, event):
    global simple_tasks, tracked_tasks, calendar_events
    if task:
        pass
    elif event:
        pass


@cli.command()
@click.option('--task', type=(int, str),
              help='Опция для редактирования задач')

def edit(task):
    global simple_tasks, tracked_tasks, calendar_events, all_users_tasksm, current_user
    try:
        if task:
            task_num = task[0]
            task_field = task[1]
            import task_manager_library
            task_manager_library.edit_task(task_num, task_field)
            #Console.edit_task(current_user, task_num, task_field, all_users_tasks, tracked_tasks, all_tasks)

    except ValueError as e:
        print(e)


@cli.command()
@click.option('--tag', type = str)
@click.option('--value', type=click.Choice(['high', 'medium', 'low']))
def showtools(tag, value):
    """
    Форматированный вывод по заданным критериям
    """
    global tracked_tasks, users
    if tag:
        Console.show_by_tag(tag, tracked_tasks)
    elif value:
        priority = task_manager_library.Priority[value]
        Console.show_by_priority(priority, tracked_tasks, users)


@cli.command()
@click.option('--level', type=str,
              help='Выбрать уровень логгирования')
@click.option('--file', type=str,
              help='Указать файл с логгированием')
@click.option('--format', type=str,
              help='Формат логгирования')
def logging(level, file, format):
    Console.set_logger(level, format, file)

@cli.command()
@click.option('--week', is_flag=True,
              help='Опция для просмотра задач')
@click.option('--month', is_flag=True,
              help='Опция для просмотра todo')
def cal(week, month):
    """Работа с календарем"""
    global simple_tasks, tracked_tasks, calendar_events
    if week:
        Console.show_week(calendar_events)
    elif month:
        pass

# endregion


if __name__ == '__main__':
    cli()
