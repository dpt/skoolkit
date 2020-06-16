#!/usr/bin/env python3

import sys
import os
from os.path import isfile, basename
import re

def parse_args(args):
    if len(args) != 2:
        print_usage()
    exp_diffs_file, diff_file = args
    if not isfile(diff_file):
        sys.stderr.write('ERROR: {}: file not found\n'.format(diff_file))
        sys.exit(1)

    return diff_file, exp_diffs_file

def print_usage():
    sys.stderr.write("""Usage: {} exp-diffs.txt diffs.txt

  Examines a diff file generated by 'write-files' and filters out expected
  differences.

  The expected diffs file (exp-diffs.txt) may contain any of the following
  directives:

  ; @ExpIgnoreCase
      Ignore case in expected diffs. This will discard a generated diff if it
      differs from an expected diff only in case.

  ; @IgnoreAddressIndex=i
      Ignore an address at index 'i' in an expected diff. For every expected
      diff containing one or more lines 'd' with a decimal address at d[i:i+5],
      this will discard any generated diff that matches it with the decimal
      addresses replaced by hexadecimal addresses.

  ; @IgnoreDiffsContainingRegex=r
      Ignore generated diffs that contain the regex 'r'. This will discard a
      generated diff if any part of it matches the regular expression 'r'.

  ; @IgnoreFile=f
      Ignore generated diffs from a file whose name ends with 'f'.

  ; @IgnoreWhitespace
      Ignore leading whitespace, trailing whitespace and blank lines in
      generated diffs. This will discard a generated diff if the old lines
      differ from the new lines only in the amount of leading/trailing
      whitespace or blank lines.

  ; @IgnoreWrap
      Ignore line wrapping. This will discard a generated diff if the old lines
      differ from the new lines only in where they are wrapped.

  ; @RegexReplace=/s/r
      Replace substrings that match the regular expression 's' with the regular
      expression 'r' in the old lines of generated diffs. This will discard a
      generated diff if the old lines match the new lines after the replacement
      has been made.

  ; @RegexReplaceNew=/s/r
      Replace substrings that match the regular expression 's' with the regular
      expression 'r' in the new lines of generated diffs. This will discard a
      generated diff if the new lines match the old lines after the replacement
      has been made.
""".format(basename(sys.argv[0])))
    sys.exit(1)

def get_diffs(fname, options=None, fnames=False):
    diffs = []
    with open(fname) as f:
        cur_file = fname if fnames else None
        last = None
        for line in f:
            s_line = line.rstrip('\n')
            if options is not None and s_line.startswith('; @'):
                option, sep, value = s_line[3:].rstrip().partition('=')
                if sep:
                    options.setdefault(option, []).append(value)
                else:
                    options[option] = True
                continue
            if s_line.startswith('--- '):
                continue
            if s_line.startswith('+++ ') and fnames:
                cur_file = s_line.split()[1]
            elif s_line and s_line[0] in '+-':
                if last is None:
                    diffs.append((cur_file, [], []))
                if s_line[0] == '-':
                    diffs[-1][1].append(s_line)
                else:
                    diffs[-1][2].append(s_line)
                last = s_line[0]
            else:
                last = None
    return diffs

def convert_addresses(lines, index):
    changed = False
    hex_lines = []
    for line in lines:
        address = line[index + 1:index + 6]
        if address.isdigit():
            hex_lines.append('{}${:04X}{}'.format(line[:index + 1], int(address), line[index + 6:]))
            changed = True
        else:
            hex_lines.append(line)
    return changed, hex_lines

