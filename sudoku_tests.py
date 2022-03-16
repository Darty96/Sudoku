# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 10:51:07 2022

@author: dmdra
"""

"""
168457932
572391468
934628517
829743156
651289374
743516289
395872641
417965823
286134795
"""

from sudoku import Sudoku
import logging, logging.config

#logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S", level=logging.DEBUG, filename="sudoku_tests.log", filemode="w")

logging.config.fileConfig('logging.conf')

logger = logging.getLogger('sudokuTest')

def test_sudoku_init_from_file():
  # Arrange
  logger.info("Beginning test: test_sudoku_init_from_file")
  test_file_name = "sudoku_test_00.txt"
  expected_square_zero =  [[[1,6,8], 
                            [5,7,2], 
                            [9,3,4]
                            ]]
  expected_square_eight = [[[6,4,1], 
                            [8,2,3], 
                            [7,9,5]
                            ]]
  
  # Act
  Actual = Sudoku(filename = test_file_name)
  
  # Assert
  logger.debug("  Beginning assertions")
  assert (Actual.board[0] == expected_square_zero).all()
  assert (Actual.board[8] == expected_square_eight).all()
  logger.info("End of test: test_sudoku_init_from_file. Result: Passed")

def main():
  logger.info("Beginning test run")
  
  test_sudoku_init_from_file()
  
  logger.info("Finished test run")

if __name__ == "__main__":
  main()