import pygame
import numpy as np
from PIL import Image
import os
import random
from queue import PriorityQueue
from collections import deque

class PhotoPuzzle:
    def __init__(self, image_path, grid_size=3):
        pygame.init()
        self.grid_size = grid_size
        self.piece_size = 150
        self.puzzle_width = self.grid_size * self.piece_size
        self.button_width = 250  # Reduced button panel width
        self.padding = 20
        self.window_width = self.puzzle_width + self.button_width + self.padding * 3
        self.window_height = self.puzzle_width + self.padding * 2 + 100
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Photo Puzzler")
        
        # Colors - More minimal color scheme
        self.colors = {
            'background': (250, 250, 250),
            'button': (45, 45, 45),
            'button_hover': (65, 65, 65),
            'button_text': (255, 255, 255),
            'border': (200, 200, 200),
            'timer': (45, 45, 45),
            'moves': (45, 45, 45),
            'algorithm': (45, 45, 45),
            'exit_button': (200, 50, 50),
            'exit_button_hover': (220, 70, 70)
        }
        
        # Initialize game state
        self.current_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        self.empty_pos = (grid_size-1, grid_size-1)
        self.moves = 0
        self.solving = False
        self.solution_path = []
        
        # Timer variables
        self.start_time = None
        self.elapsed_time = 0
        self.algorithm_time = 0
        self.timer_font = pygame.font.Font(None, 32)  # Slightly smaller font
        self.title_font = pygame.font.Font(None, 36)  # Smaller title font
        
        # Load and prepare the image
        self.original_image = Image.open("123.png")
        self.original_image = self.original_image.resize((self.puzzle_width, self.puzzle_width))
        self.pieces = self._split_image()
        
        # Shuffle the puzzle
        for _ in range(1000):
            self._make_random_move()
        
        # Initialize buttons
        self.buttons = []
        button_height = 40  # Slightly smaller buttons
        button_spacing = 8  # Tighter spacing
        button_x = self.puzzle_width + self.padding * 2
        button_y = self.padding + 150  # Start buttons higher
        
        # Title and stats area
        self.stats_rect = pygame.Rect(button_x, self.padding, self.button_width - self.padding, 120)
        
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
        self.font = pygame.font.Font(None, 24)  # Smaller button font
        
    def _split_image(self):
        """Split the image into grid_size x grid_size pieces"""
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
        """Create the initial state of the puzzle"""
        state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        # Shuffle the puzzle
        for _ in range(1000):
            self._make_random_move()
        return state
    
    def _make_random_move(self):
        """Make a random valid move"""
        i, j = self.empty_pos
        possible_moves = []
        if i > 0:
            possible_moves.append((i-1, j))
        if i < self.grid_size-1:
            possible_moves.append((i+1, j))
        if j > 0:
            possible_moves.append((i, j-1))
        if j < self.grid_size-1:
            possible_moves.append((i, j+1))
        
        if possible_moves:
            new_i, new_j = random.choice(possible_moves)
            self._swap_pieces((i, j), (new_i, new_j))
            self.empty_pos = (new_i, new_j)
    
    def _swap_pieces(self, pos1, pos2):
        """Swap two pieces in the current state"""
        i1, j1 = pos1
        i2, j2 = pos2
        self.current_state[i1][j1], self.current_state[i2][j2] = self.current_state[i2][j2], self.current_state[i1][j1]
    
    def draw(self):
        """Draw the current state of the puzzle"""
        self.screen.fill(self.colors['background'])
        
        # Draw puzzle with minimal border
        puzzle_rect = pygame.Rect(self.padding, self.padding, self.puzzle_width, self.puzzle_width)
        pygame.draw.rect(self.screen, self.colors['border'], puzzle_rect, 1)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                piece_index = self.current_state[i][j]
                if piece_index != self.grid_size * self.grid_size - 1:
                    piece = self.pieces[piece_index]
                    piece_surface = pygame.image.fromstring(piece.tobytes(), piece.size, piece.mode)
                    self.screen.blit(piece_surface, 
                                   (j * self.piece_size + self.padding, 
                                    i * self.piece_size + self.padding))
        
        # Draw stats area with minimal style
        pygame.draw.rect(self.screen, self.colors['background'], self.stats_rect)
        pygame.draw.rect(self.screen, self.colors['border'], self.stats_rect, 1)
        
        # Draw title
        title_surface = self.title_font.render("Photo Puzzle", True, self.colors['timer'])
        title_rect = title_surface.get_rect(midtop=(self.stats_rect.centerx, self.stats_rect.top + 10))
        self.screen.blit(title_surface, title_rect)
        
        # Update and draw timer
        if self.start_time is not None:  # Only update if timer is running
            current_time = pygame.time.get_ticks()
            self.elapsed_time = current_time - self.start_time
        
        timer_text = f"Time: {self.elapsed_time // 1000}.{(self.elapsed_time % 1000) // 100}s"
        timer_surface = self.timer_font.render(timer_text, True, self.colors['timer'])
        timer_rect = timer_surface.get_rect(midtop=(self.stats_rect.centerx, self.stats_rect.top + 50))
        self.screen.blit(timer_surface, timer_rect)
        
        # Draw moves counter
        moves_text = f"Moves: {self.moves}"
        moves_surface = self.timer_font.render(moves_text, True, self.colors['moves'])
        moves_rect = moves_surface.get_rect(midtop=(self.stats_rect.centerx, self.stats_rect.top + 85))
        self.screen.blit(moves_surface, moves_rect)
        
        # Draw buttons with minimal style
        for button in self.buttons:
            color = (self.colors['exit_button_hover'] if button['hover'] else self.colors['exit_button']) if button['action'] == 'exit' else (self.colors['button_hover'] if button['hover'] else self.colors['button'])
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=5)
            text = self.font.render(button['text'], True, self.colors['button_text'])
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        """Handle mouse click to move pieces or press buttons"""
        if self.solving:
            return
            
        x, y = pos
        
        # Update button hover states
        for button in self.buttons:
            button['hover'] = button['rect'].collidepoint(x, y)
        
        # Check if a button was clicked
        for button in self.buttons:
            if button['rect'].collidepoint(x, y):
                if button['action'] == 'shuffle':
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
        """Shuffle the puzzle"""
        self.current_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        self.empty_pos = (self.grid_size-1, self.grid_size-1)
        for _ in range(1000):
            self._make_random_move()
        self.moves = 0
        self.start_time = None
        self.elapsed_time = 0
    
    def _reset_puzzle(self):
        """Reset the puzzle to solved state"""
        self.current_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        self.empty_pos = (self.grid_size-1, self.grid_size-1)
        self.moves = 0
        self.start_time = None
        self.elapsed_time = 0
    
    def is_solved(self):
        """Check if the puzzle is solved"""
        solved_state = np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)
        return np.array_equal(self.current_state, solved_state)
    
    def solve_bfs(self):
        """Solve the puzzle using BFS"""
        try:
            self.solving = True
            if self.start_time is None:  # Start timer if not already started
                self.start_time = pygame.time.get_ticks()
            initial_state = self.current_state.copy()
            empty_pos = self.empty_pos
            
            queue = deque([(initial_state, empty_pos, [])])
            visited = set()
            
            while queue:
                current_state, current_empty, path = queue.popleft()
                
                if np.array_equal(current_state, np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)):
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
            if self.start_time is None:  # Start timer if not already started
                self.start_time = pygame.time.get_ticks()
            initial_state = self.current_state.copy()
            empty_pos = self.empty_pos
            
            # Set a reasonable depth limit to prevent stack overflow
            max_depth = 50
            visited = set()
            
            def dfs_helper(current_state, current_empty, path, depth):
                if depth > max_depth:
                    return None
                    
                if np.array_equal(current_state, np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)):
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
                
                if np.array_equal(current_state, np.arange(self.grid_size * self.grid_size).reshape(self.grid_size, self.grid_size)):
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
    puzzle = PhotoPuzzle("123.png")
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = puzzle.handle_click(event.pos)
                if result == 'exit':
                    running = False
        
        puzzle.draw()
        if puzzle.is_solved():
            print(f"Puzzle solved in {puzzle.moves} moves!")
            # Don't exit, just show the solved state
    
    pygame.quit()

if __name__ == "__main__":
    main()
