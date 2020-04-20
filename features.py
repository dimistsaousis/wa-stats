import re


def feature(fn):
    fn.__name__ = '__feature__' + fn.__name__
    return fn


def message_feature(fn):
    "Will map the function to the message column"

    def wrapper(df):
        return df.message.map(fn)

    wrapper.__name__ = '__feature__' + fn.__name__
    return wrapper


def row_feature(fn):
    "Will apply the function to each row"

    def wrapper(df):
        return df.apply(fn, axis=1)

    wrapper.__name__ = '__feature__' + fn.__name__
    return wrapper


def get_date_features(df):
    df['year'] = df.timestamp.dt.year
    df['quarter'] = df.timestamp.dt.quarter
    df['month'] = df.timestamp.dt.month
    df['month_name'] = df.timestamp.dt.month_name()
    df['date'] = df.timestamp.dt.date
    df['day'] = df.timestamp.dt.day
    df['day_name'] = df.timestamp.dt.day_name()
    df['dayofweek'] = df.timestamp.dt.dayofweek
    df['dayofyear'] = df.timestamp.dt.dayofyear
    df['hour'] = df.timestamp.dt.hour
    df['minute'] = df.timestamp.dt.minute
    df['second'] = df.timestamp.dt.second
    df['date'] = df.timestamp.dt.date
    df['time'] = df.timestamp.dt.time
    return df


@message_feature
def laugh_count(msg):
    if '🤣' in msg or '😂' in msg:
        return 1
    elif re.match(r'\b(?:a*(?:ha)+h?|(?:l+o+)+l+)\b', msg, re.I):
        return 1
    return 0


@row_feature
def message_count(row):
    return 1 if not row.auto else 0


@feature
def username(df):
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
    return df.user.map(USERS.get)


def media_counts(media_name, row):
    if media_name + ' omitted' in row.message and row.auto:
        return 1
    return 0


@row_feature
def image_count(row):
    return media_counts('image', row)


@row_feature
def video_count(row):
    return media_counts('video', row)


# @row_feature
# def audio_count(row):
#     return media_counts('audio', row)


# @row_feature
# def document_count(row):
#     return media_counts('document', row)


# @row_feature
# def gif_count(row):
#     return media_counts('GIF', row)


# @row_feature
# def contact_card_count(row):
#     return media_counts('Contact card', row)


@message_feature
def question_count(msg):
    if msg[-1] == '?':
        return 1
    return 0


def message_size(msg):
    return len(msg)
