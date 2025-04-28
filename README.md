# Photo Puzzle Game

A modern implementation of the classic sliding puzzle game with photo support and multiple solving algorithms.

![Game Screenshot](screenshot.png)

## Features

- 🖼️ **Photo Support**: Load and play with your favorite images
- 🎮 **Interactive Gameplay**: Click to move pieces
- ⚡ **Multiple Solving Algorithms**: Choose between BFS, DFS, and A* algorithms
- 🎯 **Progress Tracking**: Move counter and timer
- 🎨 **Modern UI**: Clean interface with gradient effects and smooth animations
- 🔄 **Multiple Controls**: Shuffle, reset, and change image options

## Requirements

- Python 3.6+
- Pygame
- NumPy
- Pillow (PIL)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/HosamFathy/PhotoPuzzler/tree/main?tab=readme-ov-file
cd PhotoPuzzler
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the game:
```bash
python PhotoPuzzler.py
```

2. Game Controls:
- Click on pieces adjacent to the empty space to move them
- Use the buttons on the right side to:
  - Change the current image
  - Shuffle the puzzle
  - Reset the puzzle
  - Solve using different algorithms (BFS, DFS, A*)

## Solving Algorithms

The game implements three different algorithms to solve the puzzle:

1. **Breadth-First Search (BFS)**
   - Guaranteed to find the shortest solution
   - Explores all possible states level by level
   - Best for small puzzles

2. **Depth-First Search (DFS)**
   - More memory efficient
   - Uses depth limit to prevent infinite recursion
   - May find solutions faster but not necessarily optimal

3. **A* Search Algorithm**
   - Most efficient for most cases
   - Uses Manhattan distance heuristic
   - Combines the best features of BFS and DFS


## Customization

### Adding New Images
1. Place your images in the 'PuzzleGame' directory
2. Supported formats: PNG, JPG
3. The game will automatically detect and include them

### Changing Grid Size
Modify the `grid_size` parameter in the `PhotoPuzzle` class initialization:
```python
puzzle = PhotoPuzzle(grid_size=4)  # For a 4x4 puzzle
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Pygame community for the excellent game development framework
- Pillow (PIL) for image processing capabilities
- NumPy for efficient array operations

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)

Project Link: https://github.com/HosamFathy/PhotoPuzzler/tree/main?tab=readme-ov-file
