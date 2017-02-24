from profilers import *

assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [s + t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'],
                  ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1']]
unitlist = row_units + column_units + square_units + diagonal_units
# unitlist = row_units + column_units + square_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    empty = dict(zip(boxes, grid))
    filled = dict((key, '123456789') if value in '.' else (key, value) for key, value in empty.items())
    return filled


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

        Go through all the boxes, and whenever there is a box with a single value,
        eliminate this value from the set of values of all its peers.

        Args:
            values: Sudoku in dictionary form.
        Returns:
            Resulting Sudoku in dictionary form after eliminating values.
    """
    for box, value in values.items():
        if len(value) == 1:
            for p in peers[box]:
                assign_value(values, p, values[p].replace(value, ""))

    return values


def only_choice(values):
    """Finalize all values that are the only choice for a unit.

        Go through all the units, and whenever there is a unit with a value
        that only fits in one box, assign the value to this box.

        Args:
            values: Sudoku in dictionary form.
        Returns:
            Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
        Args:
            values(dict): a dictionary of the form {'box_name': '123456789', ...}

        Returns:
            the values dictionary with the naked twins eliminated from peers.
    """

    def find_twin(unit, box):
        """Given a unit and a box with two values, try to find a twin box.
            Args:
                unit(array): an array containing the boxes for a single unit.
                box(string): a box with two values.

            Returns:
                a twin box if one is found, False if no twin is found.
        """
        assert len(values[box]) == 2, "box must only have two values"
        for twin_box in unit:
            if twin_box != box and values[twin_box] == values[box]:
                return twin_box
        return False

    def reduce_peers(unit, twin_box):
        """Given a unit and a box with a twin, remove the twin values from the remaining unit.
            Args:
                unit(array): an array containing the boxes for a single unit.
                twin_box(string): a box with two values that has a twin.
        """
        assert len(values[twin_box]) == 2, "twin_box must only have two values"
        twin_values = values[twin_box]
        for box in unit:
            for value in twin_values:
                if value in values[box] and values[box] != twin_values:
                    assign_value(values, box, values[box].replace(value, ""))

        pass

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their unit peers
    for unit in unitlist:
        # Keep track of the discovered twins so we don't repeat ourselves
        naked_twins_discovered = []
        for box in unit:
            if box not in naked_twins_discovered and len(values[box]) == 2:
                twin_box = find_twin(unit, box)
                if twin_box:
                    naked_twins_discovered.extend([box, twin_box])
                    reduce_peers(unit, twin_box)

    return values


def naked_chain(values):
    """Eliminate values using the naked chain strategy.
        Args:
            values(dict): a dictionary of the form {'box_name': '123456789', ...}

        Returns:
            the values dictionary with the naked chain eliminated from peers.
    """
    def find_chain(unit, first_box):
        """Given a unit and a box with two values, try to find a chain of boxes.
            Args:
                unit(array): an array containing the boxes for a single unit.
                box(string): a box with two values.

            Returns:
                a chain of boxes if one is found, False if no chain is found.
        """
        assert len(values[first_box]) == 2, "box must only have two values"

        chain = []
        chain.extend([first_box])

        def can_chain(box):
            """Check if a box could potentially be part of a chain.
                Args:
                    box(string): a box with two values.

                Returns:
                    True if the box fits the chain, False if it doesn't.
            """
            for value in values[box]:
                for chain_box in chain:
                    # A box fits the chain if one of its values can be found in another box in the chain
                    if value in values[chain_box] and values[box] != values[chain_box]:
                        return True

            return False

        def verify_chain():
            """Verifies that the current chain is valid.
                Returns:
                    True if the chain is valid, False if not.
            """

            for box in chain:
                for value in values[box]:
                    match = 0
                    for review_box in chain:
                        if review_box != box and value in values[review_box]:
                            match += 1
                            # If any value in the chain has more than one match, the chain is invalid
                            if match > 1:
                                return False
                    # If any value in the chain doesn't have a match, the chain is invalid
                    if match == 0:
                        return False

            return True

        def clean_chain():
            """Removes extra boxes from the chain.
            """
            remove_boxes = []
            for box in chain:
                for value in values[box]:
                    match = 0
                    for review_box in chain:
                        if review_box != box and value in values[review_box]:
                            match += 1
                    # If a value doesn't have a match, remove the box
                    if match == 0:
                        remove_boxes.extend([box])

            for box in remove_boxes:
                chain.remove(box)

            pass

        for box in unit:
            if len(values[box]) == 2 and box not in chain and can_chain(box):
                chain.extend([box])
                if len(chain) > 2 and verify_chain():
                    return chain

        # Check if the chain has extra boxes that could be removed.
        if len(chain) > 3:
            clean_chain()
            if len(chain) > 2 and verify_chain():
                return chain

        return False

    def reduce_peers(unit, chain):
        """Given a unit and a box with a chain, remove the chain values from the remaining unit.
            Args:
                unit(array): an array containing the boxes for a single unit.
                chain_box(string): a box with two values that has a chain.
        """
        chain_values = []
        for box in chain:
            for value in values[box]:
                chain_values.extend([value])
        chain_values = set(chain_values)
        for box in unit:
            if box not in chain:
                for value in chain_values:
                    if value in values[box]:
                        assign_value(values, box, values[box].replace(value, ""))

        pass

    # Find all instances of naked chains
    # Eliminate the naked chains as possibilities for their unit peers
    for unit in unitlist:
        for box in unit:
            if len(values[box]) == 2:
                chain = find_chain(unit, box)
                if chain:
                    reduce_peers(unit, chain)

    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        values = eliminate(values)

        values = only_choice(values)

        # This strategy can reduce the total iterations required, but is generally so expensive that no time is saved
        values = naked_chain(values)

        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku."""
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)

    if values is False:
        return False

    # If there are no unsolved values, we've found a solution!
    unsolved_values = [box for box in values.keys() if len(values[box]) > 1]
    if len(unsolved_values) == 0:
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    nextBox = {}
    threshold = 2
    stop = False
    while not stop:
        for box in unsolved_values:
            if len(values[box]) == threshold:
                nextBox = box
                unsolved_values.remove(nextBox)
                stop = True
                break
        threshold += 1

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    originalValues = values[nextBox]
    for value in originalValues:
        assign_value(values, nextBox, value)
        result = search(values.copy())
        if (result):
            return result

    return False


@do_profile(follow=[reduce_puzzle, naked_chain, naked_twins, only_choice, eliminate])
def solve(grid):
    """Find the solution to a Sudoku grid.
        Args:
            grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
            The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    easy_grid = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
    hard_grid = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    very_hard_grid = '...6..2..8.4.3.........9...4.5.....771.........3.5...83...7...4.....19.....2...6.'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
