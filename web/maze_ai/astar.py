import heapq
from .utils import in_bounds, is_walkable, neighbors4, reconstruct_path

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    # Heap items: (f_score, g_score, node)
    open_heap = []
    heapq.heappush(open_heap, (manhattan(start, goal), 0, start))

    came_from = {start: None}
    g_score = {start: 0}
    visited_order = []

    # NOTE: We do NOT use a permanent closed-set that blocks improvements.
    # We allow revisiting if we find a better g_score (relaxation).
    while open_heap:
        f, g, current = heapq.heappop(open_heap)

        # If this heap entry is outdated, skip it
        if g != g_score.get(current, float("inf")):
            continue

        visited_order.append(current)

        if current == goal:
            break

        r, c = current
        for nr, nc in neighbors4(r, c):
            if not in_bounds(nr, nc, rows, cols):
                continue
            if not is_walkable(grid, nr, nc):
                continue

            neighbor = (nr, nc)
            tentative_g = g_score[current] + 1

            # Relaxation step (this fixes "skipping behind" issues)
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan(neighbor, goal)
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

    path = reconstruct_path(came_from, goal) if goal in came_from else []
    return {"path": path, "visited": visited_order}
