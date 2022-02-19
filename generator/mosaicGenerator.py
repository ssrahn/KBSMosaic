# GUI.py
import sys
import math
import time
import pygame
import random
random.seed(time.time())
pygame.font.init()

SOLUTION_EMPTY = 0
SOLUTION_BLACK = 1
SOLUTION_RESTRICTED = -1

class Grid:

    def __init__(self, size, board, width, height):
        self.size = size
        self.board = board
        self.cubes = [[Cube(self.board[i][j], i, j, width, height, size) for j in range(size)] for i in range(size)]
        self.width = width
        self.height = height

    def draw(self, win):
        # Draw Grid Lines
        gap = self.width / self.size
        for i in range(self.size+1):
            pygame.draw.line(win, (0,0,0), (0, i*gap), (self.width, i*gap), 1)
            pygame.draw.line(win, (0,0,0), (i*gap, 0), (i*gap, self.height), 1)

        # Draw Cubes
        for i in range(self.size):
            for j in range(self.size):
                self.cubes[i][j].draw(win)


class Cube:
    def __init__(self, value, row, col, width ,height, board_size):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False
        self.board_size = board_size

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / self.board_size
        x = self.col * gap
        y = self.row * gap

        if not(self.value == -1):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

    def set(self, val):
        self.value = val


def generateRandomSolution(size, prob):
    sol = [[0 for j in range(size)] for i in range(size)]

    for x in range(size):
        for y in range(size):
            if random.random() <= prob:
                sol[x][y] = 1
    return sol


def generateBoardFromSolution(size, solution, quant):
    board = [[-1 for j in range(size)] for i in range(size)]
    covered = [[0 for j in range(size)] for i in range(size)]
    
    count = 0
    while(count < quant):
        x = math.ceil(random.random() * size) - 1
        y = math.ceil(random.random() * size) - 1
        if board[x][y] != -1:
            continue
        number = 0
        for j in range(9):
            curr_x = (x-1)+j%3
            curr_y = (y-1)+int(j/3)
            if curr_x < 0 or curr_y < 0 or curr_x > size-1 or curr_y > size-1:
                continue
            covered[curr_x][curr_y] = 1
            number += solution[curr_x][curr_y]
        board[x][y] = number
        count += 1
    
    for x in range(size):
        for y in range(size):
            if covered[x][y] != 1:
                number = 0
                for j in range(9):
                    curr_x = (x-1)+j%3
                    curr_y = (y-1)+int(j/3)
                    if curr_x < 0 or curr_y < 0 or curr_x > size-1 or curr_y > size-1:
                        continue
                    covered[curr_x][curr_y] = 1
                    number += solution[curr_x][curr_y]
                board[x][y] = number
                
    return board

def print_board(board):
    for row in board:
        s = ""
        for col in row:
            s += str(col) + "   "
        print(s)

def get_square_value(solution, x,y, board_size):
    # Check for game board boundary
    if x < 0 or y < 0 or x >= board_size or y >= board_size:
        return -2
    return solution[x][y]


def number_to_9x9(number):
    # Converts number (0 to 8) to a 3x3 Grid position
    # 0 is (-1,-1) and 8 is (1,1)
    x =   int(number/3) -1
    ret = [0,0]
    ret[0] = x
    ret[1] = (number%3) - 1
    return ret

def set_square(x,y, solution, value, board_size):
    # Check for game board boundary
    if x < 0 or y < 0 or x >= board_size or y >= board_size:
        return False

    # We can not restrict already set black squares
    if value == SOLUTION_RESTRICTED and solution[x][y] == SOLUTION_BLACK:
        #print(str(x) + "  " + str(y) + " couldnt set to restricted, because already black")
        return False

    # We can not set a square to Black if it restricted
    if value == SOLUTION_BLACK and solution[x][y] == SOLUTION_RESTRICTED:
        #print(str(x) + "  " + str(y) + " couldnt set to black, because restricted")
        return False

    solution[x][y] = value
    return True

