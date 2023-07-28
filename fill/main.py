import re
import sys
import time
import argparse
import itertools as it

import pyperclip

from pynput import mouse, keyboard


CTRL_PRESSED = False


def parse_args(argv):
    parser = argparse.ArgumentParser('fill')
    parser.add_argument('file', help='File to load strings from')
    parser.add_argument('-s', '--skip', help='RegEx to skip strings from file')
    parser.add_argument('-c', '--clipboard',
                        action='store_true',
                        help='Use clipboard instead of typing')
    return parser.parse_args(argv)


def on_click(write, line_source, *args):
    if CTRL_PRESSED:
        write(next(line_source))


def on_press(key):
    global CTRL_PRESSED
    if key in (keyboard.Key.ctrl,
               keyboard.Key.ctrl_l,
               keyboard.Key.ctrl_r):
        CTRL_PRESSED = not CTRL_PRESSED


def run_listeners(line_source, use_clipboard=False):
    kbd_controller = keyboard.Controller()

    writer = kbd_controller.type
    if use_clipboard:
        def writer(string):
            pyperclip.copy(string)
            with kbd_controller.pressed(keyboard.Key.ctrl):
                kbd_controller.press('v')

    kbd_listener = keyboard.Listener(
        daemon=False,
        on_press=on_press
    )
    mouse_listener = mouse.Listener(
        daemon=False,
        on_click=lambda *args: on_click(writer, line_source, *args)
    )
    kbd_listener.start()
    mouse_listener.start()
    return kbd_controller, kbd_listener, mouse_listener


def main(argv):
    args = parse_args(argv)
    if args.file == '-':
        def line_source():
            for line in sys.stdin:
                stripped_line = line.rstrip('\n')
                if not (args.skip and re.match(args.skip, stripped_line)):
                    yield stripped_line

    else:
        def line_source():
            with open(args.file, 'r', encoding='utf-8') as f:
                filtered_lines = (line for line in f
                                  if not (args.skip and
                                          re.match(args.skip,
                                                   line)))
                for line in it.cycle(filtered_lines):
                    yield line.rstrip('\n')
    run_listeners(line_source(), use_clipboard=args.clipboard)
    print('Press Ctrl-C to exit')
    while True:
        try:
            time.sleep(60*60)
        except KeyboardInterrupt:
            print('shutting down...')
            break


def run_default():
    main(sys.argv[1:])


if __name__ == '__main__':
    run_default()
