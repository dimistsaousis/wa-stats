import pandas as pd
import re
import calendar
import enum

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


class Media(enum.Enum):
    "A message can contain one of the following"

    IMAGE = 'image'
    VIDEO = 'video'
    CONTACT_CARD = 'contact_card'
    GIF = 'gif'
    AUDIO = 'audio'
    DOCUMENT = 'document'
    TEXT = 'text'
    LAUGH = 'laugh'


class Action(enum.Enum):
    "Actions that a user can perform"
    CREATE_GROUP = 'created_group'
    ADD_USER = 'add_user'
    CHANGED_GROUP_ICON = 'changed_group_icon'
    CHANGED_SUBJECT = 'changed_subject'
    LEFT = 'left'
    REMOVED_USER = 'removed_user'
    MESSAGE = 'message'
    CHANGED_NUMBER = 'changed_number'


@dataclass
class Message:
    datetime: datetime
    user: str
    value: Optional[str] = None
    action: Optional[Action] = None
    media: Optional[Media] = None


def get_date_and_residual(line):
    match = re.match(r'\u200e?\[(.*?)\] (.*?)$', line)
    date = None
    if match:
        date_str, residual = match.groups()
        date = get_date(date_str)
        if date:
            return date, residual
        else:
            return None, line
    return None, line


def get_date(date):
    try:
        return datetime.strptime(date, '%d/%m/%Y, %H:%M:%S')
    except ValueError:
        return None


def is_laugh(txt):
    if '🤣' in txt or '😂' in txt:
        return True
    match = re.match(r'\b(?:a*(?:ha)+h?|(?:l+o+)+l+)\b', txt, re.I)
    return bool(match)


def get_user_value_and_action(line):
    match = re.match(r'(.*?)\: \u200e?(.*?)$', line)
    if match:
        user, value = match.groups()
        return user, value, Action.MESSAGE

    match = re.match(r'^\u200e?(.*?) created group (.*?)$', line)
    if match:
        user, value = match.groups()
        return user, value, Action.CREATE_GROUP

    match = re.match(r'^\u200e?(.*?) add_user (.*?)$', line)
    if match:
        user, value = match.groups()
        return user, value, Action.ADD_USER

    match = re.match(r"^\u200e?(.*?) changed this group's icon$", line)
    if match:
        user, = match.groups()
        return user, None, Action.CHANGED_GROUP_ICON

    match = re.match(r'^\u200e?(.*?) changed the subject to (.*?)$', line)
    if match:
        user, value = match.groups()
        return user, value, Action.CHANGED_SUBJECT

    match = re.match(r'^\u200e?(.*?) left$', line)
    if match:
        user, = match.groups()
        return user, None, Action.LEFT

    match = re.match(r'^\u200e?(.*?) removed_user (.*?)$', line)
    if match:
        user, value = match.groups()
        return user, value, Action.REMOVED_USER

    match = re.match(r'^\u200e?\u200e?(.*?) changed their phone number to a new number', line)
    if match:
        user, = match.groups()
        return user, None, Action.CHANGED_NUMBER

    return None, line, None


def get_media(value):
    for media in Media:
        if media.value + ' omitted' in value.lower():
            return media
    if is_laugh(value):
        return Media.LAUGH
    return Media.TEXT


def get_message(line):
    date, residual = get_date_and_residual(line)
    if date:
        user, value, action = get_user_value_and_action(residual)
        media = None if action != Action.MESSAGE else get_media(value)
        return Message(date, user, value, action, media)
    return None


def iterfile(filepath, rows=None):
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
    for line in iterfile(filepath, rows):
        if message is None:
            message = get_message(line)
        else:
            new_message = get_message(line)
            if new_message is None:
                message.value += line
            else:
                yield message
                message = new_message


def add_action_counts(df):
    for action in Action:
        df[action.value + '_count'] = df['action'].map(lambda x: 1 if x == action else 0)


def add_media_counts(df):
    for media in Media:
        df[media.value + '_count'] = df['media'].map(lambda x: 1 if x == media else 0)


def add_counts(df):
    add_action_counts(df)
    add_media_counts(df)


def map_users(df):
    USERS = {
        'You': 'Dimis T.',
        'La Révolution Capitale': None,
        'Andreas': 'Andreas N.',
        'Mitsakos': 'Dimitris M.',
        'Alexis Pipilis': 'Alexis P.',
        'Goun': 'Kostantinos G.',
        'dimis': 'Dimis T.',
        '+44 7557 515264': 'Dimis T.',
        'Valentini Karadimou': 'Valentini K.',
        'Pxiom': 'John P.',
        'Nikos Nikolaou': 'Nikos N.',
        'Bro': 'Nikos T.',
        'Nikolaou': 'Nikos N.',
        'Skasis': 'Antonis S.',
    }
    df.user = df.user.map(USERS.get)


def add_date_attributes(df):
    df['date'] = df['datetime'].map(lambda dt: dt.date())
    df['year'] = df['datetime'].dt.year
    df['quarter'] = df['datetime'].dt.quarter
    df['month'] = df['datetime'].dt.month
    df['month_name'] = df['month'].map(lambda month: calendar.month_name[month])
    df['day'] = df['datetime'].dt.day
    df['week'] = df['datetime'].dt.week
    df['weekday'] = df['datetime'].dt.weekday
    df['day_name'] = df['weekday'].map(lambda weekday: calendar.day_name[weekday])
    df['time'] = df['datetime'].map(lambda dt: dt.time())
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute


def add_message_attributes(df):
    df['message_char_count'] = df.apply(
        lambda x: 0 if x['action'] != Action.MESSAGE else len(x['value']), axis=1
    )
    df['message_word_count'] = df.apply(
        lambda x: 0 if x['action'] != Action.MESSAGE else len(x['value'].split(' ')), axis=1
    )


def enhance(raw):
    df = raw.copy()
    map_users(df)
    add_counts(df)
    add_date_attributes(df)
    add_message_attributes(df)
    return df


def get_raw_data(filepath, rows=None):
    df = pd.DataFrame(data=[asdict(msg) for msg in itermessages(filepath, rows)])
    return df.sort_values('datetime').reset_index(drop=True)


if __name__ == '__main__':
    filepath = '_chat.txt'
    raw = get_raw_data(filepath)
    df = enhance(raw)

    daily_message_count = df.groupby('date')['message_count'].sum().reset_index()
    daily_message_count['cumsum'] = daily_message_count['message_count'].cumsum()

    daily_user_message_count = (
        df.groupby(['date', 'user'])['message_count'].sum().reset_index()
    )
    daily_user_message_count['cumsum'] = daily_user_message_count.groupby('user')[
        'message_count'
    ].cumsum()

    user_stats = (
        df.groupby('user')[[media.value + '_count' for media in Media]]
        .sum()
        .rename(columns={media.value + '_count': media.value for media in Media})
    ).T
    user_stats['Total'] = user_stats.sum(axis=1)
    user_stats = user_stats.T
