# -----------------------------------------------------------------#
# Author: Jeffrey Chu
# Date: 3/10/2021
# Description: Created a program that plays Janggi, a Korean variant on Chinese Chess. Players are Blue and Red
#              and Blue goes first. Players move by calling the make_move method in the JanggiGame class and
#              input a move_from and move_to destination via a string through algebraic notation, with rows
#              labeled 1-10 and columns labeled a-i. Players can pass the turn by inputting the same move_from
#              and move to strings. Has methods that can return the game state and whether a player is in check,
#              or checkmate.
#
#              Does not implement special rules, draws, position repetition, any miscellaneous rules, or any special
#              mechanisms for figuring out who can start the game.
# -----------------------------------------------------------------#

# ------------------------------PIECES-----------------------------------#

class ChessPiece:
    '''
    The chess piece class which works for all the pieces, will need to communicate with the other piece classes
    the JanggiGame class, and possibly the board class. It will need to do so so that pieces and
    information from pieces can be accessed moves can be made within the game.

    This class will setup the basics of the chess pieces to inherit from. It will determine possible moves,
    possible captures, and whether a move is valid or not. It will also provide get methods for piece names and
    color for players.
    '''

    def __init__(self, player, piece_name):
        '''
        init method for the chess piece class that will initialize the data members

        Recieves: takes as parameter which player's piece is being moved and the name of the piece being moved.
        Returns: nothing
        '''

        self._player = player
        self._piece_name = piece_name

        # basic directions for pieces to access
        self._orth = ((1, 0), (0, 1), (-1, 0), (0, -1))
        self._diag = ((-1, -1), (-1, 1), (1, -1), (1, 1))

    def get_piece_name(self):
        '''
        Get method for the name of the piece located on the board. 
        
        Receives: none
        Returns: the piece name
        '''

        return self._piece_name

    def get_player(self):
        '''
        Get method for the color of the player of the piece located on the board. 

        Receives: none
        Returns: the player color of the selected piece
        '''
        
        return self._player


    def possible_moves(self, row_from, col_from, board, color, directions,
                       capturable, x_distance=None, y_distance=None, palace=None):
        '''
        Method that detects the available moves a piece can make from their current location on the board. 
        
        Recieves: row and column, the board object, whose turn it is (color), piece direcitons, 
        whether a move is able to capture another piece. It can also receive default parameters of 
        the maximum row and column distance a piece can move, and the color of the palace the piece is located in.
        
        Returns: a list of coordinates in (y, x) -- row, column -- that a piece is allowed to move to
        '''
    
        coords = []
        occupied = board.get_occupied().values()
        start = (row_from, col_from)
        palace_corners = (0, 3), (0, 5), (2, 3), (2, 5), (7, 3), (7, 5), (9, 3), (9, 5)
        palace_centers = (8, 4), (1, 4)
        palace_directions = directions

        # establishes way to retrieve the opposite color
        if color == 'blue':
            opposite_color = 'red'

        if color == 'red':
            opposite_color = 'blue'

        current_is_in_palace = self.is_in_palace(row_from, col_from, palace)

        # special directions if certain pieces are located within the palace and in specific locations 
        # that allow diagonal movement
        
        if current_is_in_palace and (self.get_piece_name() == "General" or self.get_piece_name() == "Guard" or \
            self.get_piece_name() == "Chariot") and (start in palace_corners or start in palace_centers):

            palace_directions = self._diag + self._orth

        if current_is_in_palace and self.get_piece_name() == "Soldier" and \
                (start in palace_corners or start in palace_centers):

            if palace == 'red':
                palace_directions = (0, -1), (0, 1), (-1, 0), (-1, -1), (-1, 1)

            if palace == 'blue':
                palace_directions = (0, -1), (0, 1), (-1, 0), (1, 1), (-1, 1)

        # determines available moves if the starting location is located within either the red or blue palace
        if current_is_in_palace:
            
            for x_movement, y_movement in palace_directions:
                collision = False
                too_far = False

                row_temp, col_temp = row_from + x_movement, col_from + y_movement

                # while the attempted destination coordinates remain in the board and palace indices
                while self.is_in_board(row_temp, col_temp) and self.is_in_palace(row_temp, col_temp, palace):

                    destination = (row_temp, col_temp)

                    # determines if the attempted move distance is too far allowed by piece movement rules
                    if abs(row_from - row_temp) > y_distance:
                        too_far = True

                    if abs(col_from - col_temp) > x_distance:
                        too_far = True

                    #  if the attempted move runs into another piece of the same color, break the loop
                    if collision is True:
                        break

                    # special rules for the cannon piece that disallow diagonal movement if the center square
                    # of the palace is not occupied
                    if self.get_piece_name() == "Cannon" and palace == 'blue' and (8, 4) not in occupied:
                        return False

                    if self.get_piece_name() == "Cannon" and palace == 'red' and (1, 4) not in occupied:
                        return False

                    # special directions for the cannon piece that allows for diagonal movement in the palace
                    if self.get_piece_name() == "Cannon" and (8, 4) in occupied and start in palace_corners:

                        special_directions = (-2, -2), (2, 2), (-2, 2), (2, -2)
                        obstructed_color = board.get_occupied(color).values()

                        for xx_movement, yy_movement in special_directions:

                            palace_row_temp = row_from + xx_movement
                            palace_col_temp = col_from + yy_movement
                            palace_destination = (palace_row_temp, palace_col_temp)

                            # check that diagonal jump is in the board and is in the palace
                            if self.is_in_board(row_temp, col_temp) and \
                                self.is_in_palace(palace_row_temp, palace_col_temp, color) \
                                    and destination not in obstructed_color:

                                coords.append(palace_destination)

                    # for all other pieces, tests that the attempted destination positions are not occupied 
                    # and that the destination remains in the palace for unique palace movement of pieces
                    if self.get_piece_name() != "Cannon" and destination not in occupied \
                            and too_far is False and self.is_in_palace(row_temp, col_temp, color):
                        coords.append(destination)

                    # if the attempted destination runs into a piece of the same color blocking it
                    elif destination in board.get_occupied(color).values():
                        collision = True

                    else:
                        if too_far is True and self.get_piece_name() != "Cannon":
                            collision = True

                    # increments row, col to be tested by given direction coordinates
                    row_temp, col_temp = row_temp + x_movement, col_temp + y_movement

        # tests available moves for positions outside the palace but within the board
        for x_movement, y_movement in directions:
            collision = False

            row_temp, col_temp = row_from + x_movement, col_from + y_movement
            found_key = None

            while self.is_in_board(row_temp, col_temp):

                destination = (row_temp, col_temp)

                too_far = False

                if abs(row_from - row_temp) > y_distance:
                    too_far = True

                if abs(col_from - col_temp) > x_distance:
                    too_far = True

                if collision is True:
                    break

                # gets piece name in order to give special instructions for the Cannon piece
                for key, value in board.get_occupied().items():
                    if destination == value:
                        found_key = key

                # rule that disallows the Cannon piece from moving without jumping over another piece,
                # and rule that disallows the Cannon from jumping over another Cannon
                if self.get_piece_name() == "Cannon" and destination in occupied and \
                        found_key.get_piece_name() != "Cannon":

                    first = row_temp + x_movement
                    second = col_temp + y_movement
                    jump_row = first
                    jump_col = second

                    while self.is_in_board(jump_row, jump_col):
                        jump = (jump_row, jump_col)

                        if jump not in occupied:
                            coords.append(jump)

                        if jump in capturable:
                            coords.append(jump)
                            break

                        if jump in board.get_occupied(opposite_color).values():
                            coords.append(jump)
                            break  # - removed this to initiate cannon checkmate scenario

                        if jump in board.get_occupied(color).values():
                            break

                        jump_row, jump_col = jump_row + x_movement, jump_col + y_movement

                # for all other pieces aside from the cannon, general, and guard, will append available moves
                # if attempted destination is not occupied and not too far from starting position given piece rules
                if self.get_piece_name() != "Cannon" and (self.get_piece_name() != "General" and
                        self.get_piece_name() != "Guard") and destination not in occupied \
                        and destination not in coords and too_far is False:
                    coords.append(destination)

                # if piece is capturable
                if self.get_piece_name() != "Cannon" and (self.get_piece_name() != "General" and
                        self.get_piece_name() != "Guard") and destination in \
                        board.get_occupied(opposite_color).values() and destination not in coords \
                        and too_far is False:
                    coords.append(destination)

                # if piece is blocked by a piece of the same color
                elif destination in board.get_occupied(color).values():
                    collision = True

                else:
                    if too_far is True and self.get_piece_name() != "Cannon" and \
                        (self.get_piece_name() != "General" and self.get_piece_name() != "Guard"):

                        collision = True

                row_temp, col_temp = row_temp + x_movement, col_temp + y_movement

        return coords

    def horse_elephant(self, row, col, board, direction, capturable):
        '''
        After a list is returned for valid spaces for the horse and elephant pieces to move,
        this method checks if moving to that spot requires moving through a piece.

        If the horse/elephant has to move through a piece to get to the valid destination, that destination is
        no longer valid and removed from the valid moves list.
        
        Recieves: row, col, board, directions, and capturable list
        Returns: list of available coordinates either the horse or elephant list can move to
        '''

        counter = 0
        inner_counter = 0

        possible_coords = []
        actual_possible = []

        # loop that moves through all possible directions the piece can move
        while counter < 8:

            for x_movement, y_movement in direction[counter]:

                inner_counter += 1

                if inner_counter == 1:
                    row_temp, col_temp = row + x_movement, col + y_movement

                else:
                    row_temp, col_temp = row_temp + x_movement, col_temp + y_movement

                destination = (row_temp, col_temp)

                # horses and elephant pieces need to move one square orthogonally before moving either one or two 
                # squares diagonally. this appends all possible movements a piece can make. 
                if self.is_in_board(row_temp, col_temp) and inner_counter == 1:
                    first_move = destination
                    possible_coords.append(first_move)

                if self.is_in_board(row_temp, col_temp) and inner_counter == 2:
                    second_move = destination
                    possible_coords.append(second_move)

                # horses can only move one square diagonally whereas elephants can move 2, tests to see whether
                # there needs to be 2 or 3 moves to the list
                if self.is_in_board(row_temp, col_temp) and inner_counter == len(direction[counter]) \
                        and len(direction[counter]) > 2:
                    last_move = destination
                    possible_coords.append(last_move)

            # tests to see if any of the possible moves gotten from above are occupied and thus any subsequent
            # moves would be invalid
            if inner_counter == len(direction[counter]) and len(possible_coords) == len(direction[0]):

                move_1 = False
                move_2 = False

                if possible_coords[0] not in board.get_occupied().values():
                    move_1 = True

                if move_1 is True and possible_coords[1] not in board.get_occupied().values():
                    move_2 = True

                if move_1 is True and move_2 is True and possible_coords[-1] not in board.get_occupied().values():
                    actual_possible.append(possible_coords[-1])

                if move_1 is True and possible_coords[1] == possible_coords[-1] and possible_coords[-1] in capturable:
                    actual_possible.append(possible_coords[-1])

                if move_1 is True and move_2 is True and possible_coords[-1] in capturable:
                    actual_possible.append(possible_coords[-1])

            counter += 1
            inner_counter = 0
            possible_coords = []

        return actual_possible

    def is_in_board(self, row, col):
        '''
        Checks to see if a coordinates remains in the board.
        
        Receives: row, col
        Returns: either True or False if destination remains in the board indices
        '''

        if row >= 0 and row < 10 and col >= 0 and col < 9:
            return True

        return False

    def is_in_palace(self, row, col, color=None):
        '''
        Checks to see if a coordinates remains in the board.

        Receives: row, col, and color as a default parameter
        Returns: either True or False if destination remains in the palace indices
        '''

        if color == 'red' and row >= 0 and row < 3 and col >= 3 and col < 6:
            return True

        if color == 'blue' and row >= 7 and row < 10 and col >= 3 and col < 6:
            return True

        return False

    def is_valid(self, row_to, col_to, moves_list):
        '''
        Method that checks to see if proposed destination is in the available moves list.
        
        Recieves: row, col of destination, and available moves list
        Returns: True or False if destination in available moves
        '''
    
        if (row_to, col_to) in moves_list:
            return True

        else:
            return False

    def check_capture(self, row_to, col_to, board, color, updated_moves=None):
        '''
        Method that checks whether a piece is able to be captured. 
        
        Recieves: row, col of destination, the board object, color of the player, and updated moves list
        used to check capture again in a check/checkmate scenario. 
        
        Returns: list of coordinates of pieces able to be captured
        '''
        
        captured = []
        destination = (row_to, col_to)

        if color == "blue" and destination in board.get_occupied('red').values():
            captured.append(destination)

        if color == 'red' and destination in board.get_occupied('blue').values():
            captured.append(destination)

        if updated_moves is not None:
            for items in updated_moves:
                if color == 'red' and items in board.get_occupied('blue').values():
                    captured.append(items)
                if color == 'blue' and items in board.get_occupied('red').values():
                    captured.append(items)

        return captured


