import heapq
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple
from collections import deque


class World(NamedTuple):

    width: int
    height: int
    start: Tuple[int, int]
    grid: List[List[str]]
    treasures: frozenset
    entrance_to_exit: Dict[Tuple[int, int], Tuple[int, int]]


def parse_file_info(filename):
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            if len(lines) < 3:
                print("Missing info")
                return None

            dimension = lines[0].strip().lower()
            start = lines[1].strip()
            grid = [list(line.strip()) for line in lines[2:]]

            dim_parts = dimension.split("x")
            if len(dim_parts) != 2:
                print(f"Invalid dimensions format: {dimension!r}")
                return None

            start_parts = start.split("-")
            if len(start_parts) != 2:
                print(f"Invalid start format: {start!r}")
                return None

            width, height = int(dim_parts[0]), int(dim_parts[1])
            sx, sy = int(start_parts[0]), int(start_parts[1])

            return width, height, (sx, sy), grid
    except Exception as e:
        print(f"Cant parse the file. Please check filename: {e}")
        return None


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    return 0 <= x < width and 0 <= y < height


def collect_treasures(grid: List[List[str]], width: int, height: int) -> frozenset:
    found = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] == "X":
                found.append((x, y))
    return frozenset(found)


def tile_at(world: World, x: int, y: int) -> str:
    return world.grid[y][x]


def is_goal(x: int, y: int, world: World) -> bool:
    return (x, y) in world.treasures


def get_neighbors(x, y, grid, width, height):    
    neighbors = []

    # LEFT
    left = (x - 1, y)
    if in_bounds(left[0], left[1], width, height) and grid[left[1]][left[0]] != "W":
        neighbors.append(left)

    # RIGHT
    right = (x + 1, y)
    if in_bounds(right[0], right[1], width, height) and grid[right[1]][right[0]] != "W":
        neighbors.append(right)

    # UP
    up = (x, y - 1)
    if in_bounds(up[0], up[1], width, height) and grid[up[1]][up[0]] != "W":
        neighbors.append(up)

    # DOWN
    down = (x, y + 1)
    if in_bounds(down[0], down[1], width, height) and grid[down[1]][down[0]] != "W":
        neighbors.append(down)

    return neighbors


def get_cost(tile):
    if tile == '.':
        return 1
    elif tile == 'M':   # Mud
        return 2
    elif tile == 'B':   # Boulder
        return 3
    elif tile.isdigit():  # teleport tiles
        return 1
    elif tile == 'X':   # treasure
        return 1
    else:
        return 1  # default (safe fallback)

def reconstruct_path(parent, start, goal):
    path = []
    current = goal

    while current != start:
        path.append(current)
        current = parent[current]

    path.append(start)
    path.reverse()

    return path


def format_expanded(expanded):
    # Matches assignment examples: tuples concatenated without commas.
    return "".join(f"({x}, {y})" for x, y in expanded)


def format_path(path):
    # Matches assignment examples: list-like formatting with comma+space.
    return "[" + ", ".join(f"({x}, {y})" for x, y in path) + "]"

def teleport_map(grid, width, height):
    def teleport_groups(grid, width, height):
        groups = {}
        for y in range(height):
            for x in range(width):
                if grid[y][x].isdigit():
                    groups[grid[y][x]] = (x, y)
        return groups

    groups = teleport_groups(grid, width, height)
    entrance_to_exit = {}
    for key, entrance_pos in groups.items():
        n = int(key)
        if n % 2 == 1 and str(n + 1) in groups:
            entrance_to_exit[entrance_pos] = groups[str(n + 1)]
    return entrance_to_exit


def load_world(filename: str) -> Optional[World]:
    parsed = parse_file_info(filename)
    if parsed is None:
        return None

    width, height, (sx, sy), grid = parsed

    if len(grid) != height:
        print(
            f"Grid height mismatch: expected {height} rows, got {len(grid)}"
        )
        return None
    for yi, row in enumerate(grid):
        if len(row) != width:
            print(
                f"Grid width mismatch on row {yi}: expected {width}, got {len(row)}"
            )
            return None

    if not in_bounds(sx, sy, width, height):
        print(f"Start ({sx}, {sy}) is out of bounds for {width}x{height}")
        return None
    if grid[sy][sx] == "W":
        print(f"Start ({sx}, {sy}) is on a wall")
        return None

    treasures = collect_treasures(grid, width, height)
    entrance_to_exit = teleport_map(grid, width, height)

    return World(
        width=width,
        height=height,
        start=(sx, sy),
        grid=grid,
        treasures=treasures,
        entrance_to_exit=entrance_to_exit,
    )


