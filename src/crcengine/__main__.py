"""Command line invocation for crcengine to either generate code or run on a file"""

# This file is part of CrcEngine, a python library for CRC calculation
#
# Copyright 2021 Garden Tools software
#
# crcengine is free software: you can redistribute it an d /or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# crcengine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with crcengine.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys

import crcengine
import crcengine.codegen as codegen


def main():
    """Main entry point for command line"""
    parser = make_arg_parser()
    process_cmdline(parser)


def process_cmdline(parser, args=None):
    """Process command line arguments

    :param parser: Argparse parser
    :param args: commandline arguments to process (None will default to reading sys.argv)
    :return:
    """
    args = parser.parse_args(args)
    if args.command == "calculate":
        do_calculate(args)
    elif args.command == "generate":
        do_generate(args)
    else:
        parser.print_help(sys.stderr)
        raise ValueError("Subcommand must be specified")


def make_arg_parser():
    """Create the ArgumentParser for crcengine

    :return:
    """
    parser = argparse.ArgumentParser(
        prog="crcengine",
        description="Calculate CRCs for data or generate CRC calculation code.",
    )
    subparsers = parser.add_subparsers(dest="command")
    calculate = _add_calculate_parser(subparsers)
    generate = _add_generate_parser(subparsers)
    _add_shared_options([calculate, generate])
    return parser


def _add_shared_options(parsers):
    """Add the shared options to multiple parsers

    :param parsers: iterable of sub-command Argparse parsers
    :return:
    """
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
    """Add parser for generate command"""
    generate = subparsers.add_parser(
        "generate", help="Generate C code to calculate a specific CRC"
    )
    generate.add_argument(
        "-d", metavar="DIRECTORY", dest="output_dir", help="Output directory"
    )
    return generate


def _add_calculate_parser(subparsers):
    """Add parser for calculate command

    :param subparsers: subparsers as returned from add_subparsers()
    :return:
    """
    calculate = subparsers.add_parser(
        "calculate",
        help="Calculate CRC of input",
    )
    grp = calculate.add_mutually_exclusive_group(required=True)
    grp.add_argument(
        "-f", action="store", metavar="FILE", dest="file", help="Calculate CRC for FILE"
    )
    grp.add_argument(
        "-s",
        action="store",
        metavar="STRING",
        dest="string",
        help="Calculate CRC of STRING",
    )
    grp.add_argument("--stdin", action="store_true", help="Read input from STDIN")
    calculate.add_argument(
        "--hex-prefix", action="store_true", help="Prefix result with 0x"
    )
    return calculate


# '''
# def read_in_chunks(file_object, chunk_size=1024):
#     """Lazy function (generator) to read a file piece by piece.
#     Default chunk size: 1k."""
#     while True:
#         data = file_object.read(chunk_size)
#         if not data:
#             break
#         yield data
# '''


def do_calculate(args):
    """Perform the calculate command

    :param args: arguments as produced by parse_args()
    :return:
    """
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
    """Perform the generate command

    :param args:  arguments as produced by parse_args()
    :return:
    """
    codegen.generate_code(args.algorithm, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
