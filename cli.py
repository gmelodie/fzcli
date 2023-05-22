#!/usr/bin/env python3

from pyflipper import PyFlipper
import argparse
import textwrap
import signal
from pprint import pprint
import os

parser = argparse.ArgumentParser(
                    prog='Flipper CLI',
                    description='Flipper command-line interface')
parser.add_argument('--dev',
                    help='specify device name', default='/dev/ttyACM0')

args = parser.parse_args()


HELP_TXT=f'''cd <dir>
    ls <dir>
    rm <file>
    cp <local_file> <flipper_file>
    clear
    exit
'''

# handle Ctrl+C
def signal_handler(sig, frame):
    print()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)


print('connecting to flipper...')
try:
    flipper = PyFlipper(com=args.dev)
except Exception as e:
    print(f'unable to open serial port {args.dev}: {e}')
    exit(1)


def rm(filename):
    try:
        flipper.storage.remove(file=filename)
    except:
        print("no file to remove")


def cp(computer_path, flipper_path, replace=True):
    # first remove file if already exists
    if replace:
        try:
            flipper.storage.remove(file=flipper_path)
        except:
           pass # no file to remove

    try:
        flipper.storage.copy(src=computer_path, dest=flipper_path)
    except Exception as e:
        print(e)
        print("not copying")


def ls(cur_dir, fzargs):
    directory = cur_dir
    if len(fzargs) == 1:
        if fzargs[0].startswith('/'): # path is absolute
            directory = fzargs[0]
        else: # 
            directory += '/' + fzargs[0]
    print('\t'+'\n\t'.join(flipper.storage.list(path=directory)['dirs']))
    print()


def chdir(cur_dir, fzargs):
    if fzargs[0] == '..': # one dir up
        index = cur_dir.rfind("/")
        if index != -1:  # Check if slash exists in the string
            cur_dir = cur_dir[:index]
    elif fzargs[0].startswith('/'): # absolute path
        cur_dir = fzargs[0].strip('/')
    else:
        cur_dir += '/' + fzargs[0].strip('/')
    return cur_dir


cur_dir = '/any'
stop = False
while not stop:
    line = input('fzcli> ')

    cmd = line.split()[0]
    fzargs = line.split()[1:]

    match cmd:
        case 'exit':
            stop = True
        case 'cd':
            cur_dir = chdir(cur_dir, fzargs)
            print(cur_dir)
        case 'ls':
            ls(cur_dir, fzargs)
        case 'pwd':
            print(cur_dir)
        case 'cp':
            cp(fzargs[0], fzargs[1])
        case 'rm':
            rm(fzargs[0])
        case 'clear':
            os.system('clear')
        case 'c':
            os.system('clear')
        case 'help':
            print(textwrap.dedent(HELP_TXT))
        case 'h':
            print(textwrap.dedent(HELP_TXT))
        case _:
            print('unknown command')