class General(ChessPiece):
    '''
    The general class that inherits from the ChessPiece class.

    Movement: Anywhere within the place, one point.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the general class that initializes all data members.

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "Gn(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The check_moves method for the General class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, the players turn, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        direction = self._orth
        palace = None
        red = self.is_in_palace(row_from, col_from, 'red')
        blue = self.is_in_palace(row_from, col_from, 'blue')

        if red:
            palace = 'red'

        if blue:
            palace = 'blue'

        return self.possible_moves(row_from, col_from, board, color, direction, capturable, 1, 1, palace)


class Guard(ChessPiece):
    '''
    The guard class that inherits from the ChessPiece class.

    Movement: Same as general, confined to the palace.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the guard class that initializes all data members.

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "G(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The movement method for the guard class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, the players turn, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        direction = self._orth
        palace = None
        red = self.is_in_palace(row_from, col_from, 'red')
        blue = self.is_in_palace(row_from, col_from, 'blue')

        if red:
            palace = 'red'

        if blue:
            palace = 'blue'

        return self.possible_moves(row_from, col_from, board, color, direction, capturable, 1, 1, palace)


class Horse(ChessPiece):
    '''
    The horse class that inherits from the ChessPiece class.

    Movement: One point forward, backward, left or right, then one point outward diagonally. Can be blocked by others.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the horse class that initializes all data members

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "H(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The movement method for the horse class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        right_up = [(0, 1), (-1, 1)]
        right_down = [(0, 1), (1, 1)]

        up_left = [(-1, 0), (-1, -1)]
        up_right = [(-1, 0), (-1, 1)]

        left_up = [(0, -1), (1, -1)]
        left_down = [(0, -1), (-1, -1)]

        down_right = [(1, 0), (1, 1)]
        down_left = [(1, 0), (1, -1)]

        directions = [right_up] + [right_down] + [left_up] + [left_down] + \
                     [up_left] + [up_right] + [down_right] + [down_left]

        return self.horse_elephant(row_from, col_from, board, directions, capturable)


class Elephant(ChessPiece):
    '''
    The elephant class that inherits from the ChessPiece class.

    Movement: One point forward, backward, left or right, and then moves two points outward diagonally.
    Can be blocked.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the elephant class that initializes all data members

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "E(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The movement method for the soldier class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        right_up = [(0, 1), (-1, 1), (-1, 1)]
        right_down = [(0, 1), (1, 1), (1, 1)]

        up_left = [(-1, 0), (-1, -1), (-1, -1)]
        up_right = [(-1, 0), (-1, 1), (-1, 1)]

        left_up = [(0, -1), (1, -1), (1, -1)]
        left_down = [(0, -1), (-1, -1), (-1, -1)]

        down_right = [(1, 0), (1, 1), (1, 1)]
        down_left = [(1, 0), (1, -1), (1, -1)]

        directions = [right_up] + [right_down] + [left_up] + [left_down] + \
                     [up_left] + [up_right] + [down_right] + [down_left]

        return self.horse_elephant(row_from, col_from, board, directions, capturable)


