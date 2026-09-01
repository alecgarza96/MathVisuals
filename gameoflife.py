import numpy as np
import pygame

BACKGROUND = (10, 10, 10)        
GRAVE_COLORS = [
    (57, 255, 20),                
    (0, 200, 0),                  
    (80, 255, 80),                
    (148, 0, 211),              
    (180, 180, 180),
]

class Grid:
    def __init__(self, rows: int = 50, cols: int = 50):
        self.matrix = np.random.randint(2, size=(rows, cols))
        self.buffer = np.zeros_like(self.matrix)
        self.color_indices = np.random.randint(0, len(GRAVE_COLORS), size=(rows, cols))

    def detect_neighbors(self) -> np.ndarray:
        m = self.matrix
        return (
            np.roll(m,  1, axis=0) +  # Shift Right
            np.roll(m, -1, axis=0) +  # Shift Left
            np.roll(m,  1, axis=1) +  # Shift Down
            np.roll(m, -1, axis=1) +  # Shift Up
            np.roll(np.roll(m,  1, axis=0),  1, axis=1) +  # Down-Right
            np.roll(np.roll(m,  1, axis=0), -1, axis=1) +  # Up-Right
            np.roll(np.roll(m, -1, axis=0),  1, axis=1) +  # Down-Left
            np.roll(np.roll(m, -1, axis=0), -1, axis=1)    # Up-Left
        )

    def swap_buffers(self) -> None:
        self.matrix, self.buffer = self.buffer, self.matrix

    def set_buffer(self, buffer) -> None:
        self.buffer = buffer

class Policy:
    def next_state(self, matrix: np.ndarray, neighbors: np.ndarray) -> np.ndarray:
        survive = (matrix == 1) & ((neighbors == 2) | (neighbors == 3))
        rebirth = (matrix == 0) & (neighbors == 3)
        return (survive | rebirth).astype(int)
 
class GameOfLife:
    def __init__(self, grid: Grid, policy: Policy):
        self.grid = grid
        self.policy = policy
 

    def tick(self) -> None:
        neighbors = self.grid.detect_neighbors()
        self.grid.set_buffer(self.policy.next_state(self.grid.matrix, neighbors))
        self.grid.swap_buffers()

class Client:
    def __init__(self, game: GameOfLife, cell_size: int = 12, fps: int = 10):
        pygame.init()
        self.game = game
        self.cell_size = cell_size
        self.fps = fps
        rows, cols = game.grid.matrix.shape
        rows, cols = game.grid.matrix.shape
        self.screen = pygame.display.set_mode((cols * cell_size, rows * cell_size))
        self.info_box = pygame.Rect(8, 8, 230, 140)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 14)
        self.rules_text = [
            "Conway's Game of Life",
            "",
            "1. < 2 neighbors: dies",
            "2. 2-3 neighbors: survives",
            "3. > 3 neighbors: dies",
            "4. Dead + 3 neighbors: born",
        ]

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        rows, cols = self.game.grid.matrix.shape
        for row in range(rows):
            for col in range(cols):
                if self.game.grid.matrix[row, col] == 1:
                    rect = pygame.Rect(
                        col * self.cell_size,
                        row * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    if not rect.colliderect(self.info_box):
                        color = GRAVE_COLORS[self.game.grid.color_indices[row, col]]
                        pygame.draw.rect(self.screen, color, rect)
        # Dark semi-opaque box
        pygame.draw.rect(self.screen, (20, 20, 20), self.info_box)
        pygame.draw.rect(self.screen, (57, 255, 20), self.info_box, 1)  # green border, 1px
        # Text inside box
        x, y = self.info_box.x + 6, self.info_box.y + 6
        for line in self.rules_text:
            surface = self.font.render(line, True, (57, 255, 20))
            self.screen.blit(surface, (x, y))
            y += 18
 
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True
 
    def run(self) -> None:
        running = True
        while running:
            running = self.handle_events()
            self.game.tick()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.quit()

if __name__ == "__main__":
    grid = Grid(rows=50, cols=50)
    print(grid.detect_neighbors())
    policy = Policy()
    game = GameOfLife(grid, policy)
    client = Client(game, cell_size=12, fps=10)
    client.run()
