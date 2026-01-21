from .utils import in_bounds, is_walkable, neighbors4, reconstruct_path

def dfs(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    stack = [start]
    came_from = {start: None}
    visited_order = []

    while stack:
        current = stack.pop()
        visited_order.append(current)

        if current == goal:
            break

        r, c = current
        for nr, nc in neighbors4(r, c):
            if in_bounds(nr, nc, rows, cols) and is_walkable(grid, nr, nc):
                nxt = (nr, nc)
                if nxt not in came_from:
                    came_from[nxt] = current
                    stack.append(nxt)

    path = reconstruct_path(came_from, goal) if goal in came_from else []
    return {"path": path, "visited": visited_order}