def is_teleport_entrance(x, y, entrance_to_exit):
    return (x, y) in entrance_to_exit


def get_successors(x, y, grid, width, height, entrance_to_exit):
    if is_teleport_entrance(x, y, entrance_to_exit):
        ex, ey = entrance_to_exit[(x, y)]
        return [((ex, ey), 0)]

    successors = []
    for nx, ny in get_neighbors(x, y, grid, width, height):
        successors.append(((nx, ny), get_cost(grid[ny][nx])))
    return successors


def get_successors_world(x: int, y: int, world: World):
    return get_successors(
        x, y, world.grid, world.width, world.height, world.entrance_to_exit
    )


def _manhattan_pair(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _min_manhattan_to_any_treasure(x: int, y: int, world: World) -> int:
    if not world.treasures:
        return 10**9
    return min(_manhattan_pair((x, y), t) for t in world.treasures)


def heuristic_to_nearest_treasure(x: int, y: int, world: World) -> int:
    if not world.treasures:
        return 10**9
    if (x, y) in world.entrance_to_exit:
        ex, ey = world.entrance_to_exit[(x, y)]
        return _min_manhattan_to_any_treasure(ex, ey, world)
    return _min_manhattan_to_any_treasure(x, y, world)


def path_willpower_cost(world: World, path: List[Tuple[int, int]]) -> int:
    if len(path) < 2:
        return 0
    total = 0
    for i in range(len(path) - 1):
        x, y = path[i]
        nxt = path[i + 1]
        for (nx, ny), c in get_successors_world(x, y, world):
            if (nx, ny) == nxt:
                total += c
                break
    return total


def greedy_search(world: World):
    if not world.treasures:
        return [], None, None

    start = world.start
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    closed: set = set()
    expanded: List[Tuple[int, int]] = []

    h0 = heuristic_to_nearest_treasure(start[0], start[1], world)
    tie_counter = 0
    heap: List[Tuple[int, int, int, int]] = []
    heapq.heappush(heap, (h0, start[0], start[1], tie_counter))
    tie_counter += 1

    while heap:
        _h, x, y, _tc = heapq.heappop(heap)
        if (x, y) in closed:
            continue
        closed.add((x, y))
        expanded.append((x, y))

        if is_goal(x, y, world):
            goal = (x, y)
            path = reconstruct_path(parent, start, goal)
            cost = path_willpower_cost(world, path)
            return expanded, path, cost

        for (nx, ny), _step in get_successors_world(x, y, world):
            if (nx, ny) in closed:
                continue
            if (nx, ny) in parent:
                continue
            parent[(nx, ny)] = (x, y)
            nh = heuristic_to_nearest_treasure(nx, ny, world)
            heapq.heappush(heap, (nh, nx, ny, tie_counter))
            tie_counter += 1

    return expanded, None, None


def astar_search(world: World):
    if not world.treasures:
        return [], None, None

    start = world.start
    inf = 10**18
    g_score: Dict[Tuple[int, int], int] = {start: 0}
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
    closed: set = set()
    expanded: List[Tuple[int, int]] = []

    tie_counter = 0
    heap: List[Tuple[int, int, int, int, int]] = []
    h0 = heuristic_to_nearest_treasure(start[0], start[1], world)
    heapq.heappush(heap, (h0, start[0], start[1], tie_counter, 0))
    tie_counter += 1

    while heap:
        f, x, y, tc, g = heapq.heappop(heap)
        if g != g_score.get((x, y), inf):
            continue
        if (x, y) in closed:
            continue
        closed.add((x, y))
        expanded.append((x, y))

        if is_goal(x, y, world):
            goal = (x, y)
            path = reconstruct_path(parent, start, goal)
            cost = path_willpower_cost(world, path)
            return expanded, path, cost

        for (nx, ny), step_cost in get_successors_world(x, y, world):
            if (nx, ny) in closed:
                continue
            tentative_g = g + step_cost
            if tentative_g >= g_score.get((nx, ny), inf):
                continue
            g_score[(nx, ny)] = tentative_g
            parent[(nx, ny)] = (x, y)
            nh = heuristic_to_nearest_treasure(nx, ny, world)
            nf = tentative_g + nh
            heapq.heappush(heap, (nf, nx, ny, tie_counter, tentative_g))
            tie_counter += 1

    return expanded, None, None


def beam_search(world: World, k: int):
    if not world.treasures:
        return [], None, None
    if k <= 0:
        return [], None, None

    start = world.start
    parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}

    expanded_set: set = set()
    expanded: List[Tuple[int, int]] = []

    beam: List[Tuple[int, int]] = [start]

    while beam:
        best_prev = min(
            heuristic_to_nearest_treasure(x, y, world) for (x, y) in beam
        )

        candidates: Dict[Tuple[int, int], int] = {}
        next_insertion = 0

        for (x, y) in beam:
            if (x, y) in expanded_set:
                continue
            expanded_set.add((x, y))
            expanded.append((x, y))

            if is_goal(x, y, world):
                path = reconstruct_path(parent, start, (x, y))
                cost = path_willpower_cost(world, path)
                return expanded, path, cost

            for (nx, ny), _step_cost in get_successors_world(x, y, world):
                succ = (nx, ny)

                if succ in expanded_set:
                    continue

                # Keep the first parent f ound / earliest-added successor
                if succ in candidates:
                    continue
                if succ not in parent:
                    parent[succ] = (x, y)

                candidates[succ] = next_insertion
                next_insertion += 1

        if not candidates:
            return expanded, None, None

        best_succ = min(
            heuristic_to_nearest_treasure(x, y, world) for (x, y) in candidates.keys()
        )

        if best_succ >= best_prev:
            return expanded, None, None

        cand_list: List[Tuple[int, int, int, int, Tuple[int, int]]] = []
        for (sx, sy), ins in candidates.items():
            h = heuristic_to_nearest_treasure(sx, sy, world)
            cand_list.append((h, sx, sy, ins, (sx, sy)))
        cand_list.sort()
        beam = [s for *_, s in cand_list[:k]]

    return expanded, None, None