class Chariot(ChessPiece):
    '''
    The chariot class that inherits from the ChessPiece class.

    Movement: As many points as it wants in a straight line horizontally or vertically.
    Can also move diagonally within the palace. Can be blocked by other pieces.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the chariot class that initializes all data members.

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "Ch(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The movement method for the guard class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, the players turn, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        direction = self._orth
        palace = None
        red = self.is_in_palace(row_from, col_from, 'red')
        blue = self.is_in_palace(row_from, col_from, 'blue')

        if red:
            palace = 'red'

        if blue:
            palace = 'blue'

        return self.possible_moves(row_from, col_from, board, color, direction, capturable, 10, 9, palace)


class Cannon(ChessPiece):
    '''
    The cannon class that inherits from the ChessPiece class.

    Movement: Can move along any straight line vertically or horizontally, but must jump over another piece to move.
    Cannot jump over more than one piece and may not move without jumping. May not jump over another cannon and
    cannot capture another cannon.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the cannon class that initializes all data members.

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "Ca(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The movement method for the Cannon class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, the players turn, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        direction = self._orth
        palace = None
        red = self.is_in_palace(row_from, col_from, 'red')
        blue = self.is_in_palace(row_from, col_from, 'blue')

        if red:
            palace = 'red'

        if blue:
            palace = 'blue'

        return self.possible_moves(row_from, col_from, board, color, direction, capturable, 10, 9, palace)


