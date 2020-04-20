from message_parser import Message
from functools import wraps
import re


def feature(fn):
    fn.__name__ = '__feature__' + fn.__name__
    return fn


@feature
def laugh_count(msg: Message):
    if '🤣' in msg.message or '😂' in msg.message:
        return 1
    elif re.match(r'\b(?:a*(?:ha)+h?|(?:l+o+)+l+)\b', msg.message, re.I):
        return 1
    return 0


@feature
def username(msg: Message):
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
    return USERS.get(msg.user, msg.user)


@feature
def picture_count(msg: Message):
    if 'picture omitted' in msg and msg.auto:
        return 1
    return 0


@feature
def video_count(msg: Message):
    if 'video omitted' in msg and msg.auto:
        return 1
    return 0


@feature
def audio_count(msg: Message):
    if 'audio omitted' in msg and msg.auto:
        return 1
    return 0


@feature
def document_count(msg: Message):
    if 'document omitted' in msg and msg.auto:
        return 1
    return 0


@feature
def gif_count(msg: Message):
    if 'GIF omitted' in msg and msg.auto:
        return 1
    return 0


@feature
def contact_card_count(msg: Message):
    if 'Contact card omitted' in msg and msg.auto:
        return 1
    return 0
