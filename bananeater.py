#!/usr/bin/env python3
"""A clone of bsdgames worm."""
import collections
import copy
import curses
import random
import shutil
import time

EMPTY = ' '
FOODS = {str(n): n for n in range(1, 10)}
SNAKE_BODY = 'o'
SNAKE_HEAD = '@'

ON_EMPTY = 0
ON_FOOD = 1
ON_SNAKE = 2
OUT_OF_BOUNDS = 4

VERTICAL_PADDING = 2
HORIZONTAL_PADDING = VERTICAL_PADDING


def _replicate(count, item):
    return [copy.deepcopy(item) for _ in range(count)]


def random_moves(self):
    """A move strategy that moves randomly."""
    time.sleep(.1)
    directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    random.shuffle(directions)
    for direction in directions:
        landed_on = self.move_worm(direction)
        if landed_on[0] == ON_EMPTY:
            break
        elif landed_on[0] == ON_FOOD:
            self.place_food()
            self.parts_missing += landed_on[1]
            self.score += landed_on[1]
            break
    else:
        time.sleep(1)
        self.reset_game()


class WormGame:
    """Class which handles the game itself without the I/O."""

    def __init__(self, rows, columns, move_strategy):
        """Initialize a WormGame instance."""
        self.height = rows
        self.width = columns
        self.move_strategy = move_strategy
        self.reset_game()

    def reset_game(self):
        """Restore the game to a random initial state."""
        self.board = _replicate(self.height, _replicate(self.width, EMPTY))
        self.snake_parts = collections.deque()
        self.parts_missing = 0
        self.score = 0
        for i in range(1, 10):
            if i == 9:
                self.board[19][i] = SNAKE_HEAD
            else:
                self.board[19][i] = SNAKE_BODY
            self.snake_parts.append((19, i))
        self.place_food()

    def move_worm(self, direction):
        """Move the worm in a direction."""
        hy, hx = self.snake_parts[-1]
        assert self.board[hy][hx] == SNAKE_HEAD
        nhy, nhx = hy + direction[0], hx + direction[1]
        if nhy < 0 or nhx < 0:
            return (OUT_OF_BOUNDS,)
        try:
            going_to_empty = self.board[nhy][nhx] == EMPTY
            going_to_food = self.board[nhy][nhx] in FOODS
        except IndexError:
            return (OUT_OF_BOUNDS,)
        if going_to_empty or going_to_food:
            if self.parts_missing == 0:
                ty, tx = self.snake_parts.popleft()
                self.board[ty][tx] = EMPTY
            else:
                self.parts_missing -= 1
            if going_to_empty:
                self.board[hy][hx] = SNAKE_BODY
                self.board[nhy][nhx] = SNAKE_HEAD
                self.snake_parts.append((nhy, nhx))
                return (ON_EMPTY,)
            elif going_to_food:
                old_char = self.board[nhy][nhx]
                self.board[hy][hx] = SNAKE_BODY
                self.board[nhy][nhx] = SNAKE_HEAD
                self.snake_parts.append((nhy, nhx))
                return (ON_FOOD, FOODS[old_char])
        else:
            return (ON_SNAKE,)

    def place_food(self):
        """Place food in a random position."""
        assert not any(col in FOODS for row in self.board for col in row)
        while True:
            y = random.randrange(self.height)
            x = random.randrange(self.width)
            if self.board[y][x] == EMPTY:
                self.board[y][x] = random.choice(tuple(FOODS))
                break

    def play_game(self, stdscr):
        """Play the game until the heat death of the universe."""
        stdscr.scrollok(0)
        while True:
            for y in (VERTICAL_PADDING - 1, self.height + VERTICAL_PADDING):
                for x in range(HORIZONTAL_PADDING - 1,
                               self.width + HORIZONTAL_PADDING + 1):
                    stdscr.addch(y, x, "#")
            for x in (HORIZONTAL_PADDING - 1, self.width + HORIZONTAL_PADDING):
                for y in range(VERTICAL_PADDING,
                               self.height + VERTICAL_PADDING):
                    stdscr.addch(y, x, "#")
            for y, row in enumerate(self.board, start=VERTICAL_PADDING):
                stdscr.move(y, HORIZONTAL_PADDING)
                for col in row:
                    stdscr.addch(ord(col))
            if VERTICAL_PADDING >= 2:
                stdscr.addstr(VERTICAL_PADDING - 2,
                              HORIZONTAL_PADDING - 1,
                              "Score: {}".format(self.score))
            hy, hx = self.snake_parts[-1]
            stdscr.move(hy + VERTICAL_PADDING, hx + HORIZONTAL_PADDING)
            stdscr.refresh()
            self.move_strategy(self)


def main():
    """Play a clone of the bsdgames worm game."""
    width, height = shutil.get_terminal_size()
    game = WormGame(height - VERTICAL_PADDING * 2,
                    width - HORIZONTAL_PADDING * 2,
                    random_moves)
    try:
        curses.wrapper(game.play_game)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