class Soldier(ChessPiece):
    '''
    The soldier class that inherits from the ChessPiece class.

    Movement: One point either forward or sideways. May move diagonally within the palace.
    '''

    def __init__(self, player, piece_name):
        '''
        The init method for the soldier class that initializes all data members.

        Init method does not take any parameters and returns no parameters.
        '''

        super().__init__(player, piece_name)

    def __repr__(self):
        '''
        Repr method for readability of testing results
        '''

        return "S(" + repr(self._player) + ")"

    def check_moves(self, row_from, col_from, board, color, capturable):
        '''
        The movement method for the soldier class that determines the pieces specific movement.

        Recieves: row, col of starting point, the board object, the players turn, and list of coords for
        pieces able to be captured.

        Returns: List of coordinates of available moves.
        '''

        palace = None

        if color == 'blue':
            direction = (0, -1), (0, 1), (-1, 0)
            red = self.is_in_palace(row_from, col_from, 'red')

            if red:
                palace = 'red'

        if color == 'red':
            direction = (0, -1), (0, 1), (1, 0)
            blue = self.is_in_palace(row_from, col_from, 'blue')

            if blue:
                palace = 'blue'

        return self.possible_moves(row_from, col_from, board, color, direction, capturable, 1, 1, palace)

# -------------------------------BOARD-----------------------------------#
class Board:
    '''
    Class that represents the board for the JanggiGame class.

    Responsibilities of the class include initializing the board, displaying it, and
    storing the location of the pieces.

    Will interact with all classes because the board will need to be updated as the game progresses.
    '''

    def __init__(self):
        '''
        The init method for the board class that initializes the board.
        Sets up an empty board with no pieces.

        Recieves: none
        Returns: none
        '''

        self._occupied = {}
        self._occupied_red = {}
        self._occupied_blue = {}

        # creates 9x10 empty board using a list within a list
        self._board = [[], [], [], [], [], [], [], [], [], []]
        board_size = 10

        for i in range(board_size):
            spacing = "       "
            self._board[i] = [spacing] * 9

    def create_board(self):
        '''
        The create_board class that displays the board. Will place all the initial pieces.

        Recieves: no parameters
        Returns: self._board, which is the display of the board with all the pieces placed (initially).
        '''

        count = 0

        # red - top of board
        self._board[0][0] = Chariot("red", "Chariot")
        self._board[0][1] = Elephant("red", "Elephant")
        self._board[0][2] = Horse("red", "Horse")
        self._board[0][3] = Guard("red", "Guard")

        self._board[0][5] = Guard("red", "Guard")
        self._board[0][6] = Elephant("red", "Elephant")
        self._board[0][7] = Horse("red", "Horse")
        self._board[0][8] = Chariot("red", "Chariot")

        self._board[1][4] = General("red", "General")

        self._board[2][1] = Cannon("red", "Cannon")
        self._board[2][7] = Cannon("red", "Cannon")

        self._board[3][0] = Soldier("red", "Soldier")
        self._board[3][2] = Soldier("red", "Soldier")
        self._board[3][4] = Soldier("red", "Soldier")
        self._board[3][6] = Soldier("red", "Soldier")
        self._board[3][8] = Soldier("red", "Soldier")

        # blue - bottom of board
        self._board[9][0] = Chariot("blue", "Chariot")
        self._board[9][1] = Elephant("blue", "Elephant")
        self._board[9][2] = Horse("blue", "Horse")
        self._board[9][3] = Guard("blue", "Guard")

        self._board[9][5] = Guard("blue", "Guard")
        self._board[9][6] = Elephant("blue", "Elephant")
        self._board[9][7] = Horse("blue", "Horse")
        self._board[9][8] = Chariot("blue", "Chariot")

        self._board[8][4] = General("blue", "General")

        self._board[7][1] = Cannon("blue", "Cannon")
        self._board[7][7] = Cannon("blue", "Cannon")

        self._board[6][0] = Soldier("blue", "Soldier")
        self._board[6][2] = Soldier("blue", "Soldier")
        self._board[6][4] = Soldier("blue", "Soldier")
        self._board[6][6] = Soldier("blue", "Soldier")
        self._board[6][8] = Soldier("blue", "Soldier")

        # prints algebraic notation for rows -- used for testing
        # for i in self._board:
        #     print("s" + str(count + 1), count,  i)
        #     count += 1

        # space = " "
        # print(space*10 + "0", space*10 + "1", space *10 + "2", space*10 + "3",  space*8 + "4",
        #       space*8 + "5", space*10 + "6", space*10 + "7", space*10 + "8",)
        # print(space*10 + "a", space*10 + "b", space *10 + "c", space*10 + "d",  space*8 + "e",
        #       space*8 + "f", space*10 + "g", space*10 + "h", space*10 + "i",)

        return self._board

    def get_piece(self, row, col):
        '''
        Get method that takes the row and column index that the piece is located at as parameters.

        Recieves: row and col as parameters to determine where in the index the piece is.
        Returns: the piece at the specified location
        '''

        return self._board[row][col]

    def set_piece(self, row, col, piece):
        '''
        Set method that takes the row and column index to be changed, and the piece to be move as parameters
        and sets the new position of the piece.

        Recieves: row, col, and the piece object as parameters.
        Returns: sets the piece object at the specified location.
        '''

        self._board[row][col] = piece

    def display_board(self):
        '''
        Displays the current state of the board.

        Receives: none
        Returns: self._board
        '''

        space = " "
        count = 0

        for i in self._board:
            print("s" + str(count + 1), count, i)
            count += 1

        print(space*10 + "0", space*10 + "1", space *10 + "2", space*10 + "3",  space*8 + "4",
              space*8 + "5", space*10 + "6", space*10 + "7", space*10 + "8",)
        print(space*10 + "a", space*10 + "b", space *10 + "c", space*10 + "d",  space*8 + "e",
              space*8 + "f", space*10 + "g", space*10 + "h", space*10 + "i",)

        return self._board

    def get_occupied(self, color=None):
        '''
        Method that gets the location and identity of pieces on the board that occupy a space.

        Receives: color as a default parameter if one wants to get a specific color of the pieces on the board.

        Returns: if color parameter is given, then returns a dictionary with key, value of piece object : current
        coordinates on the board for the pieces of that color. If not color is given the returns the same dictionary
        with all the pieces and coordinates they are located in on the board.
        '''

        occupied_pieces = []
        occupied_coords = []

        col = 0
        row = 0

        while row <= 9 and col <= 8:
            for items in self._board:

                square = self._board[row][col]

                if row <= 9 and type(square) != str and color is None:
                    occupied_pieces.append(square)
                    occupied_coords.append((row, col))

                if row <= 9 and type(square) != str and color == 'red' and square.get_player() == 'red':
                    occupied_pieces.append(square)
                    occupied_coords.append((row, col))

                if row <= 9 and type(square) != str and color == 'blue' and square.get_player() == 'blue':
                    occupied_pieces.append(square)
                    occupied_coords.append((row, col))

                row += 1

            if row > 9:
                row = 0
                col += 1

        # dictionary comprehension to populate the dictionary
        self._occupied = {occupied_pieces[i]: occupied_coords[i] for i in range(len(occupied_pieces))}
        saved_occupied_dict = self._occupied

        # empties the dictionary after each use
        self._occupied = {}

        return saved_occupied_dict

