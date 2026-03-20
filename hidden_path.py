import sys

def parse_file_info(filename):
    try:
        with open(f"{filename}", "r") as f:
            lines = f.readlines()
            if len(lines) < 3:
                print("Missing info")
                return None

            dimension = lines[0].strip()
            start = lines[1].strip()
            grid = [list(line.strip()) for line in lines[2:]]


            return dimension, start, grid
    except Exception as e:
        print(f"Cant parse the file. Please check filename: {e}")
        return None

def get_neighbors(x, y, grid, width, height):    
    neighbors = []

    # LEFT
    if x-1 >= 0:
        if grid[y][x-1] != 'W':
            neighbors.append((x-1, y))

    # RIGHT
    if x+1 < width :
        if grid[y][x+1] != 'W':
            neighbors.append((x+1, y))

    # UP
    if y-1 >= 0:
        if grid[y-1][x] != 'W':
            neighbors.append((x, y-1))

    # DOWN
    if y+1 < height:
        if grid[y+1][x] != 'W':
            neighbors.append((x, y+1))

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

def teleport() # Try to code 

def main(strategy, filename, param=None):
    if parse_file_info(filename) is None:
        return None

    dimension, start, grid = parse_file_info(filename)
    width, height = map(int, dimension.split('x'))

    print(dimension)
    print(start)
    print(grid)
    
    return

if __name__ == '__main__':   
    if len(sys.argv) < 3:
        # You can modify these values to test your code
        strategy = 'B'
        filename = 'example1.txt'
    else:
        strategy = sys.argv[1]
        filename = sys.argv[2]
        if sys.argv[3]:
            parameter = sys.argv[3]
    main(strategy, filename)
