
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# Add the first diagonal unit ['A1', 'B2', 'C3', etc.]
unitlist.append([r+c for r,c in zip(rows,cols)])
# Add the second diagonal unit ['A9', 'B8', 'C7', etc.]
unitlist.append([r+c for r,c in zip(rows,cols[::-1])])


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
	"""Eliminate values using the naked twins strategy.

	The naked twins strategy says that if you have two or more unallocated boxes
	in a unit and there are only two digits that can go in those two boxes, then
	those two digits can be eliminated from the possible assignments of all other
	boxes in the same unit.

	Parameters
	----------
	values(dict)
		a dictionary of the form {'box_name': '123456789', ...}

	Returns
	-------
	dict
		The values dictionary with the naked twins eliminated from peers

	See Also
	--------
	Pseudocode for this algorithm on github:
	https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
	"""
	# maintain a set of visited boxes to avoid duplicate work
	visited = set()
	# deep copy to avoid propagation (we need to check the values of the unmodified version)
	out = values.copy()
	for boxA in values.keys():
		if len(values[boxA]) != 2:
			continue
		visited.add(boxA)
		for boxB in peers[boxA]:
			if boxB in visited:
				continue
			if len(values[boxB]) == 2 and values[boxB] == values[boxA]:
				for peer in peers[boxA].intersection(peers[boxB]):
					for digit in values[boxA]:
						out[peer] = out[peer].replace(digit, "")
	return out

def eliminate(values):
	"""Apply the eliminate strategy to a Sudoku puzzle

	The eliminate strategy says that if a box has a value assigned, then none
	of the peers of that box can have the same value.

	Parameters
	----------
	values(dict)
		a dictionary of the form {'box_name': '123456789', ...}

	Returns
	-------
	dict
		The values dictionary with the assigned values eliminated from peers
	"""
	solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
	for box in solved_boxes:
		digit = values[box]
		if len(digit) == 1:
			for peerBox in peers[box]:
				values[peerBox] = values[peerBox].replace(digit,'')
			
	return values


def only_choice(values):
	"""Apply the only choice strategy to a Sudoku puzzle

	The only choice strategy says that if only one box in a unit allows a certain
	digit, then that box must be assigned that digit.

	Parameters
	----------
	values(dict)
		a dictionary of the form {'box_name': '123456789', ...}

	Returns
	-------
	dict
		The values dictionary with all single-valued boxes assigned

	"""
	for unit in unitlist:
		for digit in "123456789":
			digitPlaces = [box for box in unit if digit in values[box]]
			if len(digitPlaces) == 1:
				values[digitPlaces[0]] = digit
	return values  


def reduce_puzzle(values):
	"""Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

	Parameters
	----------
	values(dict)
		a dictionary of the form {'box_name': '123456789', ...}

	Returns
	-------
	dict or False
		The values dictionary after continued application of the constraint strategies
		no longer produces any changes, or False if the puzzle is unsolvable 
	"""
	stalled = False
	while not stalled:
		# Check how many boxes have a determined value
		solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

		# Use the Eliminate Strategy
		values = eliminate(values)

		# Use the Only Choice Strategy
		values = only_choice(values)

		# Checkvalues how many boxes have a determined value, to compare
		solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
		# If no new values were added, stop the loop.
		stalled = solved_values_before == solved_values_after
		# Sanity check, return False if there is a box with zero available values:
		if len([box for box in values.keys() if len(values[box]) == 0]):
			return False
	return values


def search(values):
	"""Apply depth first search to solve Sudoku puzzles in order to solve puzzles
	that cannot be solved by repeated reduction alone.

	Parameters
	----------
	values(dict)
		a dictionary of the form {'box_name': '123456789', ...}

	Returns
	-------
	dict or False
		The values dictionary with all boxes assigned or False

	"""
	# First, reduce the puzzle using the previous function
	values = reduce_puzzle(values)
	if values is False:
		return False
	values = naked_twins(values)
	minBox = 'A1'
	minLength = 10
	# Choose one of the unfilled squares with the fewest possibilities
	for box in boxes:
		if len(values[box]) == 1:
			continue
		if len(values[box]) < minLength:
			minLength = len(values[box])
			minBox = box
	# no other work to do!
	if minLength == 10:
		return values
	minBoxValue = values[minBox]
	for digit in minBoxValue: 
		new_sudoku = values.copy()
		new_sudoku[minBox] = digit
		answer = search(new_sudoku)
		if answer:
			return answer


def solve(grid):
	"""Find the solution to a Sudoku puzzle using search and constraint propagation

	Parameters
	----------
	grid(string)
		a string representing a sudoku grid.
		
		Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

	Returns
	-------
	dict or False
		The dictionary representation of the final sudoku grid or False if no solution exists.
	"""
	values = grid2values(grid)
	values = search(values)
	return values


if __name__ == "__main__":
	diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
	display(grid2values(diag_sudoku_grid))
	result = solve(diag_sudoku_grid)
	display(result)

	try:
		import PySudoku
		PySudoku.play(grid2values(diag_sudoku_grid), result, history)

	except SystemExit:
		pass
	except:
		print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