# ------------------------------GAME-------------------------------------#

class JanggiGame:
    '''
    Class that starts the game.

    Will interact with the board and ChessPiece classes due to updating the game as it progresses.
    Will need to interact with the Board class to get the board and the ChessPiece class to get and set the
    pieces on the board.

    Will handle input, player movement, determining the game state,
    determining if a player is in check/checkmate, which player's turn it is, and convert strings for movement
    to numerical indices.
    '''

    def __init__(self):
        '''
        The init method that for the JanggiGame class that initializes all data members.

        Recieves: none
        Returns: none
        '''

        self._turn = 1

        self._game_state = "UNFINISHED"
        self._check_blue = False
        self._check_red = False

        # creates the board
        self._board = Board()
        self._new_board = self._board.create_board()

        self._blue_general = self._board.get_piece(8, 4)
        self._red_general = self._board.get_piece(1, 4)

    def get_game_state(self):
        '''
        Get method that returns the game state.

        Recieves: none
        Returns: the game state
        '''

        return self._game_state

    def all_moves(self, color):
        '''
        Returns a list of all available moves for a player's pieces

        Recieves: the players turn (color) as a parameter
        Returns: list of all available moves for a player's pieces
        '''

        all_avail_moves = []
        pieces = []

        if color == 'blue':
            opposing_color = 'red'

        if color == 'red':
            opposing_color = 'blue'

        class_coord_counter = 0

        for keys in self._board.get_occupied(opposing_color).items():
            pieces += [keys]

        # creates a list of all available moves each piece of the given color can make
        for items in range(len(pieces)):
            row = pieces[class_coord_counter][1][0]
            col = pieces[class_coord_counter][1][1]

            the_piece = self._board.get_piece(row, col)

            capture = the_piece.check_capture(row, col, self._board, color)
            moves = the_piece.check_moves(row, col, self._board, opposing_color, capture)

            all_avail_moves += moves # [the_piece.get_piece_name(), moves]
            class_coord_counter += 1

        return all_avail_moves

    def is_in_check(self, color):
        '''
        Method that determines whether a player is in check. Checks all moves of opposing pieces to see if any
        moves land on the coordinates the opposing general is located. If so, returns True.

        Recieves: the players turn (color) as a parameter
        Returns: either true or false as to whether the player is in check.
        '''

        if color == 'blue':
            opponent = 'red'
            the_general = self._blue_general

        if color == 'red':
            opponent = 'blue'
            the_general = self._red_general

        all_moves = self.all_moves(color)

        # gets the location of the opposing general
        general = [[key, value] for key, value in self._board.get_occupied(color).items()
                   if key == the_general]

        general_loc = (general[0][1][0], general[0][1][1])

        if general_loc in all_moves:


            return True

        else:
            return False

    def is_in_checkmate(self, color):
        '''
        Method that determines whether a move has put the other player in checkmate.

        Recieves: color of the player to be tested
        Returns: True or False depending on if checkmate is achieved.
        '''

        capture = []

        if color == 'blue':
            opponent = 'red'
            the_general = self._blue_general

        if color == 'red':
            opponent = 'blue'
            the_general = self._red_general

        all_moves = self.all_moves(color)

        # gets the location and possible moves of the opposing general
        general = [[key, value] for key, value in self._board.get_occupied(color).items()
                   if key == the_general]

        get_general = self._board.get_piece(general[0][1][0], general[0][1][1])

        # all moves the opposing general can make
        general_moves = get_general.check_moves(general[0][1][0],  general[0][1][1], self._board, color, capture)

        # if every move the opposing general can make is in the available moves list of the opposing pieces,
        # the oppposing general has no more moves since every move will result in a capture, thus a checkmate
        result = all(elem in all_moves for elem in general_moves)

        if result:
            return True
        else:
            return False

    def get_valid_moves(self, row_from, col_from, moves_check, board, color):

        if color == 'blue':
            opponent = 'red'
        if color == 'red':
            opponent = 'blue'

        updated_avail_moves = moves_check
        empty = "       "
        start_pos = board.get_piece(row_from, col_from)

        for i in range(len(updated_avail_moves) - 1, -1, -1):
            for x, y in updated_avail_moves:

                if type(board.get_piece(row_from, col_from)) == str:
                    old_pos = empty

                else:
                    old_pos = board.get_piece(x, y)

                board.set_piece(x, y, board.get_piece(row_from, col_from))
                board.set_piece(row_from, col_from, empty)

                if self.is_in_check(color):
                    updated_avail_moves.remove((x, y))

                board.set_piece(x, y, old_pos)
                board.set_piece(row_from, col_from, start_pos)

        if len(updated_avail_moves) == 0 and self.is_in_check(color):
            if color == "blue":
                self._game_state = "RED_WON"
            else:
                self._game_state = "BLUE_WON"

        return updated_avail_moves

    def convert_move_col(self, move):
        '''
        Method that converts letter (a-i) to the corresponding list index number
        for the move parameter for the row index on the board. Given that things are in algebraic notation.

        Recieves: the col we are moving from/to
        Returns: an integer value that corresponds with the letter so that we can manipulate list indices
        '''

        temp_move = move[0]
        new_move = None

        if temp_move == "a":
            new_move = 0

        if temp_move == "b":
            new_move = 1

        if temp_move == "c":
            new_move = 2

        if temp_move == "d":
            new_move = 3

        if temp_move == "e":
            new_move = 4

        if temp_move == "f":
            new_move = 5

        if temp_move == "g":
            new_move = 6

        if temp_move == "h":
            new_move = 7

        if temp_move == "i":
            new_move = 8

        return new_move

    def convert_move_row(self, move):
        '''
        Method that converts the string into an int to pass to make_move method to designate
        the row in which to move from. Given that things are in algebraic notation.

        Recieves: the row we are moving from/to
        Returns: an integer value that corresponds with the col number to manipulate the index to move from
        '''

        row_temp = move[1:]
        new_row_move = None

        if row_temp == "1":
            new_row_move = 0

        if row_temp == "2":
            new_row_move = 1

        if row_temp == "3":
            new_row_move = 2

        if row_temp == "4":
            new_row_move = 3

        if row_temp == "5":
            new_row_move = 4

        if row_temp == "6":
            new_row_move = 5

        if row_temp == "7":
            new_row_move = 6

        if row_temp == "8":
            new_row_move = 7

        if row_temp == "9":
            new_row_move = 8

        if row_temp == "10":
            new_row_move = 9

        return new_row_move

    def piece_to_player(self, row_from, col_from):
        '''
        Method that tests to see if the player attempting to move the piece controls the piece.

        Recieves: row and column location of the piece player is attempting to move.
        Returns: True or False depending on whether it is the player's piece they are attempting to move.
        '''

        # gets the board and gets the pieces
        get_piece = self._board.get_piece(row_from, col_from)

        player = get_piece.get_player()

        # blue will be odd numbers
        if self._turn % 2 != 0 and player == "blue":
            return True

        if self._turn % 2 == 0 and player == "red":
            return True

        else:
            return False

    def make_move(self, move_from, move_to):
        '''
        Method that moves the pieces.

        Determines if a valid move has been made. For example, if the square being moved from does not contain
        a piece belonging ot the player whose turn it is, or if the indicated move is not legal, or if the game
        has already been won. Should return false if any of these occur.

        If move is valid, then it should make the indicated move, remove any captured piece, update the game state,
        and update whose turn it is.

        Recieves: move_from and move_to arguments to determine where to move from and to.
        Returns: either true or false depending on if a valid move is made
        '''

        # converts algebraic movement to list indices
        row_from = self.convert_move_row(move_from)
        col_from = self.convert_move_col(move_from)
        row_to = self.convert_move_row(move_to)
        col_to = self.convert_move_col(move_to)

        # gets the board and gets the pieces
        get_piece = self._board.get_piece(row_from, col_from)
        occupied_dict = self._board.get_occupied()

        # returns false if the game has already been won
        if self._game_state != "UNFINISHED":
            return False

        # if player wants to pass their turn, they input the same rows and columns for both moves
        # handles if the space is empty and the player wants to pass
        if type(get_piece) == str and row_from == row_to and col_from == col_to:
            self._turn += 1
            return True

        # if the player attempts to move an empty space, will return False as an invalid move and not update
        # turn counter
        if type(get_piece) == str:
            return False

        piece = get_piece.get_piece_name()

        # finds out whose turn it is
        if self._turn % 2 != 0:
            players_turn = 'blue'
        if self._turn % 2 == 0:
            players_turn = 'red'

        if players_turn == 'blue':
            opposite_color = 'red'
        if players_turn == 'red':
            opposite_color = 'blue'

        # gets the list of capturable pieces, all available moves of the piece, and whether the attempted move is valid
        capture = get_piece.check_capture(row_to, col_to, self._board, players_turn)
        moves_check = get_piece.check_moves(row_from, col_from, self._board, players_turn, capture)
        updated_moves = self.get_valid_moves(row_from, col_from, moves_check, self._board, players_turn)
        valid_moves = get_piece.is_valid(row_to, col_to, updated_moves)

        # tests if there is a piece to be moved or if space is empty
        if type(get_piece) == str and row_from != row_to and col_from != col_to:
            return False

        # if move from is the same as move to the player passes their turn
        if row_from == row_to and col_from == col_to:
            self._turn += 1
            return True

        if not self.piece_to_player(row_from, col_from):
            return False

        empty = "       "

        # if the move is valid and the piece to be moved is controlled by the player whose turn it is,
        # move the piece and empty the space it was previously in and update the board
        if self.piece_to_player(row_from, col_from) is True and valid_moves is True:
            move_piece = self._board.set_piece(row_to, col_to, get_piece)
            empty_previous_spot = self._board.set_piece(row_from, col_from, empty)

            checkmate = self.is_in_checkmate(opposite_color)

            # if the player is in check, tests to see if that player is also in checkmate
            # if so it updates the game state to which player won
            if self.is_in_check(opposite_color) and players_turn == 'blue' and checkmate:
                self._game_state = "BLUE_WON"

            if self.is_in_check(opposite_color) and players_turn == 'red' and checkmate:
                self._game_state = "RED_WON"

            # updates the turn counter if the move was valid and returns True
            self._turn += 1
            return True

        # returns False if move invalid
        else:
            return False

