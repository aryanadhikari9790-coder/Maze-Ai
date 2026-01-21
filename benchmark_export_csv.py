"""
benchmark_export_csv.py

Batch-runs BFS, DFS, Dijkstra, and A* on random mazes and exports results to CSV.

Run from the folder containing manage.py:
    python benchmark_export_csv.py

Outputs:
    results.csv
"""

from __future__ import annotations

import csv
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional

# --- Import your algorithms (based on your zip structure) ---
# If imports fail, see the "If you get an import error" note below.
from web.maze_ai.bfs import bfs
from web.maze_ai.dfs import dfs
from web.maze_ai.dijkstra import dijkstra
from web.maze_ai.astar import astar

Coord = Tuple[int, int]
Grid = List[List[int]]  # 0 = open, 1 = wall


@dataclass
class RunResult:
    algorithm: str
    success: int
    runtime_ms: float
    visited_count: int
    path_length: int


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors_4(r: int, c: int, n: int) -> List[Coord]:
    out = []
    if r > 0:
        out.append((r - 1, c))
    if r < n - 1:
        out.append((r + 1, c))
    if c > 0:
        out.append((r, c - 1))
    if c < n - 1:
        out.append((r, c + 1))
    return out


def has_path_bfs(grid: Grid, start: Coord, goal: Coord) -> bool:
    """Small internal BFS to ensure solvable mazes in the benchmark."""
    n = len(grid)
    q = [start]
    seen = {start}
    while q:
        r, c = q.pop(0)
        if (r, c) == goal:
            return True
        for nr, nc in neighbors_4(r, c, n):
            if (nr, nc) not in seen and grid[nr][nc] == 0:
                seen.add((nr, nc))
                q.append((nr, nc))
    return False


def generate_maze(n: int, wall_density: float, start: Coord, goal: Coord, max_tries: int = 200) -> Grid:
    """
    Generates a random maze with given wall density.
    Ensures start/goal are open and the maze is solvable.
    """
    assert 0 <= wall_density <= 1
    for _ in range(max_tries):
        grid: Grid = [[0 for _ in range(n)] for _ in range(n)]
        for r in range(n):
            for c in range(n):
                if (r, c) in (start, goal):
                    continue
                grid[r][c] = 1 if random.random() < wall_density else 0

        # quick solvability check
        if has_path_bfs(grid, start, goal):
            return grid

    # If we fail to generate a solvable maze, return the last grid anyway.
    # The algorithms will record "success=0" for no-solution cases.
    return grid


def run_one(algorithm_name: str, grid: Grid, start: Coord, goal: Coord) -> RunResult:
    """
    Calls your algorithm functions and extracts visited + path.
    Assumes each algorithm returns something like:
        visited, path
    OR a dict with keys containing visited/path.
    """
    t0 = time.perf_counter()

    output = None
    if algorithm_name == "BFS":
        output = bfs(grid, start, goal)
    elif algorithm_name == "DFS":
        output = dfs(grid, start, goal)
    elif algorithm_name == "Dijkstra":
        output = dijkstra(grid, start, goal)
    elif algorithm_name == "A*":
        output = astar(grid, start, goal)
    else:
        raise ValueError("Unknown algorithm")

    dt_ms = (time.perf_counter() - t0) * 1000.0

    visited: List[Coord] = []
    path: List[Coord] = []

    # Try to support common return formats
    if isinstance(output, dict):
        # common key names
        for k in ["visited", "visited_order", "explored"]:
            if k in output:
                visited = output[k]
                break
        for k in ["path", "solution", "final_path"]:
            if k in output:
                path = output[k]
                break
    elif isinstance(output, (list, tuple)):
        if len(output) >= 2:
            visited = output[0] or []
            path = output[1] or []
        elif len(output) == 1:
            # some implementations only return path
            path = output[0] or []

    success = 1 if path and path[0] == start and path[-1] == goal else 0
    visited_count = len(visited) if visited else 0
    path_length = max(0, len(path) - 1) if path else 0

    return RunResult(
        algorithm=algorithm_name,
        success=success,
        runtime_ms=dt_ms,
        visited_count=visited_count,
        path_length=path_length,
    )


def main():
    random.seed(42)

    # --- Settings you can change easily ---
    sizes = [10, 20, 30]            # grid sizes (N x N)
    densities = [0.10, 0.20, 0.30]  # wall density (0-1)
    trials_per_setting = 20         # number of mazes per size/density
    algorithms = ["BFS", "DFS", "Dijkstra", "A*"]

    start = (0, 0)

    # Output CSV
    out_csv = "results.csv"
    fieldnames = [
        "maze_id",
        "size",
        "density",
        "algorithm",
        "success",
        "runtime_ms",
        "visited_count",
        "path_length",
    ]

    maze_id = 0
    rows: List[Dict[str, Any]] = []

    for n in sizes:
        goal = (n - 1, n - 1)
        for dens in densities:
            for _ in range(trials_per_setting):
                maze_id += 1
                grid = generate_maze(n, dens, start, goal)

                for algo in algorithms:
                    r = run_one(algo, grid, start, goal)
                    rows.append(
                        {
                            "maze_id": maze_id,
                            "size": n,
                            "density": int(dens * 100),
                            "algorithm": r.algorithm,
                            "success": r.success,
                            "runtime_ms": round(r.runtime_ms, 4),
                            "visited_count": r.visited_count,
                            "path_length": r.path_length,
                        }
                    )

                print(f"Done maze {maze_id}: size={n}, density={int(dens*100)}%")

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nSaved: {out_csv}")
    print("Tip: Use this file to create charts (runtime, visited_count, path_length).")


if __name__ == "__main__":
    main()
