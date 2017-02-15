#!/usr/bin/env python3


"""This script is meant to convert old BDL data files, which used
1/512 s "ticks" for timing information, into new-old data files (still
CSV, but with milliseconds instead). Ultimately, I hope that we move
away from the ascii-csv file, but for now it's easiest to integrate
the new with the old.

The script can be invoked with 

$ python ticks2ms.py /path/to/infile /path/to/outfile

and that will convert the data file infile into a millisecond-based 
format and save it at outfile. 

Time stamps will be rounded to the nearest whole number unless the
(--decimal | -d) flag is included, in which case it will write the
whole double-precision number out, but I don't know if the current
parser in VAT is capable of swallowing that.

The script will also preface the new file with a message intended to
warn future versions of VAT that it is using milliseconds instead of
ticks. This string defaults to "D,Time:0ms" and I intend to use that
for future iterations that might allow for offset times (instead of
the zero). The "ms" should be enough to know what unit we're
using. This string can be suppressed by adding "--spec none" to the
invocation, or can be replaced by any other message by following
--spec (or -s) with anything but none.

Finally, the script accepts an argument for the actual conversion
ratio. It defaults to 1000/512, which converts from ticks to
milliseconds, but anything else can be used instead with the
--conversion argument (or -c). This won't have too much utility,
except that it does mean that it can be used to back-convert new
millisecond data to ticks. I don't want this to become a habit, but
for *temporary* convenience, a file can be converted back like so:

$ python ticks2ms.py infile outfile -s none -c 0.512

As the new data will probably have the "D,Time:0ms" message in it,
this isn't a complete solution--that will have to be removed
manually. However, I don't care, because this is not the intended use
of the tool... so hopefully we don't need that for more than a month
or so.

"""


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
    parser.add_argument('--spec', '-s', default='D,Time:0ms',
                        help='Spec to indicate version (or "none")')
    parser.add_argument('--conversion', '-c', default=1000/512, type=float,
                        help='Multiply timestamps by this rate')
    
    args = parser.parse_args()

    if not args.spec.lower() == 'none':
        print(args.spec, file=args.outfile)
    
    for line in args.infile:
        if line.strip():  # Filter out empty line
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
