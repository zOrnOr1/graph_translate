from func_lib import files_r_w
from func_lib import plot_plot
from func_lib import test


def main(argv):
    """
    r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+'
    :param argv:
    :return:
    """

    # program, *args = argv
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', '-i', help="Название лог файла", type=str, required=True)
    parser.add_argument('--un', '-un', help="Файл с необработанными строками лога, default = unknown_result.txt",
                        type=str,
                        default='unknown_result.txt')
    parser.add_argument('--o', '-o', help="Обработанный файл формата Время - Ток, default = result.txt", type=str,
                        default='result.txt')
    parser.add_argument('--p', '-p',
                        help="Патерн для обработки формата python regex в виде raw str, default = r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+'\n"
                             "должен включать группы совпадения <date> <time> <doze>",
                        type=str,
                        default=r'(?P<date>\d{2}\.\d{2}\.\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d+)\s+(?P<doze>[^\s]+).+')
    parser.add_argument('--intens', '-intens', help="Интенсивность облучения в рентген/сек, default = 112", type=float,
                        default=112)
    parser.add_argument('--oimg', '-oimg', help="Сохраняет график в файл, default = plot.png", type=str,
                        default='plot.png')
    parser.add_argument('--dname', '-dname', help="Название образца на легенде, default = Образец 1", type=str,
                        default='Образец 1')
    parser.add_argument('--pow', '-pow', help="Степень полинома", type=int, default=1)
    parser.add_argument('--trend', '-trend', help="Нарисовать линию тренда", type=bool, default=False)
    parser.add_argument('--l', '-l', help="Чит - лимит", type=float, default=10000000000)

    args = parser.parse_args()
    response, error_flag = files_r_w(args.i, output=args.o, unknowns=args.un, pattern=args.p, limit=args.l)
    print(response)
    if not error_flag:
        plot_plot(file_to_read=args.o, inten=args.intens, outimage=args.oimg, dut_name=args.dname,
                  trend_poly_pow=args.pow, trend=args.trend)


if __name__ == '__main__':
    import sys
    import argparse

    main(sys.argv)
