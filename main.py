import re
import sys
import time
import argparse
import itertools as it

from pynput import mouse, keyboard


CTRL_PRESSED = False


def parse_args(argv):
    parser = argparse.ArgumentParser('fill')
    parser.add_argument('file', help='File to load strings from')
    parser.add_argument('-s', '--skip', help='RegEx to skip strings from file')
    return parser.parse_args(argv)


def on_click(write, line_source, *args):
    if CTRL_PRESSED:
        write(next(line_source))


def on_press(key):
    global CTRL_PRESSED
    CTRL_PRESSED = key == keyboard.Key.ctrl


def on_release(key):
    global CTRL_PRESSED
    if key == keyboard.Key.ctrl:
        CTRL_PRESSED = False


def run_listeners(line_source):
    kbd_controller = keyboard.Controller()
    kbd_listener = keyboard.Listener(
        daemon=False,
        on_press=on_press,
        on_release=on_release)
    mouse_listener = mouse.Listener(
        daemon=False,
        on_click=lambda *args: on_click(kbd_controller.type,
                                        line_source,
                                        *args)
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
                if args.skip and not re.match(args.skip, stripped_line):
                    yield stripped_line

    else:
        def line_source():
            with open(args.file, 'r') as f:
                filtered_lines = (line for line in f
                                  if args.skip and
                                  not re.match(args.skip, line))
                for line in it.cycle(filtered_lines):
                    yield line.rstrip('\n')
    run_listeners(line_source())
    print('Press Ctrl-C to exit')
    while True:
        try:
            time.sleep(60*60)
        except KeyboardInterrupt:
            print('shutting down...')
            break


if __name__ == '__main__':
    main(sys.argv[1:])
