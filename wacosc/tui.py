from wacosc.wacom import stylus, pad, touch
from curses import wrapper
from time import sleep


def main(stdscr):
    while True:
        stdscr.clear()

        i = 0
        for k, v in stylus.items():
            stdscr.addstr(i, 0, f'{k.upper()}: {v}')
            i += 1

        i = 0
        for k, v in pad.items():
            stdscr.addstr(i, 35, f'{k.upper()}: {v}')
            i += 1

        i = 0
        for k, v in touch.items():
            stdscr.addstr(i, 70, f'{k.upper()}: {v}')
            i += 1

            
        stdscr.refresh()
        try:
            sleep(0.05)
        except KeyboardInterrupt:
            # it's a shame if we hit outside of sleep
            break
        
wrapper(main)
killing = True