def run(diff_file, exp_diffs_file):
    diffs = get_diffs(diff_file, fnames=True)
    options = {}
    orig_exp_diffs = []
    if isfile(exp_diffs_file):
        orig_exp_diffs = get_diffs(exp_diffs_file, options)
    ignore_exp_case = options.get('ExpIgnoreCase', False)
    ignore_whitespace = options.get('IgnoreWhitespace', False)
    ignore_wrap = options.get('IgnoreWrap', False)
    regex_new_subs = options.get('RegexReplaceNew', ())
    regex_subs = options.get('RegexReplace', ())
    ignore_files = options.get('IgnoreFile', ())
    ignore_regexes = options.get('IgnoreDiffsContainingRegex', ())
    ignore_address_indexes = options.get('IgnoreAddressIndex', ())

    exp_diffs = [(fname, old[:], new[:]) for fname, old, new in orig_exp_diffs]
    exp_diffs_map = {i: i for i in range(len(exp_diffs))}
    for i in ignore_address_indexes:
        index = int(i)
        for i, (_, old_lines, new_lines) in enumerate(orig_exp_diffs):
            old_changed, hex_old_lines = convert_addresses(old_lines, index)
            new_changed, hex_new_lines = convert_addresses(new_lines, index)
            if old_changed or new_changed:
                exp_diffs_map[len(exp_diffs)] = i
                exp_diffs.append((None, hex_old_lines, hex_new_lines))

    if ignore_exp_case:
        for entry in exp_diffs:
            entry[1][:] = [s.lower() for s in entry[1]]
            entry[2][:] = [s.lower() for s in entry[2]]

    used_exp_diffs = set()
    unexp_diffs = set()
    lines = []
    last_fname = None
    for fname, old, new in diffs:
        ignore = any(fname.endswith(ignore_file) for ignore_file in ignore_files)
        if ignore:
            continue

        old_lines = [line[1:] for line in old]
        new_lines = [line[1:] for line in new]

        all_lines = old_lines + new_lines
        ignore = any(
            any(re.search(regex, line) for line in all_lines)
            for regex in ignore_regexes
        )

        if ignore:
            continue

        for sub in regex_new_subs:
            pattern, rep = sub[1:].split(sub[0])[0:2]
            new_lines = [re.sub(pattern, rep, line) for line in new_lines]

        for sub in regex_subs:
            pattern, rep = sub[1:].split(sub[0])[0:2]
            old_lines = [re.sub(pattern, rep, line) for line in old_lines]

        if ignore_whitespace:
            old_lines = [line.strip() for line in old_lines if line.strip()]
            new_lines = [line.strip() for line in new_lines if line.strip()]

        if ignore_wrap:
            old_lines = [' '.join(old_lines)]
            new_lines = [' '.join(new_lines)]

        if old_lines == new_lines:
            continue

        if ignore_exp_case:
            old_lines = [s.lower() for s in old]
            new_lines = [s.lower() for s in new]
        else:
            old_lines, new_lines = old, new
        for i, (_, exp_old, exp_new) in enumerate(exp_diffs):
            if (old_lines, new_lines) == (exp_old, exp_new):
                used_exp_diffs.add(i)
                break
        else:
            unexp_diff = (tuple(old), tuple(new))
            if unexp_diff in unexp_diffs:
                continue
            unexp_diffs.add(unexp_diff)
            if last_fname != fname:
                lines.append('+++ {}'.format(fname))
                last_fname = fname
            for line in old:
                lines.append(line)
            for line in new:
                lines.append(line)
            lines.append('')

    if lines:
        suffix = '' if isfile(exp_diffs_file) else ' (not found)'
        print('+ Expected diffs file: {}{}'.format(exp_diffs_file, suffix))
        print('+')
        for directive, value in (
            ('ExpIgnoreCase', ignore_exp_case),
            ('IgnoreAddressIndex', ignore_address_indexes),
            ('IgnoreDiffsContainingRegex', ignore_regexes),
            ('IgnoreFile', ignore_files),
            ('IgnoreWhitespace', ignore_whitespace),
            ('IgnoreWrap', ignore_wrap),
            ('RegexReplace', regex_subs),
            ('RegexReplaceNew', regex_new_subs)
        ):
            if isinstance(value, (list, tuple)):
                for val in value:
                    print('+ @{}={}'.format(directive, val))
            else:
                print('+ @{}={}'.format(directive, value))
        print('')
        print('\n'.join(lines))

    for i in sorted(used_exp_diffs):
        _, exp_old, exp_new = orig_exp_diffs[exp_diffs_map[i]]
        for line in exp_old + exp_new + ['']:
            sys.stderr.write(line + '\n')

def main():
    run(*parse_args(sys.argv[1:]))

if __name__ == '__main__':
    main()
