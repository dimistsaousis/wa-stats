import pandas as pd

from dataclasses import asdict
from message_parser import itermessages


def iterfeatures():
    import features

    for name in dir(features):
        obj = features.__dict__[name]

        if hasattr(obj, '__name__') and obj.__name__.startswith('__feature__'):
            yield name, obj


def apply_features(df):
    for name, feature in iterfeatures():
        df[name] = df.apply(feature, axis=1)


def get_raw_data(filepath, rows=None):
    df = pd.DataFrame(data=[asdict(msg) for msg in itermessages(filepath, rows)])
    return df.sort_values('date').reset_index(drop=True)


if __name__ == '__main__':
    filepath = '_chat.txt'
    df = get_raw_data(filepath)
    apply_features(df)
