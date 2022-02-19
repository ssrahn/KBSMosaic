
import copy


def number_to_9x9(number):
    # Converts number (0 to 8) to a 3x3 Grid position
    # 0 is (-1,-1) and 8 is (1,1)
    x = int(number / 3) - 1
    ret = [0, 0]
    ret[0] = x
    ret[1] = (number % 3) - 1
    return ret

class Solver:
    def __init__(self, size, board):
        # 1 for Black Box, 0 for Free Box, Negative for Restricted Box (the more negative it is, the more nearby Numbers restrict this block)
        self.constructed_solution = [[0 for j in range(size)] for i in range(size)]
        self.clues = copy.deepcopy(board)
        self.original_board = board
        self.board_size = size
        self.found_solutions = 0

        self.found_solution_hash = 0

        x = 0
        y = 0
        # Restrict 0-Clues
        for row in self.clues:
            y = 0
            for col in row:
                if col == 0:
                    for i in range(0,9):
                        pos = number_to_9x9(i)
                        pos[0] += x;
                        pos[1] += y;
                        if not self.is_out_of_bounds(pos[0],pos[1]):
                            self.constructed_solution[pos[0]][pos[1]] = -1
                y += 1
            x += 1

    def print_board(self, board):
        for row in board:
            s = ""
            for col in row:
                s += str(col) + "   "
            print(s)

    def print_final_solution(self):
        for row in self.constructed_solution:
            s = ""
            for col in row:
                value = col
                if value < 0:
                    value = 0
                s += str(value) + "  "
            print(s)

    def valid_solution(self):
        # Checks if current constructed Solution is valid

        y = 0
        x = 0
        for row in self.original_board:
            for number in row:
                if number != 0:
                    # We have a restriction
                    # Add Up all Black Squares in a 3x3 Square around Restriction Number
                    count_of_squares = 0
                    for i in range(0, 9):
                        pos = number_to_9x9(i)
                        _x = x + pos[0]
                        _y = y + pos[1]
                        if self.get_solution_at(_x,_y) == 1:
                            count_of_squares += 1

                    # Check for Number Missmatch
                    # Ignore if the board restriction number is -1 (no restriction)
                    if count_of_squares != self.original_board[x][y] and self.original_board[x][y] != -1:
                        return False
                # Increment Column
                y += 1

            # Increment Row
            y = 0
            x += 1

        return True

    def get_solution_at(self,x,y):
        if self.is_out_of_bounds(x,y):
            return -10
        else:
            return self.constructed_solution[x][y]

    def get_clue(self, x,y):
        if self.is_out_of_bounds(x,y):
            return -10
        else:
            return self.clues[x][y]

    def set_clue(self, x,y, value):
        if self.is_out_of_bounds(x,y):
            return -10
        else:
            if value < -1:
                value = -1
            self.clues[x][y] = value
            return value


    def is_out_of_bounds(self, x,y):
        return (x < 0 or y < 0 or x >= self.board_size or y >= self.board_size)

    def is_restricted_at(self, x,y):
        return self.constructed_solution[x][y] == -1

    def restrict_at(self,x,y):
        if self.is_out_of_bounds(x,y):
            return  False
        else:
            # We do not want to restrict already occupied Fields
            if(self.constructed_solution[x][y] != 1):
                self.constructed_solution[x][y] -= 1

    def free_at(self,x,y):
        if self.is_out_of_bounds(x,y):
            return False
        else:
            # We do not want to free Fields that aren't restricted in the first place
            if(self.constructed_solution[x][y] < 0):
                self.constructed_solution[x][y] += 1

    def set_white(self, x, y):
        # Done when we want to reverse a Black box operation

        already_blank = self.get_solution_at(x,y) == 0
        if already_blank :
            return

        # Set Square a x,y to blank
        self.constructed_solution[x][y] = 0

        # Each Surrounding Number Square now has 1 Black Square less than before, so their restrictions will change
        for i in range(0,9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]

            # Add one to the Number Square, if it is not empty (negative)
            if not self.is_out_of_bounds(_x,_y):
                value = self.get_clue(_x,_y)
                if value >= 0:
                    self.set_clue(_x,_y, value + 1)

                    # If the Value is 0, it will now flank to 1 and absolve nearby Restrictions from this black box
                    if value == 0:
                        for j in range(0, 9):
                            res_pos = number_to_9x9(j)
                            res_x = _x + res_pos[0]
                            res_y = _y + res_pos[1]
                            self.free_at(res_x,res_y)



    def set_black(self, x, y):
        # Check for Legality first:
        # We can not set a block to black twice
        already_black = self.get_solution_at(x,y)
        if already_black:
            return False

        # If square surrounding this Black box already has a Restriction of 0 (they won't allow any block near them) we can not add this black box
        illegal = False
        for i in range(0,9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]

            illegal = illegal or self.get_clue(_x,_y) == 0

        if illegal:
            return False

        # Set Square a x,y to black
        self.constructed_solution[x][y] = 1

        # Each Surrounding Number Square now has 1 Black Square around in its vicinity, so their restrictions might change
        for i in range(0,9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]

            # Since we checked for legality first, the new value is guaranteed not to go negative
            if not self.is_out_of_bounds(_x,_y):
                self.set_clue(_x,_y, self.get_clue(_x,_y) - 1)

                # Restrict Solution Fields that are near a 0-clue
                if self.clues[_x][_y] == 0:
                    for j in range(0,9):
                        res_pos = number_to_9x9(j)
                        res_x = _x + res_pos[0]
                        res_y = _y + res_pos[1]
                        self.restrict_at(res_x, res_y)
        return True


    def get_smallest_unsatisfied_number(self):
        # Coordinates of smallest unsatisfied number
        x = -1
        y = -1

        # Iterators
        _x = 0
        _y = 0

        # Value of smallest unsatisfied number, default is 10 ( should be biggest possible )
        value = 10

        for row in self.clues:
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
                            return [x, y]
                        # Else save value
                        value = col

                _y += 1
            _x += 1
        return [x, y]



    def solve_step(self, x,y):

        # Occupy Block at x,y
        valid = self.set_black(x,y)

        # If the operation was not valid, nothing has been changed and we can safely return to upper recursion level
        if not valid:
            return 0

        # Get new Unsatisfied Clue
        clue = self.get_smallest_unsatisfied_number()

        # Check if clue exists
        if clue[0] == -1 and clue[1] == -1 :
            # No Further Clues found => Probably a solution

            # Validate
            valid = self.valid_solution();

            if valid:
                # Create quick stupid hash
                _hash = 0
                for row in self.constructed_solution:
                    for col in row:
                        _hash = hash(_hash + col)

                if self.found_solution_hash == 0:
                    print("Found new Solution")
                    self.found_solution_hash = _hash
                    self.print_final_solution()

                    self.found_solutions += 1
                #elif self.found_solution_hash == _hash:
                    #print("Found duplicate Solution")
                else:
                    print("Found a second Solution")
                    self.print_final_solution()
                    self.found_solutions += 1
                    return -1

            # Reverse Occupation
            self.set_white(x, y)
            if valid:
                return 1
            else:
                return 0

        # Remember Child Solutions
        child_solutions = 0

        # Recursively add new black blocks
        for i in range(0,9):
            pos = number_to_9x9(i)
            _x = clue[0] + pos[0]
            _y = clue[1] + pos[1]

            value = self.solve_step(_x,_y)

            if value == -1:
                # A second solution has been found!
                return -1
            else:
                child_solutions += value


        # Reverse Occupation
        self.set_white(x, y)

        return child_solutions


    def get_solutions(self):
        clue = self.get_smallest_unsatisfied_number()

        # Remember Child Solutions
        child_solutions = 0

        # Recursively add new black blocks
        for i in range(0,9):
            pos = number_to_9x9(i)
            _x = clue[0] + pos[0]
            _y = clue[1] + pos[1]

            child_solutions += self.solve_step(_x,_y)


        return self.found_solutions
