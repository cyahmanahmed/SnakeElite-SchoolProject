import pygame
import sys
import random
import math

# Stores global configuration settings such as screen size, themes, and skins
class Config:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    GRID_SIZE = 20
    BASE_FPS = 10
    HUD_HEIGHT = 40
    
    THEMES = {
        "MAINFRAME": {"bg": (5, 8, 10), "grid": (15, 25, 30), "wall": (255, 255, 255), "ui": (0, 255, 180)},
        "VOID": {"bg": (10, 10, 10), "grid": (25, 25, 25), "wall": (200, 200, 200), "ui": (200, 200, 200)},
        "SYNTHWAVE": {"bg": (20, 0, 30), "grid": (45, 0, 65), "wall": (255, 0, 255), "ui": (255, 0, 255)}
    }
    SKINS = {
        "CLASSIC": {"head": (255, 255, 255), "body": (150, 150, 150)},
        "NEON": {"head": (0, 255, 255), "body": (0, 100, 100)},
        "TOXIC": {"head": (170, 255, 0), "body": (60, 90, 0)}
    }

# Controls the entire snake game including logic, input handling, and rendering
class SnakeGame:
    # Initializes the game, pygame, fonts, assets, and default state
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Elite")
        self.clock = pygame.time.Clock()
        
        self.font_title = pygame.font.SysFont("impact", 80)
        self.font_menu = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_hud = pygame.font.SysFont("consolas", 18, bold=True)
        
        self.image_path = r"pictures\snake_game_pic.jpg"
        try:
            raw_img = pygame.image.load(self.image_path).convert()
            self.menu_bg = pygame.transform.scale(raw_img, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        except:
            self.menu_bg = None

        self.state = "START" 
        self.game_mode = "CLASSIC" 
        self.maze_level = 1
        self.unlocked_levels = 1 
        self.theme_name = "MAINFRAME"
        self.skin_name = "CLASSIC"
        self.menu_index = 0
        self.menu_rects = []
        self.grid_rects = [] 
        self.icon_rect = pygame.Rect(Config.SCREEN_WIDTH - 45, 8, 30, 24)
        
        self.v_walls = []
        self.h_walls = []
        self.current_grid = Config.GRID_SIZE
        self.reset_game()

    # Creates a perfect maze structure based on the current maze level
    def generate_perfect_maze(self):
        if self.maze_level <= 3: self.current_grid = 50 
        elif self.maze_level <= 7: self.current_grid = 40
        else: self.current_grid = 25

        cols = Config.SCREEN_WIDTH // self.current_grid
        rows = (Config.SCREEN_HEIGHT - Config.HUD_HEIGHT) // self.current_grid
        self.v_walls = [[True for _ in range(rows)] for _ in range(cols + 1)]
        self.h_walls = [[True for _ in range(rows + 1)] for _ in range(cols)]
        visited = [[False for _ in range(rows)] for _ in range(cols)]
        stack = [(0, 0)]; visited[0][0] = True
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy, wt, wx, wy in [(0,-1,'h',x,y), (0,1,'h',x,y+1), (-1,0,'v',x,y), (1,0,'v',x+1,y)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows and not visited[nx][ny]:
                    neighbors.append((nx, ny, wt, wx, wy))
            if neighbors:
                nx, ny, wt, wx, wy = random.choice(neighbors)
                if wt == 'v': self.v_walls[wx][wy] = False
                else: self.h_walls[wx][wy] = False
                visited[nx][ny] = True; stack.append((nx, ny))
            else: stack.pop()

    # Resets the snake, food, score, and level for a new game session
    def reset_game(self):
        if self.game_mode == "MAZE":
            self.generate_perfect_maze()
            self.snake = [[self.current_grid // 2, Config.HUD_HEIGHT + (self.current_grid // 2)]]
            cols = Config.SCREEN_WIDTH // self.current_grid
            rows = (Config.SCREEN_HEIGHT - Config.HUD_HEIGHT) // self.current_grid
            self.food_pos = [(cols - 1) * self.current_grid + self.current_grid // 2, 
                            (rows - 1) * self.current_grid + Config.HUD_HEIGHT + self.current_grid // 2]
        else:
            self.current_grid = Config.GRID_SIZE
            self.snake = [[410, 310], [390, 310], [370, 310]]
            self.spawn_food()
            
        self.direction = "STOP"
        self.score = 0
        self.level = 1

    # Spawns food at a random grid position not occupied by the snake
    def spawn_food(self):
        cols = Config.SCREEN_WIDTH // Config.GRID_SIZE
        rows = (Config.SCREEN_HEIGHT - Config.HUD_HEIGHT) // Config.GRID_SIZE
        while True:
            x = random.randrange(0, cols) * Config.GRID_SIZE + Config.GRID_SIZE // 2
            y = random.randrange(0, rows) * Config.GRID_SIZE + Config.HUD_HEIGHT + Config.GRID_SIZE // 2
            self.food_pos = [x, y]
            if self.food_pos not in self.snake: break

    # Returns menu options based on the current game state
    def get_current_options(self):
        if self.state == "START": return ["PLAY", "TERRAIN", "EXIT GAME"]
        if self.state == "PAUSE": return ["CONTINUE", "TERRAIN", "MAIN MENU"]
        if self.state == "MODE_SELECT": return ["CLASSIC ENDLESS", "MAZE MISSIONS", "MAIN MENU"]
        if self.state == "TERRAIN": return ["THEME", "SNAKE SKIN", "BACK"]
        return []

    # Executes logic for the selected menu option
    def select_menu_option(self, choice):
        if choice == "EXIT GAME": pygame.quit(); sys.exit()
        elif choice == "PLAY": self.state = "MODE_SELECT"; self.menu_index = 0
        elif choice == "CONTINUE": self.state = "PLAYING"
        elif choice == "TERRAIN": self.previous_state = self.state; self.state = "TERRAIN"; self.menu_index = 0
        elif choice == "CLASSIC ENDLESS":
            self.game_mode = "CLASSIC"; self.reset_game(); self.state = "PLAYING"
        elif choice == "MAZE MISSIONS":
            self.state = "MAZE_SELECT"; self.menu_index = 0
        elif choice == "MAIN MENU": self.state = "START"; self.menu_index = 0
        elif choice == "BACK": self.state = self.previous_state; self.menu_index = 0

    # Cycles through available themes or snake skins
    def cycle_option(self, opt, d):
        if "THEME" in opt:
            t = list(Config.THEMES.keys())
            self.theme_name = t[(t.index(self.theme_name) + d) % len(t)]
        if "SKIN" in opt:
            s = list(Config.SKINS.keys())
            self.skin_name = s[(s.index(self.skin_name) + d) % len(s)]

    # Handles all keyboard and mouse input events
    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        opts = self.get_current_options()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "MAZE_SELECT":
                    for i, rect in enumerate(self.grid_rects):
                        if rect.collidepoint(mouse_pos) and (i + 1) <= self.unlocked_levels:
                            self.maze_level = i + 1; self.game_mode = "MAZE"; self.reset_game(); self.state = "PLAYING"
                    if hasattr(self, 'maze_back_rect') and self.maze_back_rect.collidepoint(mouse_pos): self.state = "MODE_SELECT"
                
                elif self.state in ["START", "PAUSE", "MODE_SELECT", "TERRAIN"]:
                    for i, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            if self.state == "TERRAIN" and i < 2: self.cycle_option(opts[i], 1)
                            else: self.select_menu_option(opts[i])
                
                if self.state == "PLAYING" and self.icon_rect.collidepoint(mouse_pos): self.state = "PAUSE"

            if event.type == pygame.KEYDOWN:
                if self.state == "PLAYING":
                    if event.key == pygame.K_UP and (self.game_mode == "MAZE" or self.direction != "DOWN"): self.direction = "UP"
                    elif event.key == pygame.K_DOWN and (self.game_mode == "MAZE" or self.direction != "UP"): self.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and (self.game_mode == "MAZE" or self.direction != "RIGHT"): self.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and (self.game_mode == "MAZE" or self.direction != "LEFT"): self.direction = "RIGHT"
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_m: self.state = "PAUSE"
                
                elif self.state in ["GAMEOVER", "WIN"] and event.key == pygame.K_SPACE:
                    if self.state == "WIN":
                        if self.maze_level == self.unlocked_levels: self.unlocked_levels = min(10, self.unlocked_levels + 1)
                        self.state = "MAZE_SELECT"
                    else: self.state = "START"
                
                elif self.state in ["START", "PAUSE", "MODE_SELECT", "TERRAIN"]:
                    if event.key == pygame.K_UP: self.menu_index = (self.menu_index - 1) % len(opts)
                    elif event.key == pygame.K_DOWN: self.menu_index = (self.menu_index + 1) % len(opts)
                    elif event.key == pygame.K_LEFT: self.cycle_option(opts[self.menu_index], -1)
                    elif event.key == pygame.K_RIGHT: self.cycle_option(opts[self.menu_index], 1)
                    elif event.key == pygame.K_RETURN: self.select_menu_option(opts[self.menu_index])

    # Updates snake movement, collision logic, and game progression
    def update(self):
        if self.state != "PLAYING" or self.direction == "STOP": return
        head = list(self.snake[0])
        cx, cy = head[0] // self.current_grid, (head[1] - Config.HUD_HEIGHT) // self.current_grid
        
        move_allowed = True
        if self.game_mode == "MAZE":
            if self.direction == "UP" and (cy == 0 or self.h_walls[cx][cy]): move_allowed = False
            elif self.direction == "DOWN" and (cy >= (Config.SCREEN_HEIGHT-Config.HUD_HEIGHT)//self.current_grid - 1 or self.h_walls[cx][cy+1]): move_allowed = False
            elif self.direction == "LEFT" and (cx == 0 or self.v_walls[cx][cy]): move_allowed = False
            elif self.direction == "RIGHT" and (cx >= Config.SCREEN_WIDTH//self.current_grid - 1 or self.v_walls[cx+1][cy]): move_allowed = False

        if move_allowed:
            if self.direction == "UP": head[1] -= self.current_grid
            elif self.direction == "DOWN": head[1] += self.current_grid
            elif self.direction == "LEFT": head[0] -= self.current_grid
            elif self.direction == "RIGHT": head[0] += self.current_grid
            
            if self.game_mode == "CLASSIC":
                head[0] %= Config.SCREEN_WIDTH
                if head[1] < Config.HUD_HEIGHT: head[1] = Config.SCREEN_HEIGHT - Config.GRID_SIZE // 2
                elif head[1] > Config.SCREEN_HEIGHT: head[1] = Config.HUD_HEIGHT + Config.GRID_SIZE // 2
                
                if head in self.snake: self.state = "GAMEOVER"; return
                self.snake.insert(0, head)
                if head[0] == self.food_pos[0] and head[1] == self.food_pos[1]:
                    self.score += 10; self.level = (self.score // 50) + 1; self.spawn_food()
                else: self.snake.pop()
            else:
                self.snake = [head]
                if head == [self.food_pos[0], self.food_pos[1]]: self.state = "WIN"

    # Draws all visual elements based on the current game state
    def draw(self):
        theme = Config.THEMES[self.theme_name]; skin = Config.SKINS[self.skin_name]
        self.screen.fill(theme["bg"])
        
        if self.state in ["START", "PAUSE", "MODE_SELECT", "MAZE_SELECT", "TERRAIN"]:
            if self.menu_bg: self.screen.blit(self.menu_bg, (0, 0))
            if self.state == "MAZE_SELECT": self.draw_maze_grid(theme["ui"])
            else: self.draw_dynamic_menu(theme["ui"])
        else:
            if self.game_mode == "CLASSIC":
                for x in range(0, Config.SCREEN_WIDTH, Config.GRID_SIZE):
                    pygame.draw.line(self.screen, theme["grid"], (x, Config.HUD_HEIGHT), (x, Config.SCREEN_HEIGHT))
                for y in range(Config.HUD_HEIGHT, Config.SCREEN_HEIGHT, Config.GRID_SIZE):
                    pygame.draw.line(self.screen, theme["grid"], (0, y), (Config.SCREEN_WIDTH, y))
            else:
                cols, rows = Config.SCREEN_WIDTH // self.current_grid, (Config.SCREEN_HEIGHT - Config.HUD_HEIGHT) // self.current_grid
                for x in range(cols + 1):
                    for y in range(rows):
                        if self.v_walls[x][y]:
                            pygame.draw.line(self.screen, theme["wall"], (x*self.current_grid, y*self.current_grid+Config.HUD_HEIGHT),
                                             (x*self.current_grid, (y+1)*self.current_grid+Config.HUD_HEIGHT), 2)
                for x in range(cols):
                    for y in range(rows + 1):
                        if self.h_walls[x][y]:
                            pygame.draw.line(self.screen, theme["wall"], (x*self.current_grid, y*self.current_grid+Config.HUD_HEIGHT),
                                             ((x+1)*self.current_grid, y*self.current_grid+Config.HUD_HEIGHT), 2)

            pygame.draw.rect(self.screen, (15, 15, 25), [0, 0, Config.SCREEN_WIDTH, Config.HUD_HEIGHT])
            pygame.draw.line(self.screen, theme["ui"], (0, Config.HUD_HEIGHT), (Config.SCREEN_WIDTH, Config.HUD_HEIGHT), 2)
            self.draw_hud(theme["ui"])
            
            for i, p in enumerate(self.snake):
                sz = self.current_grid - 2
                pygame.draw.rect(self.screen, skin["head" if i == 0 else "body"],
                                 [p[0]-sz//2, p[1]-sz//2, sz, sz], border_radius=3)
            
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 3
            pygame.draw.circle(self.screen,
                               (255, 50, 50) if self.game_mode == "MAZE" else (0, 255, 180),
                               (int(self.food_pos[0]), int(self.food_pos[1])),
                               8 + int(pulse))
            
            if self.state == "GAMEOVER": self.draw_overlay("GAME OVER", "SPACE FOR START")
            if self.state == "WIN": self.draw_overlay("MISSION CLEAR", "SPACE FOR MISSIONS")
            
        pygame.display.flip()

    # Draws the maze level selection grid
    def draw_maze_grid(self, ui_color):
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0,0))
        self.grid_rects = []
        for i in range(10):
            rect = pygame.Rect(115 + (i%5)*115, 200 + (i//5)*115, 90, 90)
            self.grid_rects.append(rect)
            locked = (i + 1) > self.unlocked_levels
            color = ui_color if not locked else (60, 60, 60)
            pygame.draw.rect(self.screen, color, rect, 2, border_radius=8)
            txt = self.font_menu.render(str(i+1) if not locked else "LOCKED", True, color)
            self.screen.blit(txt, txt.get_rect(center=rect.center))
        self.maze_back_rect = pygame.Rect(300, 480, 200, 45)
        pygame.draw.rect(self.screen, ui_color, self.maze_back_rect, 1, border_radius=5)
        self.screen.blit(self.font_menu.render("BACK", True, ui_color),
                         self.font_menu.render("BACK", True, ui_color).get_rect(center=self.maze_back_rect.center))

    # Draws the heads-up display showing score, level, and speed
    def draw_hud(self, ui_color):
        speed = Config.BASE_FPS + (self.level - 1) * 2
        rank = f"RANK: {self.level}" if self.game_mode == "CLASSIC" else f"LVL: {self.maze_level}"
        txt = f"SCORE: {self.score} | {rank} | SPEED: {speed} FPS"
        self.screen.blit(self.font_hud.render(txt, True, ui_color), (20, 10))
        for i in range(3):
            pygame.draw.rect(self.screen, ui_color,
                             [self.icon_rect.x, self.icon_rect.y + (i * 8), 30, 4], border_radius=2)

    # Draws the menu interface
    def draw_dynamic_menu(self, ui_color):
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170)); self.screen.blit(overlay, (0,0))
        opts = self.get_current_options()
        self.menu_rects = []
        for i, opt in enumerate(opts):
            bg_rect = pygame.Rect(0, 310 + i*50, Config.SCREEN_WIDTH, 45)
            disp = opt
            if "THEME" in opt: disp = f"THEME: < {self.theme_name} >"
            if "SKIN" in opt: disp = f"SKIN: < {self.skin_name} >"
            if i == self.menu_index:
                bar = pygame.Surface((Config.SCREEN_WIDTH, 45), pygame.SRCALPHA)
                bar.fill((*ui_color, 85)); self.screen.blit(bar, bg_rect)
            txt = self.font_menu.render(disp, True, ui_color if i == self.menu_index else (180, 180, 180))
            self.screen.blit(txt, txt.get_rect(center=bg_rect.center))
            self.menu_rects.append(bg_rect)

    # Draws full-screen overlays such as game over and win screens
    def draw_overlay(self, t, s):
        surf = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 220)); self.screen.blit(surf, (0,0))
        self.screen.blit(self.font_title.render(t, True, (255, 50, 50)), (120, 200))
        self.screen.blit(self.font_menu.render(s, True, (255, 255, 255)), (180, 320))

    # Runs the main game loop
    def run(self):
        while True:
            self.handle_input(); self.update(); self.draw()
            self.clock.tick(Config.BASE_FPS + (self.level - 1) * 2)

# Entry point that starts the game
if __name__ == "__main__":
    game = SnakeGame(); game.run()
