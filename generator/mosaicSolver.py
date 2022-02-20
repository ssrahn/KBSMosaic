import math
import random
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
    def __init__(self, size):
        # 1 for Black Box, 0 for Free Box, Negative for Restricted Box (the more negative it is, the more nearby Numbers restrict this block)
        self.constructed_solution = [[0 for j in range(size)] for i in range(size)]
        self.clues =  [[0 for j in range(size)] for i in range(size)]
        self.original_board = [[0 for j in range(size)] for i in range(size)]
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

    def print_final_clue(self):
        for row in self.clues:
            s = ""
            for col in row:
                value = col
                if value < 0:
                    value = 0
                s += str(value) + "  "
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



    def solve_step(self, x,y, depth):

        # Occupy Block at x,y
        valid = self.set_black(x,y)

        # If the operation was not valid, nothing has been changed and we can safely return to upper recursion level
        if not valid:
            return 0

        #print("Set " + str(x) + " " + str(y) + " depth: " + str(depth))
        # Get new Unsatisfied Clue
        clue = self.get_smallest_unsatisfied_number()

        # Check if clue exists
        if clue[0] == -1 and clue[1] == -1 :
            # No Further Clues found => Probably a solution

            # Validate
            valid = self.valid_solution()

            if valid:
                # Create quick stupid hash
                _hash = 0
                c = 0
                for row in self.constructed_solution:
                    for col in row:
                        c += 1
                        if col >= 0:
                            _hash = (_hash + col * 10 * c * c)
                if self.found_solution_hash == 0:
                    #print("Found new Solution")
                    self.found_solution_hash = _hash
                    #self.print_final_solution()

                    self.found_solutions += 1
                elif self.found_solution_hash != _hash:
                    #print("Found a second Solution")
                    #self.print_final_solution()
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

            value = self.solve_step(_x,_y, depth + 1)

            if value == -1:
                # A second solution has been found!
                return -1
            else:
                child_solutions += value


        # Reverse Occupation
        self.set_white(x, y)

        return child_solutions






    def restrict_around(self,x,y):
        #print("Restrict")
        for i in range(0, 9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]

            value = self.get_solution_at(_x,_y)
            if value == 0:
                self.constructed_solution[_x][_y] = -1

    def fill_around(self,x,y):
       #print("Fill")
        for i in range(0, 9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]

            value = self.get_solution_at(_x,_y)
            if value == 0:
                self.constructed_solution[_x][_y] = 1


    def number_of_black_squares_at(self, x,y):
        # Add Up all Black Squares in a 3x3 Square around Restriction Number
        amount_of_squares = 0
        for i in range(0, 9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]
            if self.get_solution_at(_x, _y) == 1:
                amount_of_squares += 1
        return amount_of_squares

    def number_of_white_squares_at(self, x,y):
        # Add Up all White Squares in a 3x3 Square around Restriction Number
        amount_of_squares = 0
        for i in range(0, 9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]
            if self.get_solution_at(_x, _y) == 0:
                amount_of_squares += 1
        return amount_of_squares

    def number_of_restricted_squares_at(self, x,y):
        # Add Up all Restricted Squares in a 3x3 Square around Restriction Number
        amount_of_squares = 0
        for i in range(0, 9):
            pos = number_to_9x9(i)
            _x = x + pos[0]
            _y = y + pos[1]
            if self.get_solution_at(_x, _y) == -1:
                amount_of_squares += 1
        return amount_of_squares

    def solve_restrict(self):
        made_change = False
        x = 0
        # Restricts possible free box fields, if a nearby number is already satisfied
        for row in self.original_board:
            y = 0
            for col in row:
                num_squares = self.number_of_black_squares_at(x,y)

                if num_squares == col:
                    # Restrict ALL nearby solution fields
                    for i in range(0, 9):
                        pos = number_to_9x9(i)
                        _x = x + pos[0]
                        _y = y + pos[1]

                        value = self.get_solution_at(_x, _y)
                        if value == 0:
                            made_change = True
                            self.constructed_solution[_x][_y] = -1

                y += 1
            x += 1
        return made_change

    def solve_fill(self):
        made_change = False
        x = 0
        # Whenever a number demands x amount of fields to be filled and it has exactly that amount of possible free room, we fill the entire room with black squares
        for row in self.original_board:
            y = 0
            for col in row:
                whites = self.number_of_white_squares_at(x,y)
                blacks = self.number_of_black_squares_at(x,y)

                if col - blacks == whites and col - blacks != 0:
                    # Fill ALL nearby solution fields
                    for i in range(0, 9):
                        pos = number_to_9x9(i)
                        _x = x + pos[0]
                        _y = y + pos[1]

                        value = self.get_solution_at(_x, _y)
                        if value == 0:
                            made_change = True
                            self.constructed_solution[_x][_y] = 1

                y += 1
            x += 1
        return made_change

    def iterate_solution(self):
        iterate = True

        while iterate:
            iterate = False
            change = self.solve_restrict()
            change = change or self.solve_fill()
            iterate = change

        return True

    def throwaway_recursion(self):
        change = False
        while change:
            if not change and not self.valid_solution():
                # Get new Unsatisfied Clue
                clue = self.get_smallest_unsatisfied_number()

                copys = copy.deepcopy(self.constructed_solution)

                # Recursively add new black blocks
                for i in range(0, 9):
                    pos = number_to_9x9(i)
                    _x = clue[0] + pos[0]
                    _y = clue[1] + pos[1]

                    made_change = False
                    # Occupy Block at x,y
                    if self.get_solution_at(_x, _y) == 0:
                        self.constructed_solution[_x][_y] = 1

                        # Restrict ALL nearby solution fields
                        for i in range(0, 9):
                            res_pos = number_to_9x9(i)
                            res_x = _x + res_pos[0]
                            res_y = _y + res_pos[1]

                            value = self.get_solution_at(res_x, res_y)
                            if value != 1 and value != -10:
                                made_change = True
                                self.constructed_solution[res_x][res_y] = -1

                        value = self.iterate_solution()

                        if value == True:
                            # A second solution has been found!
                            return True

                    self.constructed_solution = copys

            elif not change and self.valid_solution():
                break;

    def get_solutions(self, board):

        #clue = self.get_smallest_unsatisfied_number()
        self.clue = copy.deepcopy(board)
        self.original_board = board
        # Remember Child Solutions
        #child_solutions = 0

        # Recursively add new black blocks
        #for i in range(0,9):
        #    pos = number_to_9x9(i)
        #    _x = clue[0] + pos[0]
        #    _y = clue[1] + pos[1]

        #    child_solutions += self.solve_step(_x,_y, 0)

        self.iterate_solution()

        # Validate
        #print(self.valid_solution())

        #self.print_final_solution()

        x = 0

        for row in self.constructed_solution:
            y = 0
            for col in row:
                value = col
                if value < 0:
                    self.constructed_solution[x][y] = 0
                y += 1
            x += 1

        return self.constructed_solution

    def update_board_clues(self):
        x = 0
        for row in self.clues:
            y = 0
            for col in row:
                # Get Amount of White boxes
                whites = self.number_of_white_squares_at(x,y)
                # Get Amount of Black boxes
                blacks = self.number_of_black_squares_at(x,y)
                # Get Current Clue
                clue = self.clues[x][y]
                # A negative clue is already chosen as part of the puzzle set
                # Therefore we only want to update positive numbers
                if clue >= 0:
                    # This is the maximum amount of black boxes we could have around this number
                    self.clues[x][y] = whites + blacks

                y += 1
            x += 1

    def pick_clue_at(self, x,y):
        # Negative number means this clue is already picked
        if self.clues[x][y] < 0:
            return

        # Get Amount of Restricted boxes
        restricted = self.number_of_restricted_squares_at(x, y)
        # Get Amount of Black boxes
        blacks = self.number_of_black_squares_at(x, y)

        do_restriction = restricted <= blacks

        # We want to encourage taking the lowest number (higher numbers are easy)
        take_higher_number = random.random() < 0.2

        #print("Restricted Amount: " + str(restricted) + " Black Amount: " + str(blacks) + " We want to pick higher: " + str(take_higher_number))
        if take_higher_number:
            # we do the opposite of what we would usually do
            do_restriction = not do_restriction

        # If Whites are the lowest number, we pick it, meaning
        if do_restriction:
            # Restrict all surrounding squares
            self.restrict_around(x,y)
        else:
            # Fill all surrounding with black boxes
            self.fill_around(x,y)

        # Set Clue
        self.clues[x][y] = -self.number_of_black_squares_at(x,y)

    def get_unchosen_clue(self, border_discouragement):

        # Border Discouragement gradually decreases from 1 to 0
        # At 1, the entire board can be chosen from
        # At 0, only the middle is taken into consideration

        # The higher Board Wave is, the move we move inward
        border_wave = 1 - border_discouragement * math.pi

        border_wave = (math.sin(border_wave) + 1) /2

        inner = math.floor((self.board_size -1)/2 * border_wave )
        outer = math.floor((self.board_size -1) - (self.board_size -1)/2 * border_wave )

        while_breaker = 5000
        while while_breaker > 0:
            while_breaker -= 1

            picked_x = random.randint(inner, outer)
            picked_y = random.randint(inner, outer)

            picked_value = self.clues[picked_x][picked_y]

            if picked_value > 0 :
                return [picked_x,picked_y]
        return [0,0]


    def choose_good_clue_position(self, border_discouragement):
        # Picks x Random Positions on the board and evaluates their maximum and minimum Number value

        amount_of_picks = random.randint(3,6)

        start_clue = self.get_unchosen_clue(border_discouragement)

        start_value = self.number_of_black_squares_at(start_clue[0], start_clue[1]) + self.number_of_white_squares_at(start_clue[0], start_clue[1])


        for i in range(0, amount_of_picks):
            other_clue = self.get_unchosen_clue(border_discouragement)

            other_value = self.number_of_black_squares_at(other_clue[0], other_clue[1]) + self.number_of_white_squares_at(other_clue[0], other_clue[1])

            if other_value < start_value:
                start_clue = other_clue
                start_value = other_value

            #print(str(other_clue) + " This Value is : " + str(other_value))

        if start_value != -10:
            #print("Picking clue at " + str(start_clue[0]) + " " + str(start_clue[1]) + " with value " + str(start_value))
            self.pick_clue_at(start_clue[0], start_clue[1])
            return True

        return False



    def create_board(self, amount_of_clues, seed = 0):
        self.constructed_solution = [[0 for j in range(self.board_size)] for i in range(self.board_size)]
        self.clues = [[0 for j in range(self.board_size)] for i in range(self.board_size)]

        random.seed(seed)

        self.update_board_clues()

        clues_left = amount_of_clues

        while_breaker = 5000
        while while_breaker > 0 and clues_left >= 0:
            while_breaker -= 1
            # Here random Clues are added to the board
            if self.choose_good_clue_position(clues_left / amount_of_clues):
                clues_left -= 1

        # Employ the 9x9 Empty area rule
        # => There ought not to be any 9x9 area in our puzzle that isn't covered by any clue

        # Fill matrix with -1 where ever a clue is in a 9x9 area
        empty_squares = [[0 for j in range(self.board_size)] for i in range(self.board_size)]
        x = 0

        for row in self.clues:
            y = 0
            for col in row:
                if col <= 0:
                    for i in range(0, 9):
                        pos = number_to_9x9(i)
                        _x = x + pos[0]
                        _y = y + pos[1]

                        if not self.is_out_of_bounds(_x, _y):
                            empty_squares[_x][_y] = -1
                y += 1
            x += 1
        #self.print_board(empty_squares)

        x = 0
        # Where ever there is a 0, we need put a clue around
        for row in empty_squares:
            y = 0
            for col in row:
                if col == 0:
                    # Randomize x and y position for niceness
                    # The value is clamped as not to reach out of bounds
                    rand_x = max(0, min(random.randint(-1, 1) + x, self.board_size -1))
                    rand_y = max(0, min(random.randint(-1, 1) + y, self.board_size -1))

                    # Pick Clue here
                    self.pick_clue_at(rand_x, rand_y)

                    # Restrict Further
                    for i in range(0, 9):
                        pos = number_to_9x9(i)
                        _x = rand_x + pos[0]
                        _y = rand_y + pos[1]

                        if not self.is_out_of_bounds(_x, _y):
                            empty_squares[_x][_y] = -1

                y += 1
            x += 1


        x = 0
        # Cleanup Clue Board
        for row in self.clues:
            y = 0
            for col in row:
                value = col
                if value <= 0:
                    self.clues[x][y] = - value
                else:
                    self.clues[x][y] = -1
                y += 1
            x += 1
        return self.clues


