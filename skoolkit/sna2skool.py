# -*- coding: utf-8 -*-

# Copyright 2009-2013 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of SkoolKit.
#
# SkoolKit is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# SkoolKit is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# SkoolKit. If not, see <http://www.gnu.org/licenses/>.

import argparse
from os.path import isfile

from . import read_bin_file, VERSION
from .snaskool import SkoolWriter, generate_ctls, write_ctl
from .snapshot import get_snapshot
from .sftparser import SftParser
from .ctlparser import CtlParser

START = 16384
DEFB_SIZE = 8
DEFM_SIZE = 66

def find(fname):
    if isfile(fname):
        return fname

def run(snafile, options):
    start = options.start

    # Read the snapshot file
    if snafile[-4:] == '.bin':
        ram = read_bin_file(snafile)
        org = 65536 - len(ram) if options.org is None else options.org
        snapshot = [0] * org
        snapshot.extend(ram)
        start = max(org, options.start)
    else:
        snapshot = get_snapshot(snafile, options.page)
    end = len(snapshot)

    # Pad out the end of the snapshot to avoid disassembly errors when an
    # instruction crosses the 64K boundary
    snapshot += [0] * (65539 - len(snapshot))

    if options.sftfile:
        # Use a skool file template
        writer = SftParser(snapshot, options.sftfile, options.zfill, options.asm_hex, options.asm_lower)
        writer.write_skool()
        return

    ctl_parser = CtlParser()
    if options.genctl:
        # Generate a control file
        ctls = generate_ctls(snapshot, start, options.code_map)
        write_ctl(options.genctlfile, ctls, options.ctl_hex)
        ctl_parser.ctls = ctls
    elif options.ctlfile:
        # Use a control file
        ctl_parser.parse_ctl(options.ctlfile)
    else:
        ctls = {start: 'c'}
        if end < 65536:
            ctls[end] = 'i'
        ctl_parser.ctls = ctls
    writer = SkoolWriter(snapshot, ctl_parser, options.defb_size, options.defb_mod, options.zfill, options.defm_width, options.asm_hex, options.asm_lower)
    writer.write_skool(options.write_refs, options.text)

def main(args):
    parser = argparse.ArgumentParser(
        usage='sna2skool.py [options] file',
        description="Convert a binary (raw memory) file or a SNA, SZX or Z80 snapshot into a skool file.",
        add_help=False
    )
    parser.add_argument('snafile', help=argparse.SUPPRESS, nargs='?')
    group = parser.add_argument_group('Options')
    group.add_argument('-V', '--version', action='version',
                       version='SkoolKit {}'.format(VERSION),
                       help='Show SkoolKit version number and exit')
    group.add_argument('-c', '--ctl', dest='ctlfile', metavar='FILE',
                       help='Use FILE as the control file')
    group.add_argument('-T', '--sft', dest='sftfile', metavar='FILE',
                       help='Use FILE as the skool file template')
    group.add_argument('-g', '--gen-ctl', dest='genctlfile', metavar='FILE',
                       help='Generate a control file in FILE')
    group.add_argument('-M', '--map', dest='code_map', metavar='FILE',
                       help='Use FILE as a code execution map when generating the control file')
    group.add_argument('-h', '--ctl-hex', dest='ctl_hex', action='store_true',
                       help='Write hexadecimal addresses in the generated control file')
    group.add_argument('-H', '--skool-hex', dest='asm_hex', action='store_true',
                       help='Write hexadecimal addresses and operands in the disassembly')
    group.add_argument('-L', '--lower', dest='asm_lower', action='store_true',
                       help='Write the disassembly in lower case')
    group.add_argument('-s', '--start', dest='start', metavar='ADDR', type=int, default=START,
                       help='Specify the address at which to start disassembling (default={})'.format(START))
    group.add_argument('-o', '--org', dest='org', metavar='ADDR', type=int,
                       help='Specify the origin address of a binary (.bin) file (default: 65536 - length)')
    group.add_argument('-p', '--page', dest='page', metavar='PAGE', type=int, choices=list(range(8)),
                       help='Specify the page (0-7) of a 128K snapshot to map to 49152-65535')
    group.add_argument('-t', '--text', dest='text', action='store_true',
                       help='Show ASCII text in the comment fields')
    group.add_argument('-r', '--no-erefs', dest='write_refs', action='store_false',
                       help="Don't add comments that list entry point referrers")
    group.add_argument('-n', '--defb-size', dest='defb_size', metavar='N', type=int, default=DEFB_SIZE,
                       help='Set the maximum number of bytes per DEFB statement to N (default={})'.format(DEFB_SIZE))
    group.add_argument('-m', '--defb-mod', dest='defb_mod', metavar='M', type=int, default=1,
                       help='Group DEFB blocks by addresses that are divisible by M')
    group.add_argument('-z', '--defb-zfill', dest='zfill', action='store_true',
                       help='Write bytes with leading zeroes in DEFB statements')
    group.add_argument('-l', '--defm-size', dest='defm_width', metavar='L', type=int, default=DEFM_SIZE,
                       help='Set the maximum number of characters per DEFM statement to L (default={})'.format(DEFM_SIZE))

    namespace, unknown_args = parser.parse_known_args(args)
    snafile = namespace.snafile
    if unknown_args or snafile is None or snafile[-4:].lower() not in ('.bin', '.sna', '.z80', '.szx'):
        parser.exit(2, parser.format_help())
    prefix = snafile[:-4]
    if not (namespace.ctlfile or namespace.sftfile):
        namespace.sftfile = find('{}.sft'.format(prefix))
    if not (namespace.ctlfile or namespace.sftfile):
        namespace.ctlfile = find('{}.ctl'.format(prefix))
    namespace.genctl = bool(namespace.genctlfile)
    run(snafile, namespace)
