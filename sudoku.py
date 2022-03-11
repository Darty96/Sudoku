# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 23:21:45 2022

@author: dmdra
"""

import numpy as np
import logging, time
from random import randint
# square, row, col
#board = np.zeros((9, 3, 3))


logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG, filename="sudoku.log", filemode="w")

class Sudoku:
  
  LEGAL_VALUES = [i for i in range(1, 10)]
  UNIQUES = np.unique(LEGAL_VALUES)
  EMPTY_VALUE  = 0

  def __init__(self, **kwargs):
    self.board = self.init_board()
    self.clear_board()
    if "filename" in kwargs.keys():
      self.init_from_file(kwargs["filename"])
    if "generate" in kwargs.keys():
      self.generate_board(int(kwargs["generate"]))
  
  def __eq__(self, other):
    return (self.board == other.board).all()
      
  
  def __combine_digits__(self, digits):
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
  
  def __collect_row_into_list__(self, row):
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
  
  def __collect_col_into_list__(self, col):
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
  
  def __values_are_valid__(self, values):
    for i in range(len(values)):
      if values[i] in Sudoku.LEGAL_VALUES or values[i] == Sudoku.EMPTY_VALUE:
        if values.count(values[i]) > 1:
          if values[i] != Sudoku.EMPTY_VALUE:
            return False
      else:
        return False
    return True
  
  def __rows_are_valid__(self):
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
    
  def __cols_are_valid__(self):
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
  
  def __squares_are_valid__(self):
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
    
  def __is_valid__(self):
    return self.__rows_are_valid__() and self.__cols_are_valid__() and self.__squares_are_valid__()
  
#  def check_value(self, val, s, row, col) -> bool:
#    return self.check_row(val, s, row, col) and self.check_col(val, s, row, col) and self.check_square(val, s, row, col)

  def to_string(self):
    board_str = ""
    for k in range(0, 9, 3):
      for r in range(0, 3):
        for s in range(k, k+3):
          board_str += str(self.board[s][r]) + ' '
        board_str += '\n'
      board_str += '\n'
    return board_str
  
  def square_is_solved(self, s):
    unique_square = np.unique(self.board[s])
    return np.shape(unique_square) == np.shape(Sudoku.UNIQUES) and np.all(np.equal(unique_square, Sudoku.UNIQUES))
  
  def squares_are_solved(self):
    if not self.__squares_are_valid__():
      return False
    for i in range(9):
      if not self.square_is_solved(i):
        return False
    return True
  
  def board_is_solved(self):
    valid = self.__rows_are_valid__() and self.__cols_are_valid__()
    solved = self.squares_are_solved() and self.board.all()
    return valid and solved
  
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
    
  def init_from_file(self, filename):
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
    
  def pos_to_indices(x):
    col = x % 9
    c = col % 3
    
    row = (x - col) // 9
    r = row % 3
    
    square_col = 0 if col < 3 else 2 if col > 5 else 1
    square_row = 0 if row < 3 else 6 if row > 5 else 3
    s = square_col + square_row
    
    return s, r, c
  
  def indices_to_pos(s, r, c):
    square_col = s % 3
    square_row = s - square_col
    row = r + square_row
    col = 3 * square_col + c
    return 9 * row + col
  
  # return 9 * (r + s - (s % 3)) + (3 * (s % 3) + c)
    
    
  def solve_puzzle_backtracking(self):
    def gen():
      i = 1
      while i < 10:
        yield i
        i += 1
    
    def check_cell(x):
      if x > 80:
        logging.info("Finished solving board.")
        return True
      logging.debug("checking cell %s", x)
      s, r, c = Sudoku.pos_to_indices(x)
      if self.board[s][r][c] != Sudoku.EMPTY_VALUE:
        return check_cell(x + 1)
      values = gen()
      for val in values:
        self.board[s][r][c] = val
        if not self.__is_valid__():
          continue
        logging.debug("Selected value %s for cell %s, about to check cell %s", val, x, x + 1)
        if check_cell(x + 1):
          return True
        logging.debug("Returned to cell %s, current value is %s, checking next value.", x, val)
      logging.debug("About to backtrack from cell %s (value was %s)", x, self.board[s][r][c])
      self.board[s][r][c] = Sudoku.EMPTY_VALUE
      return False
    
    start = time.time()
    if check_cell(0):
      if self.board_is_solved():
        end = time.time()
        final = end - start
        print(f"Board is solved (in {final} seconds):")
        print(self.to_string())
        logging.info("Board was solved in %s seconds", final)
        return True
      else:
        print("Error: Board is not solved, but check_cell returned True.")
        print(self.to_string())
        logging.warning("Board was reported solved, but is not actually solved.")
        return False
    else:
      print("Board is not solvable")
      print(self.to_string())
      logging.info("Board was found to be unsolvable in %s seconds", time.time() - start)
      return False
    
  def generate_board(self, n=17):
    print("\n")
    def generate_position(pos, positions):
        values = [i for i in range(1, 10)]
        s, r, c = Sudoku.pos_to_indices(pos)
        while len(values) > 0:
          self.board[s][r][c] = values.pop(randint(0, len(values)-1))
          if self.__is_valid__():
            if len(positions) > 0:
              if generate_position(positions.pop(0), positions):
#                print("inner generate position returning true")
                return True
              else:
#                print("inner generate position returned false")
                continue
            else:
              return True
#          else:
#            print("self.isValid is false")
#        self.board[s][r][c] = 0
#        print("generate position returning false")
        return False
    
    while True:
      N = [i for i in range(0, 81)]
      positions = [N.pop(randint(0, len(N)-1)) for _ in range(n)]
      print(f"length of positions: {len(positions)}")
      
      generate_position(positions.pop(0), positions)
      
      print(self.to_string())
      board_cpy = self.board
      
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
  logging.debug("About to create the Sudoku Board E")
  E = Sudoku(generate=17)
  logging.info("Sudoku board generation and solution completed in %s seconds. Program is completed.", time.time() - start_time)
  
if __name__ == "__main__":
  main()