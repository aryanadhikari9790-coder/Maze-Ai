def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

def is_walkable(grid, r, c):
    # 0 = open cell, 1 = wall
    return grid[r][c] == 0

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from and came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def neighbors4(r, c):
    return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
