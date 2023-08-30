import math
import random
import pygame

# constants
window_width = 750
window_height = 750
columns = 50
rows = 50
node_width = window_width // columns
node_height = window_height // rows

# pygame initalisation
pygame.init()
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Pathfinder")
clock = pygame.time.Clock()

# classes
class Node:
    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.start = False
        self.end = False
        self.wall = False
        self.queued = False
        self.visited = False
        self.prior = None
        self.g = float('inf')
        self.neighbours = []

    def draw(self, window, colour):
        pygame.draw.rect(window, colour, (self.i*node_width, self.j*node_height, node_width-1, node_height-1))

    def set_neighbours(self):
        if self.i > 0:
            self.neighbours.append(grid[self.i - 1][self.j])
        if self.i < columns - 1:
            self.neighbours.append(grid[self.i + 1][self.j])
        if self.j > 0:
            self.neighbours.append(grid[self.i][self.j - 1])
        if self.j < rows - 1:
            self.neighbours.append(grid[self.i][self.j + 1])

# helper functions
def init_grid(grid):
    # create grid
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(Node(i, j))
        grid.append(row)

    # set neighbours
    for i in range(rows):
        for j in range(columns):
            grid[i][j].set_neighbours()

def draw_grid(grid):
    for i in range(rows):
        for j in range(columns):
            node = grid[i][j]
            if node.start:
                node.draw(window, (0, 255, 0))
            elif node.end:
                node.draw(window, (255, 0, 0))
            elif node.wall:
                node.draw(window, (150, 150, 150))
            elif node in path:
                node.draw(window, (255, 255, 255))
            elif node.visited:
                node.draw(window, (210, 174, 145))
            elif node.queued:
                node.draw(window, (239, 220, 204))
            else:
                node.draw(window, (30, 30, 30))

def reset_grid(grid):
    for row in grid:
        for node in row:
            node.start = False
            node.end = False
            node.wall = False
            node.queued = False
            node.visited = False
            node.prior = None
            node.g = float('inf')