def run_beam(world: World, k: int) -> None:
    print("Beam Search Initiated")
    expanded, path, cost = beam_search(world, k)
    print(f"Expanded: {format_expanded(expanded)}")
    if path is None:
        print("NO PATH FOUND!")
        return
    print(f"Path Found: {path}")
    print(f"Taking this path will cost: {cost} Willpower")


def format_expanded(expanded: List[Tuple[int, int]]) -> str:
    return "".join(f"({x}, {y})" for x, y in expanded)


def run_greedy(world: World) -> None:
    print("Greedy Search Initiated")
    expanded, path, cost = greedy_search(world)
    print(f"Expanded: {format_expanded(expanded)}")
    if path is None:
        print("NO PATH FOUND!")
        return
    print(f"Path Found: {path}")
    print(f"Taking this path will cost: {cost} Willpower")


def run_astar(world: World) -> None:
    print("A* Search Initiated")
    expanded, path, cost = astar_search(world)
    print(f"Expanded: {format_expanded(expanded)}")
    if path is None:
        print("NO PATH FOUND!")
        return
    print(f"Path Found: {path}")
    print(f"Taking this path will cost: {cost} Willpower")

def bfs(world):
    start = world.start
    fringe = deque([(start, None, 0)])  
    expanded = []
    expanded_set = set()
    parent = {start: None}
    path_cost = {start: 0}
    
    while fringe:
        current, parent_state, g = fringe.popleft()
        if current in expanded_set:
            continue
        expanded_set.add(current)
        expanded.append(current)
        parent[current] = parent_state
        path_cost[current] = g

        cx, cy = current

        if is_goal(cx, cy, world):
            path = reconstruct_path(parent, start, current)
            return expanded, path, path_cost[current]

        for (nx, ny), step_cost in get_successors_world(cx, cy, world):
            child = (nx, ny)
            if child in expanded_set:
                continue
            if child not in parent:
                fringe.append((child, current, path_cost[current] + step_cost))
    return expanded, None, None

