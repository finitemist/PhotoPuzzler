import pygame
import random
import math
import numpy as np

# Initialize pygame
pygame.init()

# Constants
FPS = 60
WIDTH, HEIGHT = 800, 800
ROWS = 4
COLS = 4
RECT_HEIGHT = HEIGHT // ROWS
RECT_WIDTH = WIDTH // COLS
OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)
FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MOVE_VEL = 20

# Create window
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 - Greedy Algorithm")


class Tile:
    COLORS = [
        (237, 229, 218), (238, 225, 201), (243, 178, 122),
        (246, 150, 101), (247, 124, 95), (247, 95, 59),
        (237, 208, 115), (237, 204, 99), (236, 202, 80)
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        return self.COLORS[color_index]

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(text, (
            self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
            self.y + (RECT_HEIGHT / 2 - text.get_height() / 2)
        ))

    def set_pos(self, ceil=False):
        self.row = math.ceil(self.y / RECT_HEIGHT) if ceil else math.floor(self.y / RECT_HEIGHT)
        self.col = math.ceil(self.x / RECT_WIDTH) if ceil else math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]


def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH, y), OUTLINE_THICKNESS)
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x, 0), (x, HEIGHT), OUTLINE_THICKNESS)
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)


def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)
    for tile in tiles.values():
        tile.draw(window)
    draw_grid(window)
    pygame.display.update()


def get_random_pos(tiles):
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)
        if f"{row}{col}" not in tiles:
            return row, col


def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOVE_VEL
        move_check = lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        ceil = True
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue
            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)

    return end_move(tiles)


def end_move(tiles):
    if len(tiles) == 16:
        return "lost"
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "continue"


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    draw(window, tiles)


def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles


def draw_game_over(window):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    window.blit(overlay, (0, 0))
    text = FONT.render("Game Over!", True, (255, 0, 0))
    window.blit(text, (
        WIDTH // 2 - text.get_width() // 2,
        HEIGHT // 2 - text.get_height() // 2
    ))
    pygame.display.update()


class GreedyAI:
    @staticmethod
    def evaluate_board(board):
        """Simple heuristic: prioritize empty tiles and merges"""
        empty = np.sum(board == 0)
        max_tile = np.max(board)

        # Count potential merges
        merges = 0
        for i in range(ROWS):
            for j in range(COLS - 1):
                if board[i, j] == board[i, j + 1] and board[i, j] != 0:
                    merges += 1
        for j in range(COLS):
            for i in range(ROWS - 1):
                if board[i, j] == board[i + 1, j] and board[i, j] != 0:
                    merges += 1

        return empty * 10 + merges * 5 + max_tile * 0.1

    @staticmethod
    def get_best_move(tiles):
        board = np.zeros((ROWS, COLS))
        for key in tiles:
            row, col = int(key[0]), int(key[1])
            board[row, col] = tiles[key].value

        best_score = -1
        best_move = None

        for direction in ["left", "right", "up", "down"]:
            new_board, valid = GreedyAI.simulate_move(board, direction)
            if not valid:
                continue
            score = GreedyAI.evaluate_board(new_board)
            if score > best_score:
                best_score = score
                best_move = direction

        return best_move if best_move else random.choice(["left", "right", "up", "down"])

    @staticmethod
    def simulate_move(board, direction):
        new_board = np.copy(board)
        valid = False

        if direction == "left":
            for i in range(ROWS):
                row = new_board[i, :]
                for j in range(1, COLS):
                    if row[j] != 0:
                        k = j
                        while k > 0 and row[k - 1] == 0:
                            row[k - 1] = row[k]
                            row[k] = 0
                            k -= 1
                            valid = True
                        if k > 0 and row[k - 1] == row[k]:
                            row[k - 1] *= 2
                            row[k] = 0
                            valid = True
        elif direction == "right":
            for i in range(ROWS):
                row = new_board[i, :]
                for j in range(COLS - 2, -1, -1):
                    if row[j] != 0:
                        k = j
                        while k < COLS - 1 and row[k + 1] == 0:
                            row[k + 1] = row[k]
                            row[k] = 0
                            k += 1
                            valid = True
                        if k < COLS - 1 and row[k + 1] == row[k]:
                            row[k + 1] *= 2
                            row[k] = 0
                            valid = True
        elif direction == "up":
            for j in range(COLS):
                col = new_board[:, j]
                for i in range(1, ROWS):
                    if col[i] != 0:
                        k = i
                        while k > 0 and col[k - 1] == 0:
                            col[k - 1] = col[k]
                            col[k] = 0
                            k -= 1
                            valid = True
                        if k > 0 and col[k - 1] == col[k]:
                            col[k - 1] *= 2
                            col[k] = 0
                            valid = True
        elif direction == "down":
            for j in range(COLS):
                col = new_board[:, j]
                for i in range(ROWS - 2, -1, -1):
                    if col[i] != 0:
                        k = i
                        while k < ROWS - 1 and col[k + 1] == 0:
                            col[k + 1] = col[k]
                            col[k] = 0
                            k += 1
                            valid = True
                        if k < ROWS - 1 and col[k + 1] == col[k]:
                            col[k + 1] *= 2
                            col[k] = 0
                            valid = True

        return new_board, valid


def main(window):
    clock = pygame.time.Clock()
    run = True
    game_state = "continue"
    tiles = generate_tiles()
    auto_play = False
    last_move_time = 0
    move_delay = 0.2

    while run:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                    last_move_time = current_time
                elif game_state != "lost" and not auto_play:
                    if event.key == pygame.K_LEFT:
                        game_state = move_tiles(window, tiles, clock, "left")
                    if event.key == pygame.K_RIGHT:
                        game_state = move_tiles(window, tiles, clock, "right")
                    if event.key == pygame.K_UP:
                        game_state = move_tiles(window, tiles, clock, "up")
                    if event.key == pygame.K_DOWN:
                        game_state = move_tiles(window, tiles, clock, "down")

        # AI move
        if auto_play and game_state != "lost" and current_time - last_move_time > move_delay:
            best_move = GreedyAI.get_best_move(tiles)
            if best_move:
                game_state = move_tiles(window, tiles, clock, best_move)
                last_move_time = current_time

        draw(window, tiles)

        if game_state == "lost":
            draw_game_over(window)
            pygame.time.delay(3000)
            run = False

    pygame.quit()


if __name__ == "__main__":
    main(WINDOW)