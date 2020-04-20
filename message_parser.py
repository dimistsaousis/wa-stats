from __future__ import annotations
import re

from dataclasses import dataclass
from datetime import datetime


ACTIONS = [
    "created group",
    "added",
    "changed the subject to",
    "changed this group's icon",
    "removed",
    "changed their phone number to a new number",
    "left",
]


@dataclass
class Message:
    timestamp: datetime
    user: str
    message: str
    auto: bool


def split_line_to_date_and_body(line: str):
    datestr, body = re.match(r'^\[(.*?)\] (.*?)$', line.replace('\u200e', '')).groups()
    return datetime.strptime(datestr, '%d/%m/%Y, %H:%M:%S'), body


def split_body_to_user_and_message(body: str):
    if ':' in body:
        user, message = re.match(r'^(.*?): (.*?)$', body).groups()
        return user.strip(), message
    else:
        for action in ACTIONS:
            idx = body.find(action)
            if idx > 0:
                return body[:idx].strip(), body[idx:]
    return None


def get_message(line: str):
    date, body = split_line_to_date_and_body(line)
    user, message = split_body_to_user_and_message(body)
    return Message(date, user, message, '\u200e' in line)


def is_new_message(line: str):
    try:
        split_line_to_date_and_body(line)
        return True
    except Exception:
        return False


def iterlines(filepath, rows=None):
    with open(filepath, mode='r') as f:
        count = 1
        line = f.readline()
        while line:
            yield line
            if rows and count > rows:
                break
            line = f.readline()
            count += 1


def itermessages(filepath, rows=None):
    message = None
    for line in iterlines(filepath, rows):
        if is_new_message(line):
            if message is None:
                message = get_message(line)
            else:
                yield message
                message = get_message(line)
        else:
            if message is None:
                raise ValueError('Invalid start of data.')
            else:
                message.message += line
