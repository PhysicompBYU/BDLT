#!/usr/bin/env python3


import argparse
from sys import stdin, stdout, stderr


def main():
    parser = argparse.ArgumentParser(
        description='Convert old BDL time stamps into milliseconds')
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        default=stdout)
    parser.add_argument('--decimal', '-d', action='store_const',
                        const=True, help='Use decimal time stamps')
    parser.add_argument('--tag', default='D,Time:0ms',
                        help='Prepend this to indicate version')
    parser.add_argument('--conversion', default=1000/512,
                        help='Multiply timestamps by this rate')
    
    args = parser.parse_args()

    print(args.tag, file=args.outfile)
    
    for line in args.infile:
        if line:
            parts = line.split(',')

            if len(parts) > 1 and parts[1].isdigit():
                x = int(parts[1])
                if args.decimal:
                    parts[1] = str(args.conversion * x)
                else:
                    parts[1] = str(round(args.conversion * x))
                
            print(','.join(parts), file=args.outfile)

    args.infile.close()
    args.outfile.close()


if __name__ == '__main__':
    main()
