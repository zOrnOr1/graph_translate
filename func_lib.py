from datetime import datetime
from datetime import timedelta
from copy import copy
from re import compile
import matplotlib.pyplot as plt
import numpy as np
import itertools


def files_r_w(logfile, output='result.txt', unknowns='unknown_result.txt',
              pattern=r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+'):
    """

    Takes logfile and writes result into 2 files: 1st is result 2nd is unknown results which didn't match the pattern
    pattern = r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+'

    :param logfile: takes in logfile
    :param output: output file, default is result.txt
    :param unknowns: writes unknown lines to this file, default is unknown_result.txt
    :param pattern: pattern to check file to, haven't tested different pattern's so change on your own risk
    :return: Statistics string
    """
    # (?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2}),(?P<millisec>\d+)\s+(?P<doze>[^\s]+).+
    time_format = '%H:%M:%S,%f'
    unknown_count = 0
    nan_count = 0
    doze_last = 0
    time_last = datetime.min
    time_counter = timedelta(0, 0, 0)
    lines_number = 0
    mes_format1 = compile(r'^\D')
    mes_format2 = compile(pattern)
    # r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2}),(?P<millisec>\d+)\s+(?P<doze>[^\s]+).+')
    with open(unknowns, 'w') as un_res:
        with open(output, 'w') as res:
            with open(logfile, 'r', newline='') as f:
                for ind, line in enumerate(f):
                    match1 = mes_format1.match(line)
                    match2 = mes_format2.match(line)
                    try:
                        doze = match2.group('doze')
                        if doze == 'NaN':
                            nan_count += 1
                            un_res.write(f"NaN at {ind + 1}. Replaced with last value: '{doze_last.strip()}'\n")
                            doze = doze_last
                        else:
                            float(doze.replace(',', '.'))
                        doze_correct = True
                    except (ValueError, AttributeError) as e:
                        doze_correct = False
                    try:
                        time = match2.group('time')
                        cur_time = datetime.strptime(time, time_format)
                        time_delta = cur_time - (time_last if time_last != datetime.min else cur_time)
                        if time_delta > timedelta(seconds=2):
                            time_delta = timedelta(microseconds=200)
                        time_counter += time_delta
                        time_last = copy(cur_time)
                        datecorrect = True
                    except (ValueError, AttributeError) as e:
                        datecorrect = False
                    if (match1 is not None) or not doze_correct or not datecorrect:
                        un_res.write(f"Unknown line at {ind + 1}: '{line.strip()}'\n")
                        unknown_count += 1
                        continue
                    else:
                        doze_last = copy(doze)
                        res.write(f'{time_counter} {float(doze.replace(",", ".")):.10f}\n')
                    lines_number += 1

    return (f'NaNs: {nan_count}\n'
            f'Unknown lines: {unknown_count}\n'
            f'Lines decoded: {lines_number}')


def plot_plot(file_to_read='result.txt'):
    koef = 0.88
    intensity = 112
    x_axix = []
    y_axix = []
    match_str = compile(r'(?P<time>\S+) (?P<doze>[\d|.]+)')
    with open('result_doze_to_current.txt', 'w') as fwriter:
        with open(file_to_read, 'r') as f:
            for line in f:
                match = match_str.match(line.strip())
                if match is not None:
                    mtime = match.group('time')
                    try:
                        elapsed = datetime.strptime(mtime, '%H:%M:%S.%f')
                    except ValueError:
                        mtime += '.000'
                        elapsed = datetime.strptime(mtime, '%H:%M:%S.%f')
                    x = ((elapsed.hour * 3600 + elapsed.minute * 60 + elapsed.second +
                          elapsed.microsecond / 1_000_000) * koef * intensity) / 1000
                    y = float(match.group('doze'))*1_000_000
                    fwriter.write(f'{x:.3f}\t{y:.3f}\n')
                    x_axix.append(x)
                    y_axix.append(y)

    plt.plot(x_axix, y_axix)
    plt.savefig('plot.png')
    plt.show()


def test():
    # import matplotlib.pyplot as plt
    # import matplotlib.dates as mdates
    import datetime as dt

    np.random.seed(1)

    N = 100
    y = np.random.rand(N)

    now = dt.datetime.now()
    print(type(now))
    then = now + dt.timedelta(days=100)
    print(type(then))
    days = mdates.drange(now, then, dt.timedelta(days=1))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.plot(days, y)
    plt.gcf().autofmt_xdate()
    plt.show()


if __name__ == '__main__':
    import sys

    files_r_w(sys.argv)
