#!/usr/bin/env python3
"""A clone of bsdgames worm."""
import collections
import copy
import curses
import random
import shutil
import time

EMPTY = ' '
FOOD = '*'
SNAKE_BODY = 'o'
SNAKE_HEAD = '@'

ON_EMPTY = 0
ON_FOOD = 1
ON_SNAKE = 2
OUT_OF_BOUNDS = 4


def _replicate(count, item):
    return [copy.deepcopy(item) for _ in range(count)]


class WormGame:
    """Class which handles the game itself without the I/O."""

    def __init__(self, rows, columns):
        """Initialize a WormGame instance."""
        self.height = rows
        self.width = columns
        self.board = _replicate(rows, _replicate(columns, EMPTY))
        self.snake_parts = collections.deque()
        for i in range(1, 10):
            if i == 9:
                self.board[19][i] = SNAKE_HEAD
            else:
                self.board[19][i] = SNAKE_BODY
            self.snake_parts.append((19, i))

    def move_worm(self, direction):
        """Move the worm in a direction."""
        hy, hx = self.snake_parts[-1]
        assert self.board[hy][hx] == SNAKE_HEAD
        nhy, nhx = hy + direction[0], hx + direction[1]
        if nhy < 0 or nhx < 0:
            return OUT_OF_BOUNDS
        try:
            going_to_empty = self.board[nhy][nhx] == EMPTY
            going_to_food = self.board[nhy][nhx] == FOOD
        except IndexError:
            return OUT_OF_BOUNDS
        if going_to_empty or going_to_food:
            ty, tx = self.snake_parts.popleft()
            self.board[ty][tx] = EMPTY
            self.board[hy][hx] = SNAKE_BODY
            self.board[nhy][nhx] = SNAKE_HEAD
            self.snake_parts.append((nhy, nhx))
            return ON_EMPTY if going_to_empty else ON_FOOD
        else:
            return ON_SNAKE

    def place_food(self):
        """Place food in a random position."""
        assert not any(col == FOOD for row in self.board for col in row)
        while True:
            y = random.randrange(self.height)
            x = random.randrange(self.width)
            if self.board[y][x] == EMPTY:
                self.board[y][x] = FOOD
                break

    def grow_snake(self, direction):
        """Add a piece to the snake."""
        by, bx = self.snake_parts[-1]
        hy, hx = by + direction[0], bx + direction[1]
        self.board[by][bx] = SNAKE_BODY
        self.board[hy][hx] = SNAKE_HEAD
        self.snake_parts.append((hy, hx))

    def play_game(self, stdscr):
        """Play the game until the heat death of the universe."""
        stdscr.scrollok(0)
        while True:
            for y in (1, self.height + 2):
                for x in range(1, self.width + 3):
                    stdscr.addch(y, x, "#")
            for x in (1, self.width + 2):
                for y in range(1, self.height + 2):
                    stdscr.addch(y, x, "#")
            for y, row in enumerate(self.board, start=2):
                stdscr.move(y, 2)
                for col in row:
                    stdscr.addch(ord(col))
            hy, hx = self.snake_parts[-1]
            stdscr.move(hy + 2, hx + 2)
            stdscr.refresh()

            time.sleep(.1)
            directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
            random.shuffle(directions)
            while directions:
                direction = directions.pop()
                return_value = self.move_worm(direction)
                if return_value == EMPTY:
                    break
                elif return_value == ON_FOOD:
                    self.grow_snake(direction)
                    self.place_food()
                    break


def main():
    """Play a clone of the bsdgames worm game."""
    width, height = shutil.get_terminal_size()
    game = WormGame(height - 4, width - 4)
    game.place_food()
    curses.wrapper(game.play_game)

if __name__ == "__main__":
    main()