def draw_initial_info(window):
    font = pygame.font.Font(None, 30)
    messages = [
        "_Controls_",
        "Left Click - Wall",
        "Right Click - Start/End",
        "Space Bar - Pause/Unpause Algorithm",
        "R - Reset",
        "M - Generate Maze",
        "",
        "_Algorithms_",
        "D - Dijkstra's Algorithm",
        "A - A* Algorithm",
        "B - Breadth First Search",
        "T - Depth First Search",
        "",
        "Press any button to continue"
    ]

    y_offset = window_height // 2 - len(messages) * 30 // 2

    for message in messages:
        text = font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect(center=(window_width // 2, y_offset))
        window.blit(text, text_rect)
        y_offset += 30

    pygame.display.flip()

def display_control_information(window):
    draw_initial_info(window)
    user_ready = False
    while not user_ready:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                user_ready = True

def heuristic(node, target_node):
    return math.sqrt((target_node.i - node.i)**2 + (target_node.j - node.j)**2)

def generate_maze(grid, start_node, end_node):
    for row in grid:
        for node in row:
            node.wall = True

    stack = [(start_node.i, start_node.j)]
    while stack:
        current_i, current_j = stack[-1]
        node = grid[current_i][current_j]
        node.wall = False

        unvisited_neighbours = []
        for ni, nj in [(current_i + 2, current_j), (current_i - 2, current_j), (current_i, current_j + 2), (current_i, current_j - 2)]:
            if 0 <= ni < rows and 0 <= nj < columns and grid[ni][nj].wall:
                unvisited_neighbours.append((ni, nj))

        if unvisited_neighbours:
            next_i, next_j = random.choice(unvisited_neighbours)
            stack.append((next_i, next_j))
            mid_i, mid_j = (current_i + next_i) // 2, (current_j + next_j) // 2
            grid[mid_i][mid_j].wall = False
        else:
            stack.pop()

# algorithms
def dijkstras_algorithm(queue, path, target_node, found_end_node):
    if len(queue) > 0 and not found_end_node:
        current_node = queue.pop(0)
        current_node.visited = True

        if current_node == target_node:
            found_end_node = True
            while not current_node.prior.start:
                path.append(current_node.prior)
                current_node = current_node.prior
        else:
            for neighbour in current_node.neighbours:
                if not neighbour.queued and not neighbour.wall:
                    neighbour.queued = True
                    neighbour.prior = current_node
                    queue.append(neighbour)
    return found_end_node

def a_star(queue, path, target_node, found_end_node):
    if len(queue) > 0 and not found_end_node:
        # sort the queue based on the total cost (g + h)
        queue.sort(key=lambda node: (node.prior.g + heuristic(node, target_node)) if node.prior else float('inf'))
        current_node = queue.pop(0)
        current_node.visited = True
        
        if current_node == target_node:
            found_end_node = True
            while not current_node.prior.start:
                path.append(current_node.prior)
                current_node = current_node.prior
        else:
            for neighbour in current_node.neighbours:
                if not neighbour.queued and not neighbour.wall:
                    neighbour.queued = True
                    neighbour.prior = current_node
                    neighbour.g = current_node.g + 1 
                    queue.append(neighbour)
    return found_end_node

def breadth_first_search(queue, path, target_node, found_end_node):
    return dijkstras_algorithm(queue, path, target_node, found_end_node)

def depth_first_search(queue, path, target_node, found_end_node):
    if len(queue) > 0 and not found_end_node:
        current_node = queue.pop()
        current_node.visited = True
        
        if current_node == target_node:
            found_end_node = True
            while not current_node.prior.start:
                path.append(current_node.prior)
                current_node = current_node.prior
        else:
            for neighbour in current_node.neighbours:
                if not neighbour.queued and not neighbour.wall:
                    neighbour.queued = True
                    neighbour.prior = current_node
                    queue.append(neighbour)
    return found_end_node
    

# main function
def main(grid, queue, path):
    begin_search = False
    start_node_set = False
    end_node_set = False
    found_end_node = False
    target_node = None
    end_node = None
    algorithm = None
    paused = False

    init_grid(grid)

    while True:
        # listening for user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            
            # set wall, start and end while mouse is not moving
            if event.type == pygame.MOUSEBUTTONDOWN and not begin_search:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]
                i = x // node_width
                j = y // node_height
                node = grid[i][j]
                # set wall
                if event.button == 1 and not node.start and not node.end:
                    node.wall = True
                # set start and end
                if event.button == 3 and not node.wall:
                    if not start_node_set:
                        node.start = True
                        node.g = 0
                        queue.append(node)
                        start_node_set = True
                    elif not end_node_set and not node.start:
                        node.end = True
                        target_node = node
                        end_node_set = True

            # set wall while mouse is moving
            if event.type == pygame.MOUSEMOTION and not begin_search:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]
                i = x // node_width
                j = y // node_height
                node = grid[i][j]
                # set wall
                if event.buttons[0] and not node.start and not node.end:
                    node.wall = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R key for resetting
                    begin_search = False
                    start_node_set = False
                    end_node_set = False
                    found_end_node = False
                    target_node = None
                    end_node = None
                    algorithm = None
                    paused = False
                    reset_grid(grid)
                    queue.clear()
                    path.clear()

                if event.key == pygame.K_SPACE: # space bar for pausing/unpausing
                    if algorithm:
                        paused = not paused
                
                if event.key == pygame.K_m and start_node_set and end_node_set and not begin_search:  # M key for maze generation
                    generate_maze(grid, target_node, end_node)

            # picking pathfinding algorithm to perform
            if event.type == pygame.KEYDOWN and start_node_set and end_node_set and not begin_search and not paused:
                if event.key == pygame.K_d: # D key for Dijkstra's algorithm
                    algorithm = "dijkstras"
                    begin_search = True
                elif event.key == pygame.K_a: # A key for A* algorithm
                    algorithm = "A*"
                    begin_search = True
                elif event.key == pygame.K_b: # B key for BFS algorithm
                    algorithm = "breadth_first_search"
                    begin_search = True
                elif event.key == pygame.K_t: # T key for DFS algorithm
                    algorithm = "depth_first_search"
                    begin_search = True

        # perform chosen algorithm
        if begin_search and not found_end_node and not paused:

            if algorithm == "dijkstras":
                found_end_node = dijkstras_algorithm(queue, path, target_node, found_end_node)
                if len(queue) == 0: found_end_node = True # no path found

            elif algorithm == "A*":
                found_end_node = a_star(queue, path, target_node, found_end_node)
                if len(queue) == 0: found_end_node = True

            elif algorithm == "breadth_first_search":
                found_end_node = breadth_first_search(queue, path, target_node, found_end_node)
                if len(queue) == 0: found_end_node = True
            
            elif algorithm == "depth_first_search":
                found_end_node = depth_first_search(queue, path, target_node, found_end_node)
                if len(queue) == 0: found_end_node = True
     
        window.fill((0, 0, 0))
        draw_grid(grid)
        pygame.display.flip()
        clock.tick(60)

grid = []
queue = []
path = []
display_control_information(window)
main(grid, queue, path)