# GUI.py
import sys
import math
import time
import pygame
import copy
import random
import mosaicSolver

random.seed(time.time())
pygame.font.init()

SOLUTION_EMPTY = 0
SOLUTION_BLACK = 1

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


def draw_window(surface, board):
    surface.fill((255, 255, 255))
    # Draw grid and board
    board.draw(surface)


def main():

    size = 10
    quantity = 9
    prob = 0.5
    num_inst = 5
    fname = "instances/"

    # size = int(sys.argv[1])
    # quantity = int(sys.argv[2])
    # prob = float(sys.argv[3])
    # num_inst = int(sys.argv[4])
    # fname = sys.argv[5]


    for i in range(num_inst):

        solver = mosaicSolver.Solver(size )

        surface = pygame.display.set_mode((540,540))
        # List of Black or Empty Squares
        #sol = generateRandomSolution(size, prob)
        # List of Numbers indicating Neighbors
        #board = generateBoardFromSolution(size, sol, quantity)
        board = solver.create_board(quantity, 6+ i)

        grid = Grid(size, board, 540, 540)


        sol = solver.get_solutions(board)

        draw_window(surface, grid)
        pygame.image.save(surface, fname+"instance_"+str(i)+".png")

        with open(fname+"instance_"+str(i)+".txt", 'w') as file:
            for row in sol:
                file.write(' '.join([str(i) for i in row]) + '\n')

        success = True

main()
pygame.quit()

