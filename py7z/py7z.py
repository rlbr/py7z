#!/usr/bin/env python

## GNU GPL copyright notice #################################################
#                                                                           #
#   py7z, a quick and dirty Python wrapper for the 7-zip                    #
#   command line interface.                                                 #
#   Copyright (C) 2010  Argomirr                                            #
#                                                                           #
#   This program is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   (at your option) any later version.                                     #
#                                                                           #
#   This program is distributed in the hope that it will be useful,         #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.   #
#                                                                           #
#############################################################################

'''A quick and dirty Python wrapper for the 7-zip command line interface.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__version__ = 'Revision: 2'
__date__ = 'Date: 2010/12/12 15:27:40'
__copyright__ = 'Copyright (c) 2010 Argomirr'
__license__ = 'GNU GPL'

__all__ = ['SevenZipError', 'FatalError', 'CommandLineError', 'MemError', 'UserInterrupt',
            'unpack', 'unpack_no_full_paths', 'pack', 'test', 'list', 'comp7z', 'compZip',
            'compGZip', 'compBZip2', 'compLZMA', 'compLZMA2', 'compPPMd']


import subprocess as sp
import re
import os
import configparser
from dateutil.parser import parse as date_parse
def int_or_none(i):
    try:
        return int(i)
    except ValueError:
        pass

class MyParser(configparser.ConfigParser):
    def __init__(self):
        super().__init__(interpolation = configparser.ExtendedInterpolation())
    def getlist(self,section, option,fallback=None):
        data = self.get(section,option,fallback=fallback)
        if data == fallback:
            return data
        return list(filter(bool,re.split(' *, *',data)))
    def getpath(self,section, option,fallback=None):
        data = self.get(section,option,fallback=fallback)
        if data == fallback:
            return data
        return os.path.expandvars(data)
    def getpaths(self,section,option,fallback=None):
        data = self.getlist(section,option,fallback)
        return list(map(os.path.expandvars,data))
config = MyParser()
config.read('config.ini')

_SZIP_PATH = config.getpath('7z','executable')

comp7z = '7z'
compZip = 'zip'
compGZip = 'gzip'
compBZip2 = 'bzip2'
compLZMA = 'lzma'
compLZMA2 = 'lzma2'
compPPMd = 'ppmd'


class SevenZipError(Exception):
    '''Generic error class for 7z command line operations.'''
    def __init__(self, msg='7z: unknown error'):
        self.value = msg

    def __str__(self):
        return repr(self.value)

class FatalError(SevenZipError):
    '''Error class for 7z fatal error return code.'''
    def __init__(self, msg='7z: fatal error'):
        self.value = msg

class CommandLineError(SevenZipError):
    '''Error class for 7z commmand line error return code.'''
    def __init__(self, msg='7z: command line error'):
        self.value = msg

class MemError(SevenZipError):
    '''Error class for 7z memory error return code.'''
    def __init__(self, msg='7z: not enough memory to perform this operation'):
        self.value = msg

class UserInterrupt(SevenZipError):
    '''Error class for 7z user interruption return code.'''
    def __init__(self, msg='7z: process interrupted by user'):
        self.value = msg

def unpack(path, targetdir=os.getcwd(), fullpaths=True):
    '''Unpack the archive at path to targetdir, or cwd if omitted. Return True if succesful.'''
    if not os.path.exists(path): raise IOError('Could not find file/directory at path')

    args = [_SZIP_PATH, 'x', path, '-y', '-o' + targetdir]
    if not fullpaths: args[1] = 'e'

    sub = sp.Popen(args, stdout=sp.PIPE, stdin=sp.PIPE)
    res = sub.wait()
    if res == 0:
        return True
    elif res == 1:
        return False
    elif res == 2:
        raise FatalError
    elif res == 7:
        raise CommandLineError
    elif res == 8:
        raise MemError
    elif res == 255:
        raise UserInterrupt
    else:
        raise SevenZipError

def unpack_no_full_paths(path, targetdir=os.getcwd()):
    '''Convenience function for unpack(..., fullpaths=False).'''
    return unpack(path, targetdir, False)

def pack(path, archivepath, compression_level=5, compression_type='7z', password=None):
    '''Compress file or directory at path to archivepath. Return True if succesful.'''
    if not os.path.exists(path): raise IOError('Could not find file/directory at path')

    args = [_SZIP_PATH, 'a', archivepath, path, '-t' + compression_type, '-mx' + str(compression_level)]
    if password: args.append('-p' + password)

    sub = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE)
    res = sub.wait()

    if res == 0:
        return True
    elif res == 1:
        return False
    elif res == 2:
        raise FatalError
    elif res == 7:
        raise CommandLineError
    elif res == 8:
        raise MemError
    elif res == 255:
        raise UserInterrupt
    else:
        raise SevenZipError

def test(archivepath):
    '''Test archive at archivepath for errors. Return True if none were found, False otherwise.'''
    if not os.path.exists(archivepath): raise IOError('Could not find file/directory at path')

    args = [_SZIP_PATH, 't', archivepath, '-r']

    sub = sp.Popen(args, stdout=sp.PIPE, stdin=sp.PIPE)
    res = sub.wait()
    print(res)
    if res == 0:
        return True
    elif res == 1 or res == 2:
        return False
    elif res == 7:
        raise CommandLineError
    elif res == 8:
        raise MemError
    elif res == 255:
        raise UserInterrupt
    else:
        raise SevenZipError

def list_archive(archivepath):
    '''Return a list of all files in the archive.'''
    if not os.path.exists(archivepath): raise IOError('Could not find file/directory at path')

    args = [_SZIP_PATH, 'l', archivepath]

    sub = sp.Popen(args, stdout=sp.PIPE, stdin=sp.PIPE)

    stdout = sub.communicate()[0].decode().replace('\r\n','\n')
    res = sub.returncode
    if res == 0 or res == 1:
        end = set((' ','-'))
        lines = iter(stdout.split('\n'))
        for line in lines:
            chars = set(line)
            if chars == end:
                break
            prev = line
        spans = list(match.span() for match in re.finditer('-+',line))
        sub_strings = (prev[start:end] for start,end in spans)
        word_lists = (re.findall('[^ ]+',sub_string) for sub_string in sub_strings)
        cats = list(' '.join(words) for words in word_lists)
        ret = []
        cat_indices = dict((cat,i) for i,cat in enumerate(cats))
        converters = {
            cat_indices['Date Time']: date_parse,
            cat_indices['Size']: int,
            cat_indices['Compressed']: int_or_none,
        }
        for line in lines:
            chars = set(line)
            if chars == end:
                next_line = next(lines)
                break
            else:
                columns = (line[start:end].lstrip().rstrip() for start,end in spans)
                formed_data = (converters[index](data) if index in converters.keys() else data for index,data in enumerate(columns))
                ret.append(dict(zip(cats,formed_data)))
        final = list(next_line[start:end].lstrip().rstrip() for start,end in spans)
        summary = {
            'Total Size:':int(final[cat_indices['Size']]),
            'Total Compressed':int(final[cat_indices['Compressed']]),
            'Summary':final[cat_indices['Name']],
            }
        return ret,summary

    elif res == 2:
        raise FatalError
    elif res == 7:
        raise CommandLineError
    elif res == 8:
        raise MemError
    elif res == 255:
        raise UserInterrupt
    else:
        raise SevenZipError


if __name__ == '__main__':
    l = list_archive(r"H:\test\Mindustry-windows64-4.0-alpha-52.zip")
