# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 23:21:45 2022

@author: dmdra
"""

import numpy as np
import logging, logging.config
import time
from random import randint

#logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG, filename="sudoku.log", filemode="w")
logging.config.fileConfig('logging.conf')

logger = logging.getLogger('sudoku')


class Sudoku:
  
  
  LEGAL_VALUES = [i for i in range(1, 10)]
  UNIQUES = np.unique(LEGAL_VALUES)
  EMPTY_VALUE = 0

  """
  Initializes the Sudoku class object.
  No parameters will generate a board with 17 clues.
  Key 'filename' will initialize the board from a given text file.
  Key 'generate' will generate a board with the given number of clues.
  Key 'test' will create an "empty board", which is a board with only '0's.
  """
  def __init__(self, **kwargs):
    logger.debug("Initializing Sudoku board")
    if len(kwargs) > 0: # If keyword arguments were provided
      logger.debug("  Initialization keyword arguments (expecting %s):", len(kwargs))
      if logger.getEffectiveLevel() <= logging.DEBUG:
        for key, value in kwargs.items():
          logger.debug("\t%s : %s", key, value)
#    self.board = self.init_board()
#    self.clear_board()
    self.board = np.zeros((9, 3, 3), dtype=int)
    if "filename" in kwargs.keys():
      self.init_from_file(kwargs["filename"])
    elif "generate" in kwargs.keys():
      self.generate_board(int(kwargs["generate"]))
    else:
      self.generate_board()
  
  """
  Compares Sudoku boards for equality.
  Returns: True if all values in self's board are equal to all corresponding values in other's board,
  False otherwise.
  """
  def __eq__(self, other) -> bool:
    return (self.board == other.board).all()
      
  """
  Combines the provided list of digits into one integer.
  Utility function used in validating a solved Sudoku board.
  """
  def __combine_digits__(self, digits: list) -> int:
    if len(digits) < 1:
      return None
    if len(digits) == 1:
      return digits[0]
    d = digits
    factor = 10
    value = d[-1]
    for i in range(len(digits)-2, -1, -1):
      value += d[i]*factor
      factor *= 10
    return value
  
  def init_board(self):
    board = np.zeros((9, 3, 3), dtype=int)
    for k in range(0, 9):
      board[k][0][0] = k + 1
      for i in range(0, 3):
        board[k][i][2] = 9
        for j in range(1, 3):
          board[k][0][j] = 4
    v = 1
    for r in range(0, 3):
      for c in range(0, 3):
        board[0][r][c] = v
        v += 1
    return board
  
  def clear_board(self):
    def f(s, r, c):
      self.board[s][r][c] = 0
    self.loop_rows(f)
  
  #print(board)
  
#  def check_row(self, val, s, row, col) -> bool:
#    for k in range(0, 9):
#      for c in range(0, 3):
#        if self.board[k][row][c] == val:
#          if not (k == s and c == col):
#            return False
#    return True
  
#  def check_col(self, val, s, row, col) -> bool:
#    for k in range(0, 9):
#      for r in range(0, 3):
#        if self.board[k][r][col] == val:
#          if not (k == s and r == row):
#            return False
#    return True
  
#  def check_square(self, val, s, row, col) -> bool:
#    for r in range(0, 3):
#      for c in range(0, 3):
#        if self.board[s][r][c] == val:
#          if not (r == row and c == col):
#            return False
#    return True
  
  def __collect_row_into_list__(self, row: int) -> list:
    r = row % 3
    s = 0 # first row of squares
    L = list()
    if row > 5: # last row of squares
      s = 6
    elif row > 2: # middle row of squares
      s = 3
    for j in range(9): # go through columns in row
      c = j % 3
      if j % 3 == 0 and j != 0: # if we should be in the next square
        s += 1
      L.append(self.board[s][r][c])
    return L
  
  def __collect_col_into_list__(self, col: int) -> list:
    c = col % 3
    s = 0 # first col of squares
    L = list()
    if col > 5: # last col of squares
      s = 2
    elif col > 2: # middle col of squares
      s = 1
    for j in range(9): # go through rows in column
      r = j % 3
      if j % 3 == 0 and j != 0: # if we should be in the next square
        s += 3
      L.append(self.board[s][r][c])
    return L
  
  def __values_are_valid__(self, values: list) -> bool:
    for i in range(len(values)):
      if values[i] in Sudoku.LEGAL_VALUES or values[i] == Sudoku.EMPTY_VALUE:
        if values.count(values[i]) > 1:
          if values[i] != Sudoku.EMPTY_VALUE:
            return False
      else:
        return False
    return True
  
  def __rows_are_valid__(self) -> bool:
    zcount = 0
    rows = set()
    for i in range(9):
      values = self.__collect_row_into_list__(i)
      if not self.__values_are_valid__(values):
        return False
      v = self.__combine_digits__(values)
      if v in rows:
        if v.all():
          return False
        else:
          if not v.any():
            zcount += 1
      else:
        rows.add(v)
    return len(rows) + zcount == 9
    
  def __cols_are_valid__(self) -> bool:
    zcount = 0
    cols = set()
    for i in range(9):
      values = self.__collect_col_into_list__(i)
      if not self.__values_are_valid__(values):
        return False
      v = self.__combine_digits__(values)
      if v in cols:
        if v.all():
          return False
        else:
          if not v.any():
            zcount += 1
      else:
        cols.add(v)
    return len(cols) + zcount == 9
  
  def __squares_are_valid__(self) -> bool:
    zcount = 0
    squares = set()
    for i in range(9):
      values = list(self.board[i].flatten())
      if not self.__values_are_valid__(values):
#        print("squares values are not valid")
        return False
      v = self.__combine_digits__(values)
      if v in squares:
#        print("v in squares is true")
        if v.all():
#          print(f"v.all is {v.all()}")
          return False
        else:
          if not v.any():
            zcount += 1
      else:
        squares.add(v)
#    print(f"len(squares) + zcount == 9: {len(squares)} + {zcount} == 9 -> {len(squares) + zcount == 9}")
    return len(squares) + zcount == 9
  
  """ Is Valid
  Returns: bool -> True if the rows, columns, and 3x3 squares are in a valid state,
    False otherwise.
  """
  def __is_valid__(self) -> bool:
    return (self.__rows_are_valid__() 
            and self.__cols_are_valid__() 
            and self.__squares_are_valid__())
  
#  def check_value(self, val, s, row, col) -> bool:
#    return self.check_row(val, s, row, col) and self.check_col(val, s, row, col) and self.check_square(val, s, row, col)

  """
  Returns a string representation of the current state of the Sudoku board.
  """
  def to_string(self) -> str:
    board_str = ""
    for k in range(0, 9, 3):
      for r in range(0, 3):
        for s in range(k, k+3):
          board_str += str(self.board[s][r]) + ' '
        board_str += '\n'
      board_str += '\n'
    return board_str
  
  """
  Writes the contents of this Sudoku board to a text file,
  using the same format as used to initialize a new board from a file.
  Params: filename - a string. The Sudoku board will be written to this file.
  """
  def to_file(self, filename: str):
    with open(filename, "w") as f:
      for i in range(0, 81):
        if i % 9 == 0 and i > 0:
          f.write("\n")
        s, r, c = Sudoku.pos_to_indices(i)
        f.write(str(self.board[s][r][c]))
      f.write("\n")
        
    
  """
  Returns True if the given Sudoku square (or 3x3 block) is solved, False otherwise.
  Solved is defined as each cell containing a unique integer in the interval [1,9].
  """
  def square_is_solved(self, s) -> bool:
    unique_square = np.unique(self.board[s])
    return (np.shape(unique_square) == np.shape(Sudoku.UNIQUES) 
            and np.all(np.equal(unique_square, Sudoku.UNIQUES)))
  
  """
  Returns True if all nine squares of the Sudoku board are solved, False otherwise.
  """
  def squares_are_solved(self) -> bool:
    if not self.__squares_are_valid__():
      return False
    for i in range(9):
      if not self.square_is_solved(i):
        return False
    return True
  
  """
  Returns True if the Sudoku board is solved, False otherwise.
  To be solved, the board must both be in a valid state and have no empty spaces.
  Note: An empty space is represented by a '0', the EMPTY_VALUE constant.
  """
  def board_is_solved(self) -> bool:
    valid = self.__rows_are_valid__() and self.__cols_are_valid__()
    solved = self.squares_are_solved() and self.board.all()
    return valid and solved
  
  def board_is_solved_two(self) -> bool:
    return (self.__rows_are_valid__() 
            and self.__cols_are_valid__() 
            and self.squares_are_solved() 
            and self.board.all())
  
  """
  Applies the given function, f, to each cell in the board, traversing across rows.
  Params: f, the function to apply to the given cell, and any keyword arguments to be passed into f.
  """
  def loop_rows(self, f, **kwargs):
    s = r = c = 0 # square, row, column
    for i in range(0, 9): # rows
      r = i % 3
      if i % 3 == 0 and i != 0:
        s += 1
      for j in range(0, 9): # columns
        c = j % 3
        if j % 3 == 0 and j != 0: # if this column is in the next square
          s += 1
        # do stuff with position [s][r][c]
        f(s, r, c, **kwargs)
      # end j loop
      if (i + 1) % 3 != 0: # if next row is not in the next row of squares
        s -= 2 # move square back to 

  def init_test_junk_board(self):
    def gen():
      i = 0
      while True:
        yield i
        i += 1
    it = gen()
    def f(s, r, c):
      self.board[s][r][c] = next(it)
    
    self.loop_rows(f)
    print(self.to_string())
  
  """
  Initializes the Sudoku board from a file.
  The expected file format is 9 lines of 9 unseparated integers, organized by row.
  However, as white space is removed, the integers may be separated without causing an error.
  """
  def init_from_file(self, filename: str):
    b = None
    with open(filename, "r") as f:
      b = f.read().replace(" ", "").replace("\n", "")
      
    def f(s, r, c, **kwargs):
      vals = kwargs["vals"]
      it = kwargs["it"]
      i = next(it)
      self.board[s][r][c] = int(vals[i]) if vals[i].isnumeric() else None
      
    def gen():
      i = 0
      while i < len(b):
        yield i
        i += 1
        
    self.loop_rows(f, it=gen(), vals=b)
#      if vals[i].isnumeric():
#        self.board[s][r][c] = int(vals[i])
#      else:
#        self.board[s][r][c] = None
  
  """ Position to Indices
  Maps an absolute position on the board to the three indices used in self.board.
  Params: An integer representing the absolute position on the board.
  Returns: Three integers, s, r, c, representing the square, row, and column position in self.board.
  """
  def pos_to_indices(x: int) -> int:
    col = x % 9
    c = col % 3
    
    row = (x - col) // 9
    r = row % 3
    
    square_col = 0 if col < 3 else 2 if col > 5 else 1
    square_row = 0 if row < 3 else 6 if row > 5 else 3
    s = square_col + square_row
    
    return s, r, c
  
  """ Indices to Position
  Maps the three indices (square, row, column) to the absolute position on the board.
  Params: three integers, s, r, c, representing the square, row, and column position in self.board.
  Returns: An integer representing the absolute position on the board.
  """
  def indices_to_pos(s: int, r: int, c: int) -> int:
    # return 9 * (r + s - (s % 3)) + (3 * (s % 3) + c)
    square_col = s % 3
    square_row = s - square_col
    row = r + square_row
    col = 3 * square_col + c
    return 9 * row + col
    
  """ Solve Puzzle Backtracking
  Solves the Sudoku puzzle using backtracking.
  This is a brute-force method of solving Sudoku.
  While it should be able to solve every solvable Sudoku puzzle,
  some puzzles may require a large amount of time to solve,
  given the large amount of possible solutions.
  """
  def solve_puzzle_backtracking(self):
    def gen():
      i = 1
      while i < 10:
        yield i
        i += 1
    
    """ Check Cell
    Recursive method which checks the given Sudoku cell and attempts to find
      a value to place in this cell to solve the puzzle. A recursive call is made
      only when a value has been selected for the given cell and the board
      remains in a valid state. If the board ever enters an invalid state,
      the method will either try a new value, or, if all legal values have failed,
      resets the offending value to 0 (the empty value) and returns False (backtracks)
      to the previous calling method.
    Params: x -> an integer representing the cell of the Sudoku board,
      where each cell is numbered from 0 to 80, starting from the top-left cell
      and counting across the rows from left to right, top to bottom.
    Return: a bool -> True if a solution to this Sudoku board has been found,
      False otherwise
    """
    def check_cell(x: int) -> bool:
      if x > 80:
        logger.info("Solution has been found for this board.")
        return True
      logger.debug("checking cell %s", x)
      s, r, c = Sudoku.pos_to_indices(x)
      if self.board[s][r][c] != Sudoku.EMPTY_VALUE:
        return check_cell(x + 1)
      values = gen()
      for val in values:
        self.board[s][r][c] = val
        if not self.__is_valid__():
          continue
        logger.debug("Selected value %s for cell %s, about to check cell %s", val, x, x + 1)
        if check_cell(x + 1):
          return True
        logger.debug("Returned to cell %s, current value is %s, checking next value.", x, val)
      logger.debug("About to backtrack from cell %s (value was %s)", x, self.board[s][r][c])
      self.board[s][r][c] = Sudoku.EMPTY_VALUE
      return False
    
    start = time.time()
    if check_cell(0):
      if self.board_is_solved():
        end = time.time()
        final = end - start
        print(f"Board is solved (in {final} seconds):")
        print(self.to_string())
        logger.info("Board was solved in %s seconds", final)
        return True
      else:
        print("Error: Board is not solved, but check_cell returned True.")
        print(self.to_string())
        logger.warning("Board was reported solved, but is not actually solved.")
        return False
    else:
      print(f"Board is not solvable (conclusion reached in {time.time() - start} seconds)")
      print(self.to_string())
      logger.info("Board was found to be unsolvable in %s seconds", time.time() - start)
      return False
  
  """ Generate Board
  Generates a solvable Sudoku board given a number of clues to generate.
  Params: n -> An integer representing the number of clues to use for this board.
    Defaults to 17 (the minimum number of clues needed to solve a Sudoku puzzle).
  Return: None
  """
  def generate_board(self, n: int = 17):
    print("\n")
    
    """ Generate Clue
    Recursive method which generates a clue at the given position, 
      selected from a list of positions.
    Params: pos -> an integer representing the position in which to generate a clue on the board.
      clues -> a list of integers representing positions to place clues.
    Return: bool -> True if this and all future calls found a clue for positions which
      did not place the board in an invalid state, False otherwise.
    """
    def generate_clue(pos: int, clues: list) -> bool:
        values = [i for i in range(1, 10)]
        s, r, c = Sudoku.pos_to_indices(pos)
        while len(values) > 0:
          # Try a random value from the remaining values
          self.board[s][r][c] = values.pop(randint(0, len(values)-1))
          if self.__is_valid__():
            if len(clues) > 0:
              if generate_clue(clues.pop(0), clues):
                # Received True from recursive call. All clues should be placed.
                logger.debug("inner generate position returning true")
                return True
              else:
                # Received False from recursive call. At least one clue was invalid. 
                # Try a new value.
                logger.debug("inner generate position returned false")
                continue
            else:
              # Base case for recursion. We have finished placing all clues.
              return True
          else:
            # This clue put the board in an invalid state. Try a new value.
            logger.debug("self.isValid is false")
#        self.board[s][r][c] = 0
        # All values at this position failed to produce a valid board.
        logger.debug("generate position returning false")
        return False
    
    while True:
      N = [i for i in range(0, 81)]
      clues = [N.pop(randint(0, len(N)-1)) for _ in range(n)]
      print(f"Number of clues: {len(clues)}")
      
      generate_clue(clues.pop(0), clues)
      
      print(self.to_string())
      board_cpy = self.board.copy()
      
      if self.solve_puzzle_backtracking():
        self.board = board_cpy
        break
      else:
        self.clear_board()
#        break
      
      

def rand_gen():
  l = [i for i in range(1, 10)]
  while len(l) > 0:
    yield l.pop(randint(0, len(l)-1))

def write_dummy_file():
  def gen():
    vals = [i for i in range(1, 10)]
    i = 0
    while True:
      yield vals[i]
      i += 1
      if i == 9:
        vals.append(vals.pop(0))
        i = 0
  it = gen()
  
  with open("dummy.txt", 'w') as f:
    for r in range(9):
      for c in range(9):
        f.write(str(next(it)))
        f.write(" ")
      f.write("\n")

def test_combine_digits():
  test_list_1 = [1, 2, 3, 4]
  test_value_1 = 1234
  T = Sudoku()
  actual_value = T.__combine_digits__(test_list_1)
  print(f"expected: {test_value_1} | actual: {actual_value}")
  assert actual_value == test_value_1
  
    
def main():
#  T = Sudoku(filename="sudoku_solver_test_02.txt")
#  print(T.to_string())
#  print(T.board_is_solved())
#  print("Beginning backtracking algorithm\n")
#  print(T.solve_puzzle_backtracking())
#  
#  G = Sudoku(filename="sudoku_test_00.txt")
#  print(G.to_string())
#  print("Matches original puzzle?")
#  print(G == T)
  start_time = time.time()
  print("Generating board")
  logger.debug("About to create the Sudoku Board E")
  E = Sudoku(generate=17)
  logger.info("Sudoku board generation and solution completed in %s seconds.\
               Program is completed.", time.time() - start_time)
  E.to_file("sudoku_output_test_00.txt")
  
if __name__ == "__main__":
  logger.info("Sudoku running as main.")
  main()