def restrict_around(x,y, solution, board_size):
    set_square(x - 1, y - 1,solution, SOLUTION_RESTRICTED,board_size)
    set_square(x - 1, y,solution, SOLUTION_RESTRICTED,board_size)
    set_square(x - 1, y + 1,solution, SOLUTION_RESTRICTED,board_size)

    set_square(x + 1, y - 1,solution, SOLUTION_RESTRICTED,board_size)
    set_square(x + 1, y,solution, SOLUTION_RESTRICTED,board_size)
    set_square(x + 1, y + 1,solution, SOLUTION_RESTRICTED,board_size)

    set_square(x, y - 1,solution, SOLUTION_RESTRICTED,board_size)
    set_square(x, y,solution, SOLUTION_RESTRICTED,board_size)
    set_square(x, y + 1,solution, SOLUTION_RESTRICTED,board_size)

def get_black_square_amount(solution, x, y, board_size):
    amount = 0

    if y < board_size - 1:
        amount += solution[x][y + 1]
    amount += solution[x][y]
    if y > 0:
        amount += solution[x][y - 1]
    if y < board_size - 1 and x < board_size - 1:
        amount += solution[x + 1][y + 1]
    if x < board_size - 1:
        amount += solution[x + 1][y]
    if y > 0 and x < board_size - 1:
        amount += solution[x + 1][y - 1]
    if y  < board_size - 1 and x > 0:
        amount += solution[x - 1][y + 1]
    if x > 0:
        amount += solution[x - 1][y]
    if y > 0 and x > 0:
        amount += solution[x - 1][y - 1]


    return amount


def satisfy_around(satisfaction, x,y, board_size):
    for i in range(0,9):
        pos = number_to_9x9(i)

        cur_value = get_square_value(satisfaction, x + pos[0], y + pos[1], board_size)
        if cur_value == 0:
            # Illegal State!
            return False
        elif cur_value != -2:
            satisfaction[pos[0] + x][pos[1] +y] -= 1
    return True

def is_legal_state(board,solution,board_size):
    # Solution contains given set of black / empty squares
    # Board contains restriction numbers

    # Similar to Valid state, but returns False only if count of squares exceeds board number
    y = 0
    x = 0
    for row in board:
        for number in row:
            if number != 0:
                # We have a restriction
                # Add Up all Black Squares in a 3x3 Square around Restriction Number
                count_of_squares = get_black_square_amount(solution, x, y, board_size)

                # Check for Number Missmatch
                # Ignore if the board restriction number is -1 (no restriction)
                if count_of_squares > board[x][y] and board[x][y] != -1:
                    return False
            # Increment Column
            y += 1

        # Increment Row
        y = 0
        x += 1

    return True


def is_valid_solution(board, solution, board_size):
    # Solution contains given set of black / empty squares
    # Board contains restriction numbers

    y = 0
    x = 0
    for row in board:
        for number in row:
            if number != 0:
                # We have a restriction
                # Add Up all Black Squares in a 3x3 Square around Restriction Number
                count_of_squares = get_black_square_amount(solution, x, y, board_size)

                # Check for Number Missmatch
                # Ignore if the board restriction number is -1 (no restriction)
                if count_of_squares != board[x][y] and board[x][y] != -1:
                    return False
            # Increment Column
            y += 1

        # Increment Row
        y = 0
        x += 1


    return True

def get_smallest_unsatisfied_number(satisfaction):
    # Coordinates of smallest unsatisfied number
    x = -1
    y = -1
    # Iterators
    _x = 0
    _y = 0
    # Value of smallest unsatisfied number
    value = 10
    for row in satisfaction:
        _y = 0
        for col in row:
            # Check if not yet satisfied
            if col > 0:
                # Check if value is smaller than previous smallest value
                if col < value:
                    # Remember coordinates
                    x = _x
                    y = _y

                    # Break immediatly, if value is 1 (it cannot be smaller)
                    if col == 1:
                        return [x,y]
                    # Else save value
                    value = col

            _y += 1
        _x += 1
    return [x,y]


