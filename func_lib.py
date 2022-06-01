from copy import copy
from datetime import datetime
from datetime import timedelta
from re import compile

import matplotlib.pyplot as plt
import numpy as np


def files_r_w(logfile, output='result.txt', unknowns='unknown_result.txt',
              pattern=r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+',
              limit=100000):
    """

    Takes logfile and writes result into 2 files: 1st is result 2nd is unknown results which didn't match the pattern
    pattern = r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+'

    :param logfile: takes in logfile
    :param output: output file, default is result.txt
    :param unknowns: writes unknown lines to this file, default is unknown_result.txt
    :param pattern: pattern to check file to, haven't tested different pattern's so change on your own risk
    :param limit: Чит лимит
    :return: Statistics string
    """
    # (?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2}),(?P<millisec>\d+)\s+(?P<doze>[^\s]+).+
    time_format = '%H:%M:%S,%f'
    unknown_count = 0
    error_flag = 0
    nan_count = 0
    doze_last = 0
    time_last = datetime.min
    time_counter = timedelta(0, 0, 0)
    lines_number = 0
    mes_format1 = compile(pattern)
    # r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2}),(?P<millisec>\d+)\s+(?P<doze>[^\s]+).+')
    with open(unknowns, 'w') as un_res:
        with open(output, 'w') as res:
            with open(logfile, 'r', newline='') as f:
                for ind, line in enumerate(f):
                    match1 = mes_format1.match(line)
                    try:
                        doze = match1.group('doze')
                        if doze == 'NaN':
                            nan_count += 1
                            un_res.write(f"NaN at {ind + 1}. Replaced with last value: '{doze_last.strip()}'\n")
                            doze = doze_last
                        else:
                            float(doze.replace(',', '.'))
                        doze_correct = True
                    except (ValueError, AttributeError):
                        doze_correct = False
                    try:
                        time = match1.group('time')
                        cur_time = datetime.strptime(time, time_format)
                        time_delta = cur_time - (time_last if time_last != datetime.min else cur_time)
                        if time_delta > timedelta(seconds=2):
                            time_delta = timedelta(microseconds=200)
                        time_counter += time_delta
                        time_last = copy(cur_time)
                        datecorrect = True
                    except (ValueError, AttributeError):
                        datecorrect = False
                    if not all((match1 is not None, doze_correct, datecorrect)):
                        un_res.write(f"Unknown line at {ind + 1}: '{line.strip()}'\n")
                        unknown_count += 1
                        continue
                    else:
                        try:
                            if float(doze.replace(",", ".")) > limit:
                                doze = doze_last
                            doze_last = copy(doze)
                            res.write(f'{time_counter} {float(doze.replace(",", ".")):.10f}\n')
                        except AttributeError:
                            print(f'Set limit ({limit}) is too low, no points to draw')
                            error_flag = 1
                            break
                        except ValueError:
                            un_res.write(f"Unknown line at {ind + 1}: '{line.strip()}'\n")
                            unknown_count += 1
                            continue
                    lines_number += 1

    return (f'NaNs: {nan_count}\n'
            f'Unknown lines: {unknown_count}\n'
            f'Lines decoded: {lines_number}'), error_flag


def plot_plot(file_to_read='result.txt', inten=112, outimage='plot.png', dut_name="Образец 1", trend=False,
              trend_poly_pow=5):
    koef = 0.88
    intensity = inten
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
                    y = float(match.group('doze'))  # * 1_000
                    fwriter.write(f'{x:.3f}\t{y:.3f}\n')
                    x_axix.append(x)
                    y_axix.append(y)

    plt.suptitle(f'Зависимость тока потребления от накопленной дозы', fontsize=13)
    plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True, useLocale=False)
    plt.xlabel('Накопленная доза, кРад')
    plt.ylabel('Ток, мА')
    plt.plot(x_axix, y_axix, '-0', label=dut_name)
    plt.minorticks_on()

    if trend:
        xnp = np.array(x_axix)
        ynp = np.array(y_axix)
        z = np.polyfit(xnp, ynp, trend_poly_pow)
        p = np.poly1d(z)
        print(f'Использованный полином:')
        print(p)
        plt.plot(xnp, p(xnp), '--r', label='Trend')
    plt.legend(loc='lower right')
    plt.grid()
    plt.tight_layout()
    plt.savefig(outimage)
    plt.show()


if __name__ == '__main__':
    import sys

    files_r_w(sys.argv)
