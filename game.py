import time
import curses
from random import randint

from neopixel import Adafruit_NeoPixel, Color

# LED strip configuration:
LED_COUNT = 32  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 5  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 15 # Set to 0 for darkest and 255 for brightest
LED_INVERT = False # True to invert the signal (when using NPN transistor level shift)

REWARD_COLORS = (Color(0, 100, 50), Color(0, 250, 50), Color(0, 100, 50))

# direction
UP, DOWN, LEFT, RIGHT = 0, 2, 1, 3
key_map = {curses.KEY_UP: UP, curses.KEY_DOWN: DOWN, curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT}


def _set_pixel(strip, position, color):
    strip.setPixelColor(position[1] * 8 + position[0], color)


def clrscr(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


class Game(object):clrscr
    def __init__(self):
        self.snake = [(1, 1), (2, 1)]
        self.direction = RIGHT
        self.reward = None
        self.reward_blink = True
        self.to_clear = None
        self.is_on = True
        self._frame = 0

    def input(self, key):
        if key in key_map.keys():
            new_dir = key_map[key]
            if abs(new_dir - self.direction) == 2:
                return
            self.direction = new_dir

    def next_frame(self):
        self._frame += 1

        next_head = self._calc_next_pos()
        if next_head in self.snake[1:]:
            self.is_on = False
            return
        self.snake.append(next_head)

        if next_head != self.reward:
            self.to_clear = self.snake[0]
            del self.snake[0]
        else:
            self.reward = None

        if (not self.reward) and randint(0, 10) == 7:
            rew = randint(0, 7), randint(0, 3)
            if rew not in self.snake:
                self.reward = rew

    def _calc_next_pos(self):
        head = self.snake[-1]
        if self.direction == RIGHT:
            return (head[0] + 1) % 8, head[1]
        if self.direction == LEFT:
            return (head[0] - 1) % 8, head[1]
        if self.direction == UP:
            return head[0], (head[1] - 1) % 4
        if self.direction == DOWN:
            return head[0], (head[1] + 1) % 4

    def draw(self, strip):
        snake_len = len(self.snake)
        for i, pos in enumerate(self.snake):
            _set_pixel(strip, pos, Color(255 - (snake_len - i) * 20, 0, 0))
        if self.to_clear:
            _set_pixel(strip, self.to_clear, Color(0, 0, 0))
        if self.reward:
            _set_pixel(strip, self.reward, REWARD_COLORS[self._frame % len(REWARD_COLORS)])


if __name__ == '__main__':
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)
    stdscr.nodelay(1)

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()

    try:
        while True:
            game = Game()
            while game.is_on:
                game.input(stdscr.getch())
                game.next_frame()
                game.draw(strip)
                strip.show()
                time.sleep(0.15)
            clrscr(strip)
    except KeyboardInterrupt:
        curses.endwin()
