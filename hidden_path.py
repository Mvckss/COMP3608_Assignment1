import sys
from collections import deque
from typing import Dict, List, NamedTuple, Optional, Tuple


class World(NamedTuple):
    """Everything needed to run search on one map instance."""

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

def teleport_map(grid, width, height):
    def teleport_groups(grid, width, height):
        groups = {}
        for y in range(height):
            for x in range(width):
                if grid[y][x].isdigit():
                    groups[grid[y][x]] = (x, y)
        return groups

    groups = teleport_groups(grid, width, height)

    # Avoid shadowing the function name; this is entrance_coord -> exit_coord
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


def main(strategy, filename, param=None):
    world = load_world(filename)
    if world is None:
        return

    print(world)
    
    return

if __name__ == '__main__':   
    if len(sys.argv) < 3:
        # You can modify these values to test your code
        strategy = 'B'
        filename = 'example2.txt'
    else:
        strategy = sys.argv[1]
        filename = sys.argv[2]
        if len(sys.argv) > 3:
            parameter = sys.argv[3]
    main(strategy, filename)