# -----------------TESTING------------------#
if __name__ == '__main__':
    game = JanggiGame()

# ------
    # passing, games state
    #move_result = game.make_move('e9', 'e10')
    # state = game.get_game_state()
    # print(state)

# ------
    # cannon test
    # move_result = game.make_move('c7', 'c6')
    # move_result = game.make_move('a4', 'a5')
    # move_result = game.make_move('a7', 'b7')
    # move_result = game.make_move('a5', 'a6')
    # move_result = game.make_move('b8', 'b6')
    # move_result = game.make_move('a6', 'a7')
    # move_result = game.make_move('b6', 'e6')

# ------
    # rook capture/chariot move
    # move_result = game.make_move('a7', 'a6')
    # move_result = game.make_move('d1', 'd2')
    # move_result = game.make_move('a10', 'a9')
    # move_result = game.make_move('d2', 'd3')
    # move_result = game.make_move('a9', 'b9')
    # move_result = game.make_move('b3', 'b9')

# ------
    # soldier capture
    # move_result = game.make_move('a7', 'a6')
    # move_result = game.make_move('a4', 'a5')
    # move_result = game.make_move('a6', 'a5')

# ------
    # general moves
    # move_result = game.make_move('e9', 'f8')
    # move_result = game.make_move('e2', 'e3')
    # move_result = game.make_move('f8', 'f9')

