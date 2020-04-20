from features import get_date_features
from dataclasses import dataclass, field
from datetime import datetime
import calendar
import pandas as pd
import seaborn as sns


@dataclass
class Template:
    df: pd.DataFrame
    min_date: datetime = field(init=False)
    max_date: datetime = field(init=False)
    grid: pd.DataFrame = field(init=False)

    def __post_init__(self):
        self.min_date = self.df.timestamp.min()
        self.max_date = self.df.timestamp.max()
        self.grid = self._get_grid(hours=1)

    def _get_grid(self, **offsets):
        grid = []
        current = self.min_date
        while current < self.max_date:
            grid.append(current)
            current = current + pd.DateOffset(**offsets)
        grid = pd.DataFrame(columns=['timestamp'], data=grid)
        return get_date_features(grid)

    def occurences(self, x, y):
        hourly = ['hour']
        daily = ['day', 'dayofweek', 'dayofyear']
        # monthly = ['month']
        if x in hourly or y in hourly:
            grid = self.grid[[x, y]]
        elif x in daily or y in daily:
            grid = self.grid[list({x, y, 'date'})].drop_duplicates()
        else:
            grid = self.grid[list({x, y, 'month', 'year'})].drop_duplicates()
        return grid.groupby([x, y]).size()

    def heatmap(self, x, y, value):
        data = self.df.groupby([x, y])[value].sum() / self.occurences(x, y)
        data.name = value
        data = data.reset_index().pivot(columns=x, index=y, values=value).fillna(0)
        data.columns.name = x
        data.index.name = y
        data.index = data.index.map(plot_labels(y))
        data.columns = data.columns.map(plot_labels(x))
        sns.heatmap(data).set_title(plot_title(value))

    def cumsum(self, *groupby, value):
        df = self.df[self.df[value] != 0]
        x = df.timestamp
        if groupby:
            y = df.groupby(list(groupby))[value].cumsum()
            hue = df[groupby[0]] if len(groupby) == 1 else None
        else:
            y = df[value].cumsum()
            hue = None
        sns.lineplot(x=x, y=y, hue=hue).set_title(plot_title(value))

    @property
    def count_fields(self):
        return [field for field in self.df.columns if field.endswith('_count')]

    def user_stats(self):
        size = self.df.groupby('username').size()
        df = self.df.groupby('username')[self.count_fields].sum().divide(size, axis=0)
        df = df.applymap("{0:.0%}".format)
        df['total'] = size
        df.columns = df.columns.map(plot_title)
        df.index.name = ''
        return df


def plot_title(value):
    return value.replace('_count', '')


def plot_labels(x):
    def day_name(weekday):
        return calendar.day_name[weekday]

    def month_name(month):
        return calendar.month_name[month]

    def hour_name(hour):
        am_or_pm = 'am' if hour < 12 else 'pm'
        hour = hour % 12
        if hour == 0:
            return '12' + am_or_pm
        return f'{hour} {am_or_pm}'

    if x == 'month':
        return month_name
    elif x == 'dayofweek':
        return day_name
    elif x == 'hour':
        return hour_name
    else:
        return lambda x: x
