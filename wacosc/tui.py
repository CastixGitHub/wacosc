from wacosc.wacom import stylus, pad, touch
from curses import wrapper
from time import sleep


def main(stdscr):
    while True:
        stdscr.clear()

        i = 0
        for k, v in stylus.items():
            stdscr.addstr(i, 0, f"{k.upper().replace('_', ' ')}: {v}")
            i += 1

        i = 0
        for k, v in pad.items():
            stdscr.addstr(i, 35, f"{k.upper().replace('_', ' ')}: {v}")
            i += 1

        i = 0
        for k, v in touch.items():
            stdscr.addstr(i, 70, f"{k.upper().replace('_', ' ')}: {v}")
            i += 1

        stdscr.refresh()
        sleep(0.05)


try:
    wrapper(main)
except KeyboardInterrupt:
    print('interrupted.')
killing = True