def solve_step(solution, satisfaction, board, board_size, x, y):
    # Recursive Solving

    # Start with changing our local Solution
    # Set Square to Black
    # Operation returns false, if out of bounce or Restricted
    lead_to_valid_board = set_square(x, y, solution, SOLUTION_BLACK, board_size)
    if lead_to_valid_board:
        # New Black Square was legal and valid
        # Satisfy 9x9 surroundings
        lead_to_valid_board = satisfy_around(satisfaction,x,y,board_size)

        #print("Current Solution: ")
        # Debug print solution
        #print_board(solution)
        #print("Current Satisfaction: ")
        # Debug print satisfaction
        #print_board(satisfaction)

    # Recursion ancor:
    # Adding a black square at (x,y) lead to an invalid board
    if not lead_to_valid_board:
        return False

    # Recurse

    # Get smallest unsatisfied number
    pos = get_smallest_unsatisfied_number(satisfaction)

    # Recursion ancor:
    # If no smallest unsatisfied number has been found, every number should be satisfied and we should have a valid solution
    if pos[0] == -1 and pos[0] == -1:
        print("Done")
        # Debug print solution
        print_board(solution)
        return True

    # Add a black square at each position in the 3x3 area around smallest number
    for i in range(0, 9):
        # Offset
        new_pos = number_to_9x9(i)
        new_pos[0] += pos[0]
        new_pos[1] += pos[1]

        if new_pos[0] != pos[0] and new_pos[1] != pos[1]:
            solve_step(solution, satisfaction, board, board_size, new_pos[0], new_pos[1])
    return False




def solve(board, board_size):

    solution = [[0 for j in range(board_size)] for i in range(board_size)]
    # 0 for satisfied, 1+ for number of unsatisfied squares, -1 for don't care
    satisfaction =  [[0 for j in range(board_size)] for i in range(board_size)]

    # Debug print board
    print_board(board)

    print("")
    print("solve:")
    print("")

    x = 0
    y = 0

    # First Restrict all Fields around a 0
    for row in board:
        for col in row:
            if col == 0:
                restrict_around(x,y, solution, board_size)
                satisfaction[x][y] = 0
            elif col > 0:
                satisfaction[x][y] = col
            else:
                satisfaction[x][y] = -1
            y += 1
        x += 1
        y = 0

    # Debug print solution

    print_board(solution)

    # Manually do first Solve Recursion

    # Get smallest unsatisfied number
    pos = get_smallest_unsatisfied_number(satisfaction)

    # Recursion Ancer:
    # If no smallest unsatisfied number has been found, every number should be satisfied and we should have a valid solution
    if pos[0] == -1 and pos[0] == -1:
        return True

    # Add a black square at each position in the 3x3 area around smallest number
    for i in range(0, 9):
        # Offset
        new_pos = number_to_9x9(i)
        new_pos[0] += pos[0]
        new_pos[1] += pos[1]

        if new_pos[0] != pos[0] and new_pos[1] != pos[1]:
            solve_step(solution, satisfaction, board, board_size, new_pos[0], new_pos[1])

    return True

def draw_window(surface, board):
    surface.fill((255,255,255))
    # Draw grid and board
    board.draw(surface)


def main():

    size = 10
    quantity = 35
    prob = 0.35
    num_inst = 1
    fname = "instances"

    # size = int(sys.argv[1])
    # quantity = int(sys.argv[2])
    # prob = float(sys.argv[3])
    # num_inst = int(sys.argv[4])
    # fname = sys.argv[5]


    for i in range(num_inst):
        surface = pygame.display.set_mode((540,540))
        # List of Black or Empty Squares
        sol = generateRandomSolution(size, prob)
        # List of Numbers indicating Neighbors
        board = generateBoardFromSolution(size, sol, quantity)
        grid = Grid(size, board, 540, 540)

        solve(board, size)

        draw_window(surface, grid)
        pygame.image.save(surface, fname+"instance_"+str(i)+".png")
        
        with open(fname+"instance_"+str(i)+".txt", 'w') as file:
            for row in sol:
                file.write(' '.join([str(i) for i in row]) + '\n')

main()
pygame.quit()

