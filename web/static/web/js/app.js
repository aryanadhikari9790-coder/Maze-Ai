const gridEl = document.getElementById("grid");
const algoEl = document.getElementById("algo");
const statsEl = document.getElementById("stats");
const compareBox = document.getElementById("compareBox");

const rowsInput = document.getElementById("rows");
const colsInput = document.getElementById("cols");
const densityInput = document.getElementById("density");

let rows = parseInt(rowsInput.value, 10);
let cols = parseInt(colsInput.value, 10);

let grid = [];
let start = [0, 0];
let goal = [rows - 1, cols - 1];

function makeEmptyGrid() {
  grid = Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0));
}

function renderGrid() {
  gridEl.style.gridTemplateColumns = `repeat(${cols}, 22px)`;
  gridEl.innerHTML = "";
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      if (grid[r][c] === 1) cell.classList.add("wall");
      if (r === start[0] && c === start[1]) cell.classList.add("start");
      if (r === goal[0] && c === goal[1]) cell.classList.add("goal");
      cell.dataset.r = r;
      cell.dataset.c = c;
      gridEl.appendChild(cell);
    }
  }
}

function cellAt(r, c) {
  return gridEl.querySelector(`.cell[data-r="${r}"][data-c="${c}"]`);
}

function clearMarks() {
  document.querySelectorAll(".visited,.path").forEach(el => {
    el.classList.remove("visited", "path");
  });
  compareBox.innerHTML = "";
}

async function generateMaze() {
  rows = Math.max(5, Math.min(60, parseInt(rowsInput.value || "20", 10)));
  cols = Math.max(5, Math.min(80, parseInt(colsInput.value || "25", 10)));
  const density = Math.max(5, Math.min(45, parseInt(densityInput.value || "28", 10))) / 100;

  start = [0, 0];
  goal = [rows - 1, cols - 1];

  const t0 = performance.now();
  const res = await fetch("/api/generate/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rows, cols, density, start, goal })
  });
  const data = await res.json();
  const t1 = performance.now();

  if (data.error) {
    alert(data.error);
    return;
  }

  grid = data.grid;
  renderGrid();
  clearMarks();

  statsEl.textContent = `Maze generated in ${data.gen_time_ms} ms (client total ${Math.round(t1 - t0)} ms)`;
}

async function solve() {
  clearMarks();
  const t0 = performance.now();

  const res = await fetch("/api/solve/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid, start, goal, algo: algoEl.value })
  });

  const data = await res.json();
  const t1 = performance.now();

  if (data.error) {
    alert(data.error);
    return;
  }

  statsEl.textContent = `Solve (${algoEl.value.toUpperCase()}): ${data.time_ms} ms | Visited: ${data.visited_count} | Path: ${data.path_length} | Client total: ${Math.round(t1 - t0)} ms`;

  const visited = data.visited || [];
  const path = data.path || [];

  for (let i = 0; i < visited.length; i++) {
    const [r, c] = visited[i];
    const el = cellAt(r, c);
    if (el && !el.classList.contains("start") && !el.classList.contains("goal")) el.classList.add("visited");
    await new Promise(r => setTimeout(r, 6));
  }

  for (let i = 0; i < path.length; i++) {
    const [r, c] = path[i];
    const el = cellAt(r, c);
    if (el && !el.classList.contains("start") && !el.classList.contains("goal")) el.classList.add("path");
    await new Promise(r => setTimeout(r, 18));
  }
}

async function compareAll() {
  clearMarks();

  const res = await fetch("/api/compare/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid, start, goal })
  });

  const data = await res.json();
  if (data.error) {
    alert(data.error);
    return;
  }

  const results = data.results || [];
  compareBox.innerHTML = `<b>Comparison (sorted by time)</b>` +
    results.map(r => `
      <div class="compareRow">
        <div>${r.algo}</div>
        <div>${r.time_ms} ms | visited ${r.visited_count} | path ${r.path_length}</div>
      </div>
    `).join("");
}

document.getElementById("generate").onclick = () => generateMaze();
document.getElementById("solve").onclick = () => solve();
document.getElementById("compare").onclick = () => compareAll();
document.getElementById("reset").onclick = () => { makeEmptyGrid(); renderGrid(); clearMarks(); statsEl.textContent=""; };

makeEmptyGrid();
renderGrid();