#------
    # chariot palace

    # move_result = game.make_move('a10', 'a9')
    # move_result = game.make_move('e2', 'd2')
    # move_result = game.make_move('a9', 'd9')
    # move_result = game.make_move('d2', 'e2')
    # move_result = game.make_move('d9', 'd8')
    # move_result = game.make_move('e2', 'd2')
    # move_result = game.make_move('e9', 'e10')
    # move_result = game.make_move('d2', 'e2')
    # move_result = game.make_move('d8', 'e9')
    # move_result = game.make_move('e9', 'e9')
    # move_result = game.make_move('e9', 'e8')

#------
    # soldier palace

    # move_result = game.make_move('e7', 'e6')
    # move_result = game.make_move('a1', 'a2')
    # move_result = game.make_move('e6', 'e5')
    # move_result = game.make_move('a2', 'a1')
    # move_result = game.make_move('e5', 'e4')
    # move_result = game.make_move('a1', 'a2')
    # move_result = game.make_move('e4', 'e3')
    # move_result = game.make_move('a2', 'a1')
    # move_result = game.make_move('e3', 'f2')
    # move_result = game.make_move('e9', 'e9')
    # move_result = game.make_move('e9', 'e8')

#------
    # turn taking

    # move_result = game.make_move('a1', 'a3')
    # move_result = game.make_move('a7', 'a6')
    # move_result = game.make_move('a1', 'a2')
    # move_result = game.make_move('d10', 'd9')

