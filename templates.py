import calendar


def heatmap(df, x, y, value):
    data = df.groupby([x, y])[value].sum().reset_index()
    data = data.pivot(columns=x, index=y, values=value).fillna(0)
    data.columns.name = ''
    data.index.name = ''
    data.index = data.index.map(plot_labels(y))
    data.columns = data.columns.map(plot_labels(x))
    return data


def plot_labels(x):
    def day_name(weekday):
        return calendar.day_name[weekday]

    def month_name(month):
        return calendar.month_name[month]

    def hour_name(hour):
        if hour == 0:
            return '12 am'
        am_or_pm = 'am' if hour < 12 else 'pm'
        return f'{hour % 12} {am_or_pm}'

    if x == 'month':
        return month_name
    elif x == 'weekday':
        return day_name
    elif x == 'hour':
        return hour_name
    else:
        return lambda x: x
