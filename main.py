from func_lib import files_r_w
from func_lib import plot_plot
from func_lib import test


def main(argv):
    print(files_r_w('Sarov3obr_2part.txt'))
    plot_plot()


if __name__ == '__main__':
    import sys

    main(sys.argv)
