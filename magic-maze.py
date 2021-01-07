import os
import sys
from itertools import chain


WALL = '#'
SPACE = ' '
PLAYER = '@'
FINISH = '$'
VALID_ACTIONS = ['W', 'S', 'A', 'D', 'R', 'Q']
MAZE_SYMBOLS = [WALL, SPACE, PLAYER, FINISH]


# trick to get only one character input from the user
# it works with Unix and Windows
class _Getch:
    """Gets a single character from standard input.  
       Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


def new_game(maze_name):
    maze_array = get_maze_from_file(maze_name)
    x_position, y_position = get_current_position(maze_array)
    x_initial_position = x_position
    y_initial_position = y_position
    previous_symbol = ' '
    special_positions = get_special_positions(maze_array)

    while True:
        print_headers_and_maze(maze_name, maze_array)
        previous_symbol, x_position, y_position = move(x_position, 
                                                       y_position, 
                                                       maze_array, 
                                                       previous_symbol, 
                                                       special_positions, 
                                                       x_initial_position, 
                                                       y_initial_position)
        if reach_exit_maze(previous_symbol):
            break
    
    os.system("clear")
    print_rules()
    print("----------")
    print_maze(maze_array)
    print("-------------------")
    print("Congratulations :-)")
    print("-------------------")
    getch()


def add_special_position(special_positions, index, another_index, value):
    point = (index, another_index)

    if value in special_positions:
        if len(special_positions[value]) > 1:
            raise Exception(f"Value in maze more than one time repeated: {value}") 
        special_positions[value].append(point)
    else:
        special_positions[value] = [point]


def get_special_positions(maze_array):
    special_positions ={}
    for index, value in enumerate(maze_array):
        for another_index, another_value in enumerate(value):
            if not another_value in MAZE_SYMBOLS:
                add_special_position(special_positions, index, another_index, another_value)
    
    return special_positions


def get_current_position(maze_array):
    for index, value in enumerate(maze_array):
        for another_index, another_value in enumerate(value):
            if another_value == PLAYER:
                return index, another_index


def print_headers_and_maze(maze_name, maze_array):
    os.system("clear")
    print_rules()
    print("----------")
    print(f"Maze: {name_without_extension(maze_name)}")
    print("----------")
    print_maze(maze_array)


def print_maze(maze_array):
    for row in maze_array:
        print(*row)


def move(x_position, y_position, maze, previous_symbol, special_positions, x_initial_position, y_initial_position):
    while True:
        action = getch().upper()

        if action in VALID_ACTIONS:
            return execute_action(action, x_position, y_position, maze, previous_symbol, special_positions, x_initial_position, y_initial_position)


def execute_action(action, x_position, y_position, maze, previous_symbol, special_positions, x_initial_position, y_initial_position):
    if action == 'Q':
        os.system("clear")
        sys.exit(0)

    if action == 'W':
        return go_up(x_position, y_position, maze, previous_symbol, special_positions)

    if action == 'S':
        return go_down(x_position, y_position, maze, previous_symbol, special_positions)

    if action == 'A':
        return go_left(x_position, y_position, maze, previous_symbol, special_positions)

    if action == 'D':
        return go_right(x_position, y_position, maze, previous_symbol, special_positions)


def can_move(x, y, maze):
    if x < 0 or y < 0 or x > len(maze) or y > len(maze[x]):
        return False

    return maze[x][y] != WALL


def go_up(x_position, y_position, maze, prev_position_symbol, special_positions):
    if can_move(x_position - 1, y_position, maze):
        x_position = x_position - 1
        maze[x_position + 1][y_position] = prev_position_symbol
        prev_position_symbol = maze[x_position][y_position]
        maze[x_position][y_position] = PLAYER
        x_position, y_position = move_if_special_symbol(prev_position_symbol, maze, x_position, y_position, special_positions)

    return prev_position_symbol, x_position, y_position


def go_down(x_position, y_position, maze, prev_position_symbol, special_positions):
    if can_move(x_position + 1, y_position, maze):
        x_position = x_position + 1
        maze[x_position - 1][y_position] = prev_position_symbol
        prev_position_symbol = maze[x_position][y_position]
        maze[x_position][y_position] = PLAYER
        x_position, y_position = move_if_special_symbol(prev_position_symbol, maze, x_position, y_position, special_positions)

    return prev_position_symbol, x_position, y_position


def go_left(x_position, y_position, maze, prev_position_symbol, special_positions):
    if can_move(x_position, y_position - 1, maze):
        y_position = y_position - 1
        maze[x_position][y_position + 1] = prev_position_symbol
        prev_position_symbol = maze[x_position][y_position]
        maze[x_position][y_position] = PLAYER
        x_position, y_position = move_if_special_symbol(prev_position_symbol, maze, x_position, y_position, special_positions)

    return prev_position_symbol, x_position, y_position


def go_right(x_position, y_position, maze, prev_position_symbol, special_positions):
    if can_move(x_position, y_position + 1, maze):
        y_position = y_position + 1
        maze[x_position][y_position - 1] = prev_position_symbol
        prev_position_symbol = maze[x_position][y_position]
        maze[x_position][y_position] = PLAYER
        x_position, y_position = move_if_special_symbol(prev_position_symbol, maze, x_position, y_position, special_positions)

    return prev_position_symbol, x_position, y_position


def move_if_special_symbol(prev_position_symbol, maze, x_position, y_position, special_positions):
    if prev_position_symbol not in MAZE_SYMBOLS:
        move_to = special_positions[prev_position_symbol][0]
        if special_positions[prev_position_symbol][0] == (x_position, y_position):
            move_to = special_positions[prev_position_symbol][1]
        
        maze[x_position][y_position] = prev_position_symbol
        x_position = move_to[0]
        y_position = move_to[1]
        maze[x_position][y_position] = PLAYER

    return x_position, y_position


def name_without_extension(filename):
    return filename.split(".")[0]


def reach_exit_maze(prev_position_symbol):
    return prev_position_symbol == FINISH


def get_maze_from_file(maze_file_name):
    maze = []

    with open(f"mazes/{maze_file_name}") as f:
        content = f.readlines()

    maze_content = [x.strip().replace('.', ' ') for x in content]
    maze.extend(list(c) for c in maze_content)
    
    return maze


def print_rules():
    """ The rules of magic-maze (ascii edition)"""
    print("The goal is to reach the $")
    print("- use 'W' to move up")
    print("- use 'S' to move down")
    print("- use 'A' to move left")
    print("- use 'D' to move right")
    print("- use 'Q' to quit")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Only one argument is valid, the maze (<maze_name>.txt for example)")
        exit()

    maze = sys.argv[1] if len(sys.argv) == 2 else 'test_maze.txt'

    new_game(maze)
