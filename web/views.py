import json
import time
import random
from collections import deque

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .maze_ai.bfs import bfs
from .maze_ai.dfs import dfs
from .maze_ai.dijkstra import dijkstra
from .maze_ai.astar import astar


def home(request):
    return render(request, "web/index.html")


def _has_path(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    q = deque([start])
    seen = {start}

    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return True

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                nxt = (nr, nc)
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)

    return False


@csrf_exempt
def generate_maze(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        rows = int(data.get("rows", 20))
        cols = int(data.get("cols", 25))
        density = float(data.get("density", 0.28))
        start = tuple(data.get("start", [0, 0]))
        goal = tuple(data.get("goal", [rows - 1, cols - 1]))
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    # safety limits
    rows = max(5, min(rows, 60))
    cols = max(5, min(cols, 80))
    density = max(0.05, min(density, 0.45))

    # fix goal if rows/cols changed
    if goal[0] >= rows or goal[1] >= cols:
        goal = (rows - 1, cols - 1)
    if start[0] >= rows or start[1] >= cols:
        start = (0, 0)

    t0 = time.perf_counter()

    # Try up to 200 random mazes until one has a valid path
    for _ in range(200):
        grid = [[0 for _ in range(cols)] for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                if (r, c) == start or (r, c) == goal:
                    continue
                grid[r][c] = 1 if random.random() < density else 0

        if _has_path(grid, start, goal):
            t1 = time.perf_counter()
            return JsonResponse({
                "grid": grid,
                "rows": rows,
                "cols": cols,
                "start": [start[0], start[1]],
                "goal": [goal[0], goal[1]],
                "gen_time_ms": round((t1 - t0) * 1000, 3)
            })

    # fallback open grid if unlucky
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    t1 = time.perf_counter()
    return JsonResponse({
        "grid": grid,
        "rows": rows,
        "cols": cols,
        "start": [start[0], start[1]],
        "goal": [goal[0], goal[1]],
        "gen_time_ms": round((t1 - t0) * 1000, 3),
        "note": "Fallback open grid used"
    })


@csrf_exempt
def solve_maze(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        grid = data["grid"]
        start = tuple(data["start"])
        goal = tuple(data["goal"])
        algo = data["algo"]
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    t0 = time.perf_counter()

    if algo == "bfs":
        result = bfs(grid, start, goal)
    elif algo == "dfs":
        result = dfs(grid, start, goal)
    elif algo == "dijkstra":
        result = dijkstra(grid, start, goal)
    elif algo == "astar":
        result = astar(grid, start, goal)
    else:
        return JsonResponse({"error": "Unknown algorithm"}, status=400)

    t1 = time.perf_counter()

    # tuples -> lists for JSON
    path = [[r, c] for (r, c) in result.get("path", [])]
    visited = [[r, c] for (r, c) in result.get("visited", [])]

    return JsonResponse({
        "path": path,
        "visited": visited,
        "time_ms": round((t1 - t0) * 1000, 3),
        "visited_count": len(visited),
        "path_length": len(path),
    })


@csrf_exempt
def compare_algos(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        grid = data["grid"]
        start = tuple(data["start"])
        goal = tuple(data["goal"])
    except Exception:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    def run_one(name, fn):
        t0 = time.perf_counter()
        out = fn(grid, start, goal)
        t1 = time.perf_counter()
        return {
            "algo": name,
            "time_ms": round((t1 - t0) * 1000, 3),
            "visited_count": len(out.get("visited", [])),
            "path_length": len(out.get("path", [])),
        }

    results = [
        run_one("BFS", bfs),
        run_one("DFS", dfs),
        run_one("Dijkstra", dijkstra),
        run_one("A*", astar),
    ]

    results_sorted = sorted(results, key=lambda x: x["time_ms"])

    return JsonResponse({"results": results_sorted})
