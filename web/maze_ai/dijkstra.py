import heapq
from .utils import in_bounds, is_walkable, neighbors4, reconstruct_path

def dijkstra(grid, start, goal):
    rows, cols = len(grid), len(grid[0])

    pq = [(0, start)]
    dist = {start: 0}
    came_from = {start: None}
    visited_order = []

    while pq:
        current_dist, current = heapq.heappop(pq)

        # Skip outdated entries
        if current_dist != dist.get(current, float("inf")):
            continue

        visited_order.append(current)

        if current == goal:
            break

        r, c = current
        for nr, nc in neighbors4(r, c):
            if in_bounds(nr, nc, rows, cols) and is_walkable(grid, nr, nc):
                nxt = (nr, nc)
                new_cost = current_dist + 1  # uniform cost
                if new_cost < dist.get(nxt, float("inf")):
                    dist[nxt] = new_cost
                    came_from[nxt] = current
                    heapq.heappush(pq, (new_cost, nxt))

    path = reconstruct_path(came_from, goal) if goal in came_from else []
    return {"path": path, "visited": visited_order}
