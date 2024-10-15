from environment.state import State
import numpy as np
from typing import Tuple

# PLEASE NOTE: There's probably a cleaner way to implement A* along with the team aware agent in general, but this still
# is a fairly straightforward and simple implementation, so hopefully it is understandable.  I also tried to insert
# comments in key places


class PathNode:
    def __init__(self, row: int, col: int, parent=None):
        self.row, self.col, self.parent = row, col, parent

        self.g, self.h, self.f = 0, 0, 0

    def position(self) -> Tuple[int, int]:
        return self.row, self.col

    def update_values(self, g: int, h: int):
        self.g, self.h, self.f = g, h, g + h

    def __eq__(self, other):
        return self.position() == other.position()

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return str((self.row, self.col))


class AStar(object):
    @staticmethod
    def find_path(curr_row: int, curr_col: int, goal_row: int, goal_col: int, state: State) -> Tuple[int, int]:
        start_node = PathNode(curr_row, curr_col)
        end_node = PathNode(goal_row, goal_col)

        open_list = [start_node]
        closed_nodes = set()

        while len(open_list) > 0:
            # Find node with smallest F score
            curr_node, idx, min_score = None, 0, np.inf

            for i, node in enumerate(open_list):
                if node.f < min_score:
                    curr_node, idx, min_score = node, i, node.f

            # Remove node with smallest F score and add it to the closed/visited list
            open_list.pop(idx)
            closed_nodes.add(curr_node)

            # Path has been found
            if curr_node == end_node:
                path = []

                while curr_node != start_node:
                    path.append(curr_node.position())
                    curr_node = curr_node.parent

                return path[-1]

            # Otherwise, continue with the algorithm - next step is to generate the children of the current node
            available_neighbors = state.neighboring_positions(curr_node.row, curr_node.col)
            children = [PathNode(row, col, curr_node) for row, col in available_neighbors]

            # Visit the children and update their g, h, and f values
            for child in children:
                if child in closed_nodes:
                    continue

                new_g, new_h = curr_node.g + 1, state.n_movements(child.row, child.col, end_node.row, end_node.col)
                child.update_values(new_g, new_h)

                for node in open_list:
                    if child == node and child.g > node.g:
                        continue

                open_list.append(child)

        # We might be unable to follow a path if we're blocked in by other agents; in that case, just stay where we are
        return curr_row, curr_col
