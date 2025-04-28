import pygame
import numpy as np
from PIL import Image, ImageFilter
import os
import random
from queue import PriorityQueue
from collections import deque
import io

# Add message box functionality
pygame.init()
pygame.font.init()

class MessageBox:
    def __init__(self, screen, message, width=400, height=200):
        self.screen = screen
        self.message = message
        self.width = width
        self.height = height
        self.x = (screen.get_width() - width) // 2
        self.y = (screen.get_height() - height) // 2
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.button_rect = pygame.Rect(self.x + width//2 - 50, self.y + height - 60, 100, 40)
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 28)
        self.visible = True
        self.button_hover = False

        self.colors = {
            'background': (245, 245, 245),
            'border': (0, 0, 0),
            'button': (52, 152, 219),
            'button_hover': (41, 128, 185),
            'button_text': (255, 255, 255),
            'text': (0, 0, 0)
        }

        # Split message into lines if it's too long
        words = message.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if self.font.size(test_line)[0] < width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        self.lines = lines

    def draw(self):
        if not self.visible:
            return

        # Draw semi-transparent background
        s = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, 0))

        shadow_rect = pygame.Rect(self.x + 3, self.y + 3, self.width, self.height)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Draw main box
        pygame.draw.rect(self.screen, self.colors['background'], self.rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['border'], self.rect, 2, border_radius=10)

        # Draw message lines
        for i, line in enumerate(self.lines):
            text_surface = self.font.render(line, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=(self.x + self.width//2, 
                                                    self.y + self.height//2 - 20 + i * 30))
            self.screen.blit(text_surface, text_rect)

        button_surface = pygame.Surface((self.button_rect.width, self.button_rect.height), pygame.SRCALPHA)

        shadow_rect = pygame.Rect(2, 2, self.button_rect.width, self.button_rect.height)
        pygame.draw.rect(button_surface, (0, 0, 0, 100), shadow_rect, border_radius=5)

        color = self.colors['button_hover'] if self.button_hover else self.colors['button']
        for y in range(self.button_rect.height):
            alpha = int(255 * (1 - y / self.button_rect.height * 0.3))
            gradient_color = (*color[:3], alpha)
            pygame.draw.line(button_surface, gradient_color, (0, y), (self.button_rect.width, y))

        pygame.draw.rect(button_surface, (*color[:3], 200),
                         pygame.Rect(0, 0, self.button_rect.width, self.button_rect.height),
                         border_radius=5)

        highlight_rect = pygame.Rect(0, 0, self.button_rect.width, self.button_rect.height // 3)
        highlight_color = (*color[:3], 100)
        pygame.draw.rect(button_surface, highlight_color, highlight_rect, border_radius=5)

        self.screen.blit(button_surface, self.button_rect)

        text = "OK"
        shadow_surface = self.button_font.render(text, True, (0, 0, 0, 150))
        shadow_rect = shadow_surface.get_rect(center=(self.button_rect.centerx + 1, self.button_rect.centery + 1))
        self.screen.blit(shadow_surface, shadow_rect)

        text_surface = self.button_font.render(text, True, self.colors['button_text'])
        text_rect = text_surface.get_rect(center=self.button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_click(self, pos):
        if not self.visible:
            return False
        
        self.button_hover = self.button_rect.collidepoint(pos)
        
        if self.button_rect.collidepoint(pos):
            self.visible = False
            return True
        return False

class PhotoPuzzle:
    def __init__(self, grid_size=3):
        pygame.init()
        self.grid_size = grid_size #Default grid size is 3x3
        self.piece_size = 150 
        self.puzzle_width = self.grid_size * self.piece_size
        self.button_width = 250
        self.padding = 20
        self.side_padding = 40
        self.window_width = self.puzzle_width + self.button_width + self.padding * 2 + self.side_padding
        self.window_height = self.puzzle_width + self.padding * 2 + 50
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Photo Puzzler")

        # Initialize completion message
        self.completion_message = None
        self.current_algorithm = None

        # Available images
        self.available_images = [
            "2.jpg",
            "1.png",
            "3.jpg"
        ]
        self.current_image_index = 0

        self.puzzle_top_padding = (self.window_height - self.puzzle_width) // 2


        self.colors = {
            'background': (245, 245, 245),
            'button': (45, 45, 45),
            'button_hover': (65, 65, 65),
            'button_text': (255, 255, 255),
            'border': (245, 245, 245),
            'timer': (45, 45, 45),
            'moves': (45, 45, 45),
            'algorithm': (45, 45, 45),
            'exit_button': (200, 50, 50),
            'exit_button_hover': (220, 70, 70),
            'title': (30, 30, 30),
            'stats_bg': (245, 245, 245),
            'shuffle_button': (52, 152, 219),
            'shuffle_button_hover': (41, 128, 185),
            'reset_button': (46, 204, 113),
            'reset_button_hover': (39, 174, 96),
            'algorithm_button': (155, 89, 182),
            'algorithm_button_hover': (142, 68, 173),
            'image_button': (241, 196, 15),
            'image_button_hover': (243, 156, 18)
        }

        # Initialize game state
        self.current_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        self.empty_pos = (grid_size - 1, grid_size - 1) #Bottom right corner
        self.moves = 0
        self.solving = False
        self.solution_path = []

        # Timer variables
        self.start_time = None
        self.elapsed_time = 0
        self.algorithm_time = 0

        self.timer_font = pygame.font.Font(None, 36) 
        self.title_font = pygame.font.Font(None, 42)  
        self.stats_font = pygame.font.Font(None, 32)  

        try:
            self.title_font = pygame.font.Font("C:\\Windows\\Fonts\\arial.ttf", 42)
        except:
            self.title_font = pygame.font.Font(None, 42)

        self.load_image()

        # Initialize buttons
        self.buttons = []
        button_height = 40  
        button_spacing = 8  
        button_x = self.puzzle_width + self.padding + self.side_padding  
        button_y = self.padding + 150 

        # Title and stats area
        self.stats_rect = pygame.Rect(button_x, self.padding, self.button_width - self.padding, 120)

        # Image selection button
        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'Change Image',
            'action': 'change_image',
            'hover': False
        })
        button_y += button_height + button_spacing

        # Shuffle button
        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'Shuffle',
            'action': 'shuffle',
            'hover': False
        })
        button_y += button_height + button_spacing

        # Reset button
        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'Reset',
            'action': 'reset',
            'hover': False
        })
        button_y += button_height + button_spacing

        # Algorithm buttons
        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'BFS',
            'action': 'bfs',
            'hover': False
        })
        button_y += button_height + button_spacing

        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'DFS',
            'action': 'dfs',
            'hover': False
        })
        button_y += button_height + button_spacing

        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'A*',
            'action': 'astar',
            'hover': False
        })
        button_y += button_height + button_spacing

        # Exit button
        self.buttons.append({
            'rect': pygame.Rect(button_x, button_y, self.button_width - self.padding, button_height),
            'text': 'Exit',
            'action': 'exit',
            'hover': False
        })

        # Font for buttons
        self.font = pygame.font.Font(None, 24) 

    def load_image(self):
        """Load the current image and prepare it for the puzzle"""
        try:
            self.original_image = Image.open(self.available_images[self.current_image_index])
            self.original_image = self.original_image.resize((self.puzzle_width, self.puzzle_width))
            self.pieces = self._split_image()
            self.blurred_piece = self._create_blurred_piece()
            # Reset and shuffle the puzzle
            self._reset_puzzle()
            self._shuffle_puzzle()
        except Exception as e:
            print(f"Error loading image: {e}")
            self.current_image_index = (self.current_image_index + 1) % len(self.available_images)
            self.load_image()

    def change_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.available_images)
        self.load_image()
        self._shuffle_puzzle()

    def _split_image(self):
        pieces = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                left = j * self.piece_size
                top = i * self.piece_size
                right = left + self.piece_size
                bottom = top + self.piece_size
                piece = self.original_image.crop((left, top, right, bottom))
                pieces.append(piece)
        return pieces

    def _create_initial_state(self):
        state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        for _ in range(1000):
            self._make_random_move()
        return state

    def _make_random_move(self):
        i, j = self.empty_pos
        possible_moves = []
        if i > 0:
            possible_moves.append((i - 1, j))
        if i < self.grid_size - 1:
            possible_moves.append((i + 1, j))
        if j > 0:
            possible_moves.append((i, j - 1))
        if j < self.grid_size - 1:
            possible_moves.append((i, j + 1))

        if possible_moves:
            new_i, new_j = random.choice(possible_moves)
            self._swap_pieces((i, j), (new_i, new_j))
            self.empty_pos = (new_i, new_j)

    def _swap_pieces(self, pos1, pos2):
        i1, j1 = pos1
        i2, j2 = pos2
        self.current_state[i1][j1], self.current_state[i2][j2] = self.current_state[i2][j2], self.current_state[i1][j1]

    def _create_blurred_piece(self):
        last_piece = self.pieces[-1]
        blurred = last_piece.filter(ImageFilter.GaussianBlur(radius=15))
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=15))
        return blurred

    def draw(self):
        self.screen.fill(self.colors['background'])

        puzzle_rect = pygame.Rect(self.padding, self.puzzle_top_padding, self.puzzle_width, self.puzzle_width)
        pygame.draw.rect(self.screen, (100, 100, 100), puzzle_rect, 3)  # Thicker outer border

        # Draw grid lines
        for i in range(1, self.grid_size):
            # Vertical lines
            pygame.draw.line(self.screen, (100, 100, 100),
                             (self.padding + i * self.piece_size, self.puzzle_top_padding),
                             (self.padding + i * self.piece_size, self.puzzle_top_padding + self.puzzle_width), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, (100, 100, 100),
                             (self.padding, self.puzzle_top_padding + i * self.piece_size),
                             (self.padding + self.puzzle_width, self.puzzle_top_padding + i * self.piece_size), 2)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                piece_index = self.current_state[i][j]
                if piece_index != self.grid_size * self.grid_size - 1:
                    piece = self.pieces[piece_index]
                else:
                    piece = self.blurred_piece
                piece_surface = pygame.image.fromstring(piece.tobytes(), piece.size, piece.mode)

                # Calculate piece position
                piece_x = j * self.piece_size + self.padding
                piece_y = i * self.piece_size + self.puzzle_top_padding

                # Draw piece
                self.screen.blit(piece_surface, (piece_x, piece_y))

                # Draw border around each piece
                piece_rect = pygame.Rect(piece_x, piece_y, self.piece_size, self.piece_size)
                pygame.draw.rect(self.screen, (150, 150, 150), piece_rect, 1)

        # Draw stats area with improved style
        pygame.draw.rect(self.screen, self.colors['stats_bg'], self.stats_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['border'], self.stats_rect, 2, border_radius=10)

        # Draw title with colorful gradient and shadow effect
        title_text = "Photo Puzzler"
        title_x = self.stats_rect.centerx
        title_y = self.stats_rect.top + 20
        font = self.title_font

        # Define a gradient color palette (rainbow-like)
        gradient_colors = [
            (255, 99, 71),  # Tomato
            (255, 215, 0),  # Gold
            (50, 205, 50),  # Lime Green
            (0, 191, 255),  # Deep Sky Blue
            (138, 43, 226),  # Blue Violet
            (255, 20, 147),  # Deep Pink
        ]

        # Calculate total width for centering
        total_width = 0
        char_surfaces = []
        for i, char in enumerate(title_text):
            color = gradient_colors[i % len(gradient_colors)]
            surf = font.render(char, True, color)
            char_surfaces.append((surf, color))
            total_width += surf.get_width()

        # Draw shadow
        shadow_offset = 3
        x = title_x - total_width // 2
        for i, (surf, color) in enumerate(char_surfaces):
            char = title_text[i]
            shadow = font.render(char, True, (0, 0, 0))
            self.screen.blit(shadow, (x + shadow_offset, title_y + shadow_offset))
            x += surf.get_width()

        # Draw gradient text
        x = title_x - total_width // 2
        for i, (surf, color) in enumerate(char_surfaces):
            self.screen.blit(surf, (x, title_y))
            x += surf.get_width()

        # Update and draw timer
        if self.start_time is not None:  # Only update if timer is running
            current_time = pygame.time.get_ticks()
            self.elapsed_time = current_time - self.start_time

        timer_text = f"Time: {self.elapsed_time // 1000}.{(self.elapsed_time % 1000) // 100}s"
        timer_surface = self.timer_font.render(timer_text, True, self.colors['timer'])
        timer_rect = timer_surface.get_rect(midtop=(self.stats_rect.centerx, self.stats_rect.top + 80))
        self.screen.blit(timer_surface, timer_rect)

        # Draw moves counter 
        moves_text = f"Moves: {self.moves}"
        moves_surface = self.stats_font.render(moves_text, True, self.colors['moves'])
        moves_rect = moves_surface.get_rect(midtop=(self.stats_rect.centerx, self.stats_rect.top + 120))
        self.screen.blit(moves_surface, moves_rect)

        # Draw buttons
        for button in self.buttons:
            if button['action'] == 'shuffle':
                base_color = self.colors['shuffle_button']
                hover_color = self.colors['shuffle_button_hover']
            elif button['action'] == 'reset':
                base_color = self.colors['reset_button']
                hover_color = self.colors['reset_button_hover']
            elif button['action'] in ['bfs', 'dfs', 'astar']:
                base_color = self.colors['algorithm_button']
                hover_color = self.colors['algorithm_button_hover']
            else:  
                base_color = self.colors['exit_button']
                hover_color = self.colors['exit_button_hover']

            button_surface = pygame.Surface((button['rect'].width, button['rect'].height), pygame.SRCALPHA)
            shadow_rect = pygame.Rect(2, 2, button['rect'].width, button['rect'].height)
            pygame.draw.rect(button_surface, (0, 0, 0, 100), shadow_rect, border_radius=5)

            color = hover_color if button['hover'] else base_color
            # Create gradient effect
            for y in range(button['rect'].height):
                alpha = int(255 * (1 - y / button['rect'].height * 0.3))  # Fade to darker
                gradient_color = (*color[:3], alpha)
                pygame.draw.line(button_surface, gradient_color, (0, y), (button['rect'].width, y))

            # Draw button border
            pygame.draw.rect(button_surface, (*color[:3], 200),
                             pygame.Rect(0, 0, button['rect'].width, button['rect'].height),
                             border_radius=5)

            # Draw button highlight
            highlight_rect = pygame.Rect(0, 0, button['rect'].width, button['rect'].height // 3)
            highlight_color = (*color[:3], 100)
            pygame.draw.rect(button_surface, highlight_color, highlight_rect, border_radius=5)

            # Blit button surface to screen
            self.screen.blit(button_surface, button['rect'])

            # Draw button text with shadow
            text = button['text']
            # Draw text shadow
            shadow_surface = self.font.render(text, True, (0, 0, 0, 150))
            shadow_rect = shadow_surface.get_rect(center=(button['rect'].centerx + 1, button['rect'].centery + 1))
            self.screen.blit(shadow_surface, shadow_rect)

            # Draw main text
            text_surface = self.font.render(text, True, self.colors['button_text'])
            text_rect = text_surface.get_rect(center=button['rect'].center)
            self.screen.blit(text_surface, text_rect)

        # Draw completion message if it exists
        if self.completion_message:
            self.completion_message.draw()

        pygame.display.flip()

    def handle_click(self, pos):
        if self.solving:
            return
        x, y = pos

        # Update button hover states
        for button in self.buttons:
            button['hover'] = button['rect'].collidepoint(x, y)

        # Check if a button was clicked
        for button in self.buttons:
            if button['rect'].collidepoint(x, y):
                if button['action'] == 'change_image':
                    self.change_image()
                elif button['action'] == 'shuffle':
                    self._shuffle_puzzle()
                elif button['action'] == 'reset':
                    self._reset_puzzle()
                elif button['action'] == 'bfs':
                    self.solve_bfs()
                    self.execute_solution()
                elif button['action'] == 'dfs':
                    self.solve_dfs()
                    self.execute_solution()
                elif button['action'] == 'astar':
                    self.solve_astar()
                    self.execute_solution()
                elif button['action'] == 'exit':
                    return 'exit'
                return

        # Handle puzzle piece movement (only in puzzle area)
        if (self.padding <= x < self.puzzle_width + self.padding and
                self.padding <= y < self.puzzle_width + self.padding):
            clicked_i = (y - self.padding) // self.piece_size
            clicked_j = (x - self.padding) // self.piece_size
            empty_i, empty_j = self.empty_pos

            # Check if the clicked piece is adjacent to the empty space
            if (abs(clicked_i - empty_i) == 1 and clicked_j == empty_j) or \
                    (abs(clicked_j - empty_j) == 1 and clicked_i == empty_i):
                if self.start_time is None:  # Start timer on first move
                    self.start_time = pygame.time.get_ticks()
                self._swap_pieces((clicked_i, clicked_j), (empty_i, empty_j))
                self.empty_pos = (clicked_i, clicked_j)
                self.moves += 1

    def _shuffle_puzzle(self):
        self.current_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        self.empty_pos = (self.grid_size - 1, self.grid_size - 1)
        for _ in range(1000):
            self._make_random_move()
        self.moves = 0
        self.start_time = None
        self.elapsed_time = 0

    def _reset_puzzle(self):
        self.current_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        self.empty_pos = (self.grid_size - 1, self.grid_size - 1)
        self.moves = 0
        self.start_time = None
        self.elapsed_time = 0

    def is_solved(self):
        solved_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        return np.array_equal(self.current_state, solved_state)

    def solve_bfs(self):
        """Solve the puzzle using BFS"""
        try:
            self.solving = True
            self.current_algorithm = 'bfs'  # Store current algorithm
            if self.start_time is None:  # Start timer if not already started
                self.start_time = pygame.time.get_ticks()
            initial_state = self.current_state.copy()
            empty_pos = self.empty_pos

            queue = deque([(initial_state, empty_pos, [])])
            visited = set()

            while queue:
                current_state, current_empty, path = queue.popleft()

                if np.array_equal(current_state,
                                  np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)):
                    self.solution_path = path
                    return True

                state_hash = tuple(current_state.flatten())
                if state_hash in visited:
                    continue

                visited.add(state_hash)

                i, j = current_empty
                for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_i, new_j = i + di, j + dj
                    if 0 <= new_i < self.grid_size and 0 <= new_j < self.grid_size:
                        new_state = current_state.copy()
                        new_state[i][j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[i][j]
                        new_path = path + [(new_i, new_j)]
                        queue.append((new_state, (new_i, new_j), new_path))

            return False
        except Exception as e:
            print(f"Error in BFS: {e}")
            self.solving = False
            return False

    def solve_dfs(self):
        """Solve the puzzle using DFS with depth limit"""
        try:
            self.solving = True
            self.current_algorithm = 'dfs'  # Store current algorithm
            if self.start_time is None:  # Start timer if not already started
                self.start_time = pygame.time.get_ticks()
            initial_state = self.current_state.copy()
            empty_pos = self.empty_pos

            # Set a reasonable depth limit to prevent stack overflow
            max_depth = 70
            visited = set()

            def dfs_helper(current_state, current_empty, path, depth):
                if depth > max_depth:
                    return None

                if np.array_equal(current_state,
                                  np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)):
                    return path

                state_hash = tuple(current_state.flatten())
                if state_hash in visited:
                    return None

                visited.add(state_hash)

                i, j = current_empty
                for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_i, new_j = i + di, j + dj
                    if 0 <= new_i < self.grid_size and 0 <= new_j < self.grid_size:
                        new_state = current_state.copy()
                        new_state[i][j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[i][j]
                        new_path = path + [(new_i, new_j)]
                        result = dfs_helper(new_state, (new_i, new_j), new_path, depth + 1)
                        if result is not None:
                            return result

                return None

            solution = dfs_helper(initial_state, empty_pos, [], 0)
            if solution is not None:
                self.solution_path = solution
                return True
            else:
                print("DFS could not find a solution within the depth limit")
                return False

        except Exception as e:
            print(f"Error in DFS: {e}")
            self.solving = False
            return False

    def solve_astar(self):
        """Solve the puzzle using A* algorithm"""
        try:
            self.solving = True
            self.current_algorithm = 'astar'  # Store current algorithm
            if self.start_time is None:  # Start timer if not already started
                self.start_time = pygame.time.get_ticks()
            initial_state = self.current_state.copy()
            empty_pos = self.empty_pos

            def heuristic(state):
                # Manhattan distance heuristic
                total = 0
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        value = state[i][j]
                        if value != self.grid_size * self.grid_size - 1:  # Skip empty tile
                            goal_i = value // self.grid_size
                            goal_j = value % self.grid_size
                            total += abs(i - goal_i) + abs(j - goal_j)
                return total

            queue = PriorityQueue()
            queue.put((0, 0, initial_state, empty_pos, []))
            visited = set()
            counter = 1

            while not queue.empty():
                _, _, current_state, current_empty, path = queue.get()

                if np.array_equal(current_state,
                                  np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)):
                    self.solution_path = path
                    return True

                state_hash = tuple(current_state.flatten())
                if state_hash in visited:
                    continue

                visited.add(state_hash)

                i, j = current_empty
                for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_i, new_j = i + di, j + dj
                    if 0 <= new_i < self.grid_size and 0 <= new_j < self.grid_size:
                        new_state = current_state.copy()
                        new_state[i][j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[i][j]
                        new_path = path + [(new_i, new_j)]
                        priority = len(new_path) + heuristic(new_state)
                        queue.put((priority, counter, new_state, (new_i, new_j), new_path))
                        counter += 1

            return False
        except Exception as e:
            print(f"Error in A*: {e}")
            self.solving = False
            return False

    def execute_solution(self):
        """Execute the found solution step by step"""
        try:
            if not self.solution_path:
                self.solving = False
                return

            for move in self.solution_path:
                if not self.solving:  # Allow interruption
                    break
                self._swap_pieces(self.empty_pos, move)
                self.empty_pos = move
                self.moves += 1  # Increment moves counter
                self.draw()  # This will update the timer
                pygame.time.delay(500)  # Delay between moves for visualization
                pygame.event.pump()  # Keep the window responsive

            # Stop the timer but keep the final time
            if self.solving:  # Only if we completed the solution (not interrupted)
                final_time = self.elapsed_time
                self.start_time = None
                self.elapsed_time = final_time  # Keep the final time
                # Create completion message
                algorithm_name = "BFS" if self.current_algorithm == 'bfs' else \
                               "DFS" if self.current_algorithm == 'dfs' else "A*"
                message = f"{algorithm_name} solved the puzzle in {self.moves} moves and {self.elapsed_time/1000:.1f} seconds!"
                self.completion_message = MessageBox(self.screen, message)
                print(f"Created completion message: {message}")  # Debug print

            self.solving = False
            self.solution_path = []
        except Exception as e:
            print(f"Error executing solution: {e}")
            self.solving = False
            self.solution_path = []
            final_time = self.elapsed_time
            self.start_time = None
            self.elapsed_time = final_time  # Keep the final time


def main():
    puzzle = PhotoPuzzle()
    running = True
    was_solved = False
    message_box = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if message_box and message_box.handle_click(event.pos):
                    message_box = None
                elif puzzle.completion_message and puzzle.completion_message.handle_click(event.pos):
                    puzzle.completion_message = None
                else:
                    result = puzzle.handle_click(event.pos)
                    if result == 'exit':
                        running = False

        puzzle.draw()

        current_state = puzzle.is_solved()
        if current_state and puzzle.moves > 0 and not was_solved:
            message = f"Puzzle solved in {puzzle.moves} moves!"
            message_box = MessageBox(puzzle.screen, message)
            was_solved = True
        elif not current_state:
            was_solved = False

        if message_box:
            message_box.draw()

        pygame.time.delay(50)

    pygame.quit()


if __name__ == "__main__":
    main()
