"""
Module represents methods required for inputing and outputing data to console interface
"""

import click
import os

from task_manager_library.models.task_model import Status, Task, Priority


def print_tree(manager, tasks):
    click.clear()
    root_tasks = [task for task in tasks if task.parent is None]
    for task in root_tasks:
        marker = get_status_marker(task)
        click.echo(marker + " - " + task.tid + " - " + click.style(task.title, fg='yellow'))
        subtasks = manager.get_subtasks(task.tid)
        for subtask in subtasks:
            marker = get_status_marker(subtask)
            print(subtask.height*"\t" + marker + " - " + subtask.tid + " - " + click.style(subtask.title, fg='yellow'))
            print_sub(manager, subtask)


def print_sub(manager, _task):
    subtasks = manager.get_subtasks(_task.tid)
    for subtask in subtasks:
        marker = get_status_marker(subtask)
        print(subtask.height * "\t" + marker + " - " + subtask.tid + " - " + click.style(subtask.title, fg='yellow'))
        print_sub(manager, subtask)


def get_status_marker(task):
    """Printing list of tasks"""
    if task.is_completed == Status.done:
        marker = click.style('[X]', fg='green')
    elif task.is_completed == Status.undone:
        marker = click.style('[ ]', fg='red')
    else:
        marker = click.style('[O]', fg='blue')
    return marker


def split_str_to_list(splitter):
    """
    Split string separated by ',' and convert it to list
    """
    if splitter == "":
        return []

    splitter = splitter.split(",")
    return splitter


def format_print_ordered(ordered_tasks):
    """Showing full info of orderedn tasks"""

    for task in ordered_tasks:
        marker = ' '
        if task.is_completed == Status.done:
            marker = 'X'
        elif task.is_completed == Status.undone:
            marker = ' '
        elif task.is_completed == Status.process:
            marker = 'O'
        else:
            raise ValueError("Status is not status object")

        click.echo("[" + marker + "] - "
                   + click.style(str(task.title), bold=True, bg='yellow', fg='white'))


def print_notifications(notifications):
    """Ptint current notification"""
    click.secho("You have {} reminders for today:".format(len(notifications)),
                bg='yellow', bold=True, fg='white')
    for notify in notifications:
        click.secho(notify.title, bg='green', bold=True, fg='white')
