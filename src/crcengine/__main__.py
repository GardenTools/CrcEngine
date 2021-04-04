"""Command line invocation for crcengine to either generate code or run on a file"""
import argparse
import sys

import crcengine
import crcengine.codegen as codegen


def main():
    parser = make_arg_parser()
    process_cmdline(parser)


def process_cmdline(parser, args=None):
    args = parser.parse_args(args)
    if args.command == "calculate":
        do_calculate(args)
    elif args.command == "generate":
        do_generate(args)
    else:
        parser.print_help(sys.stderr)
        raise ValueError("Subcommand must be specified")


def make_arg_parser():
    parser = argparse.ArgumentParser(
        prog="crcengine",
        description="Calculate CRCs for data or generate CRC calculation code."
    )
    subparsers = parser.add_subparsers(dest="command")
    calculate = _add_calculate_parser(subparsers)
    generate = _add_generate_parser(subparsers)
    _add_shared_options([calculate, generate])
    return parser


def _add_shared_options(parsers):
    for sub_parser in parsers:
        sub_parser.add_argument(
            "-a",
            action="store",
            metavar="ALGO",
            dest="algorithm",
            required=True,
            help="Use algorithm ALGO",
        )


def _add_generate_parser(subparsers):
    generate = subparsers.add_parser(
        "generate",
        help="Generate C code to calculate a specific CRC"
    )
    generate.add_argument(
        "-d",
        metavar="DIRECTORY",
        dest="output_dir",
        help="Output directory"

    )
    return generate


def _add_calculate_parser(subparsers):
    calculate = subparsers.add_parser(
        "calculate",
        help="Calculate CRC of input",
    )
    grp = calculate.add_mutually_exclusive_group(required=True)
    grp.add_argument(
        "-f", action="store", metavar="FILE", dest="file", help="Calculate CRC for FILE"
    )
    grp.add_argument(
        "-s", action="store", metavar="STRING", dest="string", help="Calculate CRC of STRING"
    )
    grp.add_argument(
        "--stdin", action="store_true", help="Read input from STDIN"
    )
    calculate.add_argument(
        "--hex-prefix",
        action="store_true",
        help="Prefix result with 0x"

    )
    return calculate


'''
def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data
'''


def do_calculate(args):
    algo = crcengine.new(args.algorithm)
    prefix = "0x" if args.hex_prefix else ""
    if args.string:
        data = args.string.encode()
    elif args.file:
        # This is a bit stupid for now just to get it working, ideally calculation would be chunked
        with open(args.file, "rb") as f:
            data = f.read()
    else:
        data = sys.stdin.read().encode()
    result = algo.calculate(data)
    print("{}{:x}".format(prefix, result))


def do_generate(args):
    codegen.generate_code(args.algorithm, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
