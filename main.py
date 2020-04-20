from message_parser import itermessages
from templates import Template

import pandas as pd

from dataclasses import asdict
from typing import Callable, Tuple


def iterfeatures(features) -> Tuple[str, Callable]:
    for name in dir(features):
        obj = features.__dict__[name]

        if hasattr(obj, '__name__') and obj.__name__.startswith('__feature__'):
            yield name, obj


def apply_features(df: pd.DataFrame) -> None:
    import features

    df = features.get_date_features(df)
    for name, feature in iterfeatures(features):
        df[name] = feature(df)


def get_raw_data(filepath, rows=None) -> pd.DataFrame:
    df = pd.DataFrame(data=[asdict(msg) for msg in itermessages(filepath, rows)])
    return df.sort_values('timestamp').reset_index(drop=True)


if __name__ == '__main__':
    filepath = '_chat.txt'
    df = get_raw_data(filepath)
    apply_features(df)
    template = Template(df)
