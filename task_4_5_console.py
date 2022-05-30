def main(argv):
    program, *args = argv
    print(currency_check(*args))

    return 0


if __name__ == '__main__':
    import sys
    from func_lib import currency_check

    exit(main(sys.argv))