#------

    # general/guard stay in palace check

    # move_result = game.make_move('e9', 'f8')
    # move_result = game.make_move('e2', 'f3')
    # move_result = game.make_move('f8', 'g8')
    # move_result = game.make_move('f8', 'f8')
    # move_result = game.make_move('f3', 'f4')
    # move_result = game.make_move('f3', 'f3')
    # move_result = game.make_move('f10', 'e10')
    # move_result = game.make_move('f1', 'e1')
    # move_result = game.make_move('f8', 'f10')

#------

    # chariot moves

    # move_result = game.make_move('a10', 'a8')
    # move_result = game.make_move('a1', 'a2')
    # move_result = game.make_move('a8', 'a9')

#------

    # move piece out of check test

    # move_result = game.make_move('h10', 'g8')
    # move_result = game.make_move('h1', 'g3')
    # move_result = game.make_move('h8', 'e8')
    # move_result = game.make_move('e4', 'd4')
    # print("CHECK: ", game.is_in_check('red'))           # False - Game should prevent this move
    # print("CHECKMATE: ", game.is_in_checkmate('red'))   # False

#------
    # check moves

    # move_result = game.make_move('c7', 'c6')
    # blue_in_check = game.is_in_check('blue')
    #
    # move_result = game.make_move('c1', 'd3')
    #
    # move_result = game.make_move('b10', 'd7')
    #
    # move_result = game.make_move('b3', 'e3')
    #
    # move_result = game.make_move('c10', 'd8')
    #
    # move_result = game.make_move('h1', 'g3')
    #
    # move_result = game.make_move('e7', 'e6')
    #
    # move_result = game.make_move('e3', 'e6')
    #
    # move_result = game.make_move('h8', 'c8')
    #
    # move_result = game.make_move('d3', 'e5')
    #
    # move_result = game.make_move('c8', 'c4')
    #
    # move_result = game.make_move('e5', 'c4')
    #
    # move_result = game.make_move('i10', 'i8')
    #
    # move_result = game.make_move('g4', 'f4')
    #
    # move_result = game.make_move('i8', 'f8')
    #
    # move_result = game.make_move('g3', 'h5')
    #
    # move_result = game.make_move('h10', 'g8')
    #
    # move_result = game.make_move('e6', 'e3')
    #
    # move_result = game.make_move('e9', 'd9')
    #
    # move_result = game.make_move('e9', 'd9')
    #
    # move_result = game.make_move('a4', 'b4')
    #
    # move_result = game.make_move('a10', 'c10')
    #
    # move_result = game.make_move('b4', 'b4')
    #
    # move_result = game.make_move('a7', 'b7')
    #
    # move_result = game.make_move('a1', 'a9')
    #
    # print("CHECK STATUS:", game.is_in_check('blue'))
    # print("CHECKMATE:", game.get_game_state())

    # move_result = game.make_move('d9', 'e9')




