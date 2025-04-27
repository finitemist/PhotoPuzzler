import pygame
import random
import math
import numpy as np
import time

pygame.init()

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

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")


class Tile:
    COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.COLORS[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
            (
                self.x + (RECT_WIDTH / 2 - text.get_width() / 2),
                self.y + (RECT_HEIGHT / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

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
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + RECT_WIDTH + MOVE_VEL
        )
        ceil = True
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.x + RECT_WIDTH + MOVE_VEL < next_tile.x
        )
        ceil = False
    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + RECT_HEIGHT + MOVE_VEL
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOVE_VEL
        move_check = (
            lambda tile, next_tile: tile.y + RECT_HEIGHT + MOVE_VEL < next_tile.y
        )
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
    window.blit(
        text,
        (
            WIDTH // 2 - text.get_width() // 2,
            HEIGHT // 2 - text.get_height() // 2,
        ),
    )
    pygame.display.update()


class AI:
    @staticmethod
    def get_board_state(tiles):
        board = np.zeros((ROWS, COLS), dtype=int)
        for key in tiles:
            row = int(key[0])
            col = int(key[1])
            board[row, col] = tiles[key].value
        return board

    @staticmethod
    def evaluate(board):
        # Heuristic function that evaluates the board state
        empty = np.sum(board == 0)
        smoothness = AI.get_smoothness(board)
        monotonicity = AI.get_monotonicity(board)
        max_tile = np.max(board)

        # Weightings for each heuristic
        weights = {
            'empty': 10,
            'smoothness': 0.1,
            'monotonicity': 1.0,
            'max_tile': 1.0
        }

        return (empty * weights['empty'] +
                smoothness * weights['smoothness'] +
                monotonicity * weights['monotonicity'] +
                max_tile * weights['max_tile'])

    @staticmethod
    def get_smoothness(board):
        smoothness = 0
        for i in range(ROWS):
            for j in range(COLS):
                if board[i, j] != 0:
                    val = math.log2(board[i, j])
                    # Check right and down neighbors
                    for dx, dy in [(1, 0), (0, 1)]:
                        x, y = i + dx, j + dy
                        if x < ROWS and y < COLS and board[x, y] != 0:
                            neighbor_val = math.log2(board[x, y])
                            smoothness -= abs(val - neighbor_val)
        return smoothness

    @staticmethod
    def get_monotonicity(board):
        totals = [0, 0, 0, 0]  # Left/right and up/down directions

        # Left/right direction
        for i in range(ROWS):
            current = 0
            next = current + 1
            while next < COLS:
                while next < COLS and board[i, next] == 0:
                    next += 1
                if next >= COLS:
                    next -= 1
                current_val = math.log2(board[i, current]) if board[i, current] != 0 else 0
                next_val = math.log2(board[i, next]) if board[i, next] != 0 else 0
                if current_val > next_val:
                    totals[0] += next_val - current_val
                elif next_val > current_val:
                    totals[1] += current_val - next_val
                current = next
                next += 1

        # Up/down direction
        for j in range(COLS):
            current = 0
            next = current + 1
            while next < ROWS:
                while next < ROWS and board[next, j] == 0:
                    next += 1
                if next >= ROWS:
                    next -= 1
                current_val = math.log2(board[current, j]) if board[current, j] != 0 else 0
                next_val = math.log2(board[next, j]) if board[next, j] != 0 else 0
                if current_val > next_val:
                    totals[2] += next_val - current_val
                elif next_val > current_val:
                    totals[3] += current_val - next_val
                current = next
                next += 1

        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    @staticmethod
    def get_possible_moves(board):
        moves = []
        for direction in ["left", "right", "up", "down"]:
            new_board, valid = AI.move_board(board, direction)
            if valid:
                moves.append((direction, new_board))
        return moves

    @staticmethod
    def move_board(board, direction):
        # Create a copy of the board to manipulate
        new_board = np.copy(board)
        valid = False

        if direction == "left":
            for i in range(ROWS):
                row = new_board[i, :]
                merged = [False] * COLS
                for j in range(1, COLS):
                    if row[j] != 0:
                        k = j
                        while k > 0 and row[k - 1] == 0:
                            row[k - 1] = row[k]
                            row[k] = 0
                            k -= 1
                            valid = True
                        if k > 0 and row[k - 1] == row[k] and not merged[k - 1]:
                            row[k - 1] *= 2
                            row[k] = 0
                            merged[k - 1] = True
                            valid = True
        elif direction == "right":
            for i in range(ROWS):
                row = new_board[i, :]
                merged = [False] * COLS
                for j in range(COLS - 2, -1, -1):
                    if row[j] != 0:
                        k = j
                        while k < COLS - 1 and row[k + 1] == 0:
                            row[k + 1] = row[k]
                            row[k] = 0
                            k += 1
                            valid = True
                        if k < COLS - 1 and row[k + 1] == row[k] and not merged[k + 1]:
                            row[k + 1] *= 2
                            row[k] = 0
                            merged[k + 1] = True
                            valid = True
        elif direction == "up":
            for j in range(COLS):
                col = new_board[:, j]
                merged = [False] * ROWS
                for i in range(1, ROWS):
                    if col[i] != 0:
                        k = i
                        while k > 0 and col[k - 1] == 0:
                            col[k - 1] = col[k]
                            col[k] = 0
                            k -= 1
                            valid = True
                        if k > 0 and col[k - 1] == col[k] and not merged[k - 1]:
                            col[k - 1] *= 2
                            col[k] = 0
                            merged[k - 1] = True
                            valid = True
        elif direction == "down":
            for j in range(COLS):
                col = new_board[:, j]
                merged = [False] * ROWS
                for i in range(ROWS - 2, -1, -1):
                    if col[i] != 0:
                        k = i
                        while k < ROWS - 1 and col[k + 1] == 0:
                            col[k + 1] = col[k]
                            col[k] = 0
                            k += 1
                            valid = True
                        if k < ROWS - 1 and col[k + 1] == col[k] and not merged[k + 1]:
                            col[k + 1] *= 2
                            col[k] = 0
                            merged[k + 1] = True
                            valid = True

        return new_board, valid

    @staticmethod
    def get_empty_cells(board):
        empty = []
        for i in range(ROWS):
            for j in range(COLS):
                if board[i, j] == 0:
                    empty.append((i, j))
        return empty

    @staticmethod
    def expectimax(board, depth, is_max=False):
        if depth == 0:
            return AI.evaluate(board), None

        if is_max:
            max_score = -float('inf')
            best_move = None
            moves = AI.get_possible_moves(board)

            for move in moves:
                direction, new_board = move
                score, _ = AI.expectimax(new_board, depth - 1, False)

                if score > max_score:
                    max_score = score
                    best_move = direction

            return max_score, best_move
        else:
            empty_cells = AI.get_empty_cells(board)
            if not empty_cells:
                return AI.evaluate(board), None

            total_score = 0
            for cell in empty_cells:
                i, j = cell
                # Try both 2 and 4 with their probabilities
                for value, prob in [(2, 0.9), (4, 0.1)]:
                    new_board = np.copy(board)
                    new_board[i, j] = value
                    score, _ = AI.expectimax(new_board, depth - 1, True)
                    total_score += score * prob

            avg_score = total_score / len(empty_cells)
            return avg_score, None

    @staticmethod
    def get_best_move(tiles, depth=3):
        board = AI.get_board_state(tiles)
        _, best_move = AI.expectimax(board, depth, True)
        return best_move


def main(window):
    clock = pygame.time.Clock()
    run = True
    game_state = "continue"
    tiles = generate_tiles()
    auto_play = False
    last_move_time = time.time()
    move_delay = 0.1  # Delay between AI moves in seconds

    while run:
        clock.tick(FPS)
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                    last_move_time = current_time  # Reset timer when toggling
                elif game_state != "lost" and not auto_play:
                    if event.key == pygame.K_LEFT:
                        game_state = move_tiles(window, tiles, clock, "left")
                    if event.key == pygame.K_RIGHT:
                        game_state = move_tiles(window, tiles, clock, "right")
                    if event.key == pygame.K_UP:
                        game_state = move_tiles(window, tiles, clock, "up")
                    if event.key == pygame.K_DOWN:
                        game_state = move_tiles(window, tiles, clock, "down")

        # AI move logic
        if auto_play and game_state != "lost" and current_time - last_move_time > move_delay:
            best_move = AI.get_best_move(tiles)
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