def ucs(world):
    start = world.start
    sx, sy = start
    tie = 0
    # (g, x, y, tie_break_fifo, state)
    fringe = [(0, sx, sy, tie, start)]
    tie += 1

    expanded = []
    expanded_set = set()
    parent = {start: None}
    best_path_cost = {start: 0}

    while fringe:
        path_cost, _, _, _, current = heapq.heappop(fringe)
        cx, cy = current

        if current in expanded_set:
            continue

        expanded_set.add(current)
        expanded.append(current)

        if is_goal(cx, cy, world):
            path = reconstruct_path(parent, start, current)
            return expanded, path, path_cost

        for (nx, ny), step_cost in get_successors_world(cx, cy, world):
            child = (nx, ny)
            if child in expanded_set:
                continue
            new_path_cost = path_cost + step_cost
            if new_path_cost < best_path_cost.get(child, float("inf")):
                best_path_cost[child] = new_path_cost
                parent[child] = current
                heapq.heappush(fringe, (new_path_cost, nx, ny, tie, child))
                tie += 1

    return expanded, None, None

def ids(world, limit):
    limit = int(limit)

    all_expanded = []
    last_expanded = []

    for depth_limit in range(limit + 1):  # inclusive (0..l)
        expanded, path, total_cost = dls(world, depth_limit)
        all_expanded.extend(expanded)
        last_expanded = expanded

        if path is not None:
            return all_expanded, path, total_cost

    return all_expanded if all_expanded else last_expanded, None, None


def dls(world, depth_limit):
    start = world.start
    # (state, depth, parent_state, cumulative_cost)
    stack = [(start, 0, None, 0)]

    expanded = []
    expanded_set = set()
    parent = {start: None}
    path_cost = {start: 0}

    while stack:
        current, current_depth, parent_state, g = stack.pop()

        if current_depth > depth_limit:
            continue
        if current in expanded_set:
            continue

        expanded_set.add(current)
        expanded.append(current)
        parent[current] = parent_state
        path_cost[current] = g

        cx, cy = current
        if is_goal(cx, cy, world):
            path = reconstruct_path(parent, start, current)
            return expanded, path, g

        successors = get_successors_world(cx, cy, world)
        for (child_state, step_cost) in reversed(successors):
            nx, ny = child_state
            stack.append((child_state, current_depth + 1, current, g + step_cost))

    return expanded, None, None

def print_search_result(strategy_name, expanded, path, total_cost):
    print(f"{strategy_name} Search Initiated")
    print(f"Expanded: {format_expanded(expanded)}")
    if path is None:
        print("NO PATH FOUND!")
        return
    print(f"Path Found: {format_path(path)}")
    print(f"Taking this path will cost: {total_cost} Willpower")

def main(strategy, filename, param=None):
    world = load_world(filename)
    if world is None:
        return

    if strategy == "B":
        expanded, path, total_cost = bfs(world)
        print_search_result("BFS", expanded, path, total_cost)
        return

    elif strategy == "U":
        expanded, path, total_cost = ucs(world)
        print_search_result("UCS", expanded, path, total_cost)
        return
    elif strategy == "I":
        expanded, path, total_cost = ids(world, param)
        print_search_result("IDS", expanded, path, total_cost)
        return
    elif strategy == "G":
        expanded, path, total_cost = greedy_search(world)
        print_search_result("Greedy", expanded, path, total_cost)
        return
    elif strategy == "A":
        expanded, path, total_cost = astar_search(world)
        print_search_result("A*", expanded, path, total_cost)
        return
    elif strategy == "M":
        expanded, path, total_cost = beam_search(world, int(param))
        print_search_result("Beam", expanded, path, total_cost)
        return
    print(f"Strategy '{strategy}' not implemented yet.")
    return

if __name__ == '__main__':   
    parameter = None
    if len(sys.argv) < 3:
        strategy = 'G'
        filename = 'example2.txt'
        parameter = 5
        main(strategy, filename, parameter)
    else:
        strategy = sys.argv[1]
        filename = sys.argv[2]
        if len(sys.argv) > 3:
            parameter = sys.argv[3]
            main(strategy, filename, parameter)
        else:
            main(strategy, filename)
