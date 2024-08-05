import pygame
from enum import Enum
import random
import numpy as np

# COLOR CONSTANTS
class Color(Enum):
    BLACK = pygame.Color(0, 0, 0)
    WHITE = pygame.Color(255, 255, 255)
    LIGHTBLUE = pygame.Color(130, 130, 230)
    GREEN = pygame.Color(0, 200, 0)
    YELLOW = pygame.Color(235, 235, 52)


# OTHER GLOBAL CONSTANTS
GRAVITY = 1
VW, VH = 800, 600
FRAMERATE = 30

# REWARD
# - Pass 1 pipe: +10
# - Game Over:   -10
# - Otherwise:   +0

# [jump, don't jump]


class Pipe:

    def __init__(self, gap_center: float = -1, gap_height: float = 100) -> None:
        self.MAX_GAP, self.MIN_GAP = 200, 80
        self.WIDTH = 50
        self.VELOCITY = 5
        self.gap_center = gap_center if gap_center != -1 else random.randint(100, VH - 100)
        self.gap_height = gap_height
        self.x = VW + self.WIDTH / 2
    
    def move(self) -> None:
        '''
        Move pipes 1 tick
        '''
        self.x -= self.VELOCITY
    
    def off_screen(self) -> bool:
        '''
        Whether the pipes are off screen or not
        '''
        return self.x < (self.WIDTH * -1)
    
    def past_player(self) -> bool:
        '''
        Whether the pipe has passed by player yet
        '''
        return self.x < (int(VW / 3) - (self.WIDTH * 2))
    
    def rectangles(self) -> tuple[pygame.Rect, pygame.Rect]:
        '''
        Return rectangles to draw pipes
        '''
        return (
            pygame.Rect(self.x + self.WIDTH / 2, 0, self.WIDTH,
                        self.gap_center - self.gap_height / 2),
            pygame.Rect(self.x + self.WIDTH / 2, self.gap_center + self.gap_height / 2, 
                        self.WIDTH, VH)
        )


class Player:
     
    def __init__(self, y_pos: float = 200, velocity: float = 0) -> None:
        self.JUMP_POWER = -10
        self.MAX_GRAVITY = 40
        self.X = int(VW / 3)
        self.y = y_pos
        self.v = velocity
    
    def gravity(self) -> None:
        '''
        Apply 1 tick of gravity
        '''
        self.y += self.v
        self.v = min(self.v + GRAVITY, self.MAX_GRAVITY)

    def jump(self) -> None:
        '''
        Adjust velocity to make bird jump
        '''
        self.v = self.JUMP_POWER

    def out_of_bounds(self) -> bool:
        '''
        Whether player is in bounds
        '''
        return not (-5 < self.y < VH + 5)
    
    def touching_pipe(self, pipe: Pipe) -> bool:
        '''
        Whether player is colliding with a pipe
        '''
        r1, r2 = pipe.rectangles()
        
        # checking in bounds x
        if self.X > r1.right or self.X < r1.left:
            return False
        
        # checking in bounds y
        if self.y < r1.bottom or self.y > r2.top:
            return True
        return False


class GameAI:

    def __init__(self) -> None:
        '''
        Initialize game variables
        '''

        # initialize PyGame variables
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((VW, VH), vsync=1)
        pygame.display.set_caption('Walmart Flappy Bird')
        pygame.font.init()
        self.reset()

        # Game constants
        self.MAX_PIPE_GAP, self.MIN_PIPE_GAP = 200, 80

    def reset(self) -> None:
        '''
        Reset all game constants
        '''
        # initialize game variables
        self.player = Player()
        self.pipes: list[Pipe] = []
        self.seconds_per_pipe = 3
        self.time_till_pipe = 1
        self.score = 0
        self.frame_iteration = 0
        self.pipe_gap = 200
    
    def play_step(self, action):
        '''
        play 1 frame of the game
        '''
        self.clock.tick(FRAMERATE)
        self.time_till_pipe -= 1
        game_over = False
        reward = 0

        # handle quit game
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    exit()

        # handle player jumping
        if action == [1, 0]:
            self.player.jump()

        self.surface.fill(Color.LIGHTBLUE.value)

        # create new pipe every 3 seconds
        if self.time_till_pipe == 0:
            self.time_till_pipe = round(self.seconds_per_pipe * FRAMERATE)
            self.pipes.append(Pipe(gap_height=self.pipe_gap))

            # make game increasingly difficult as time goes
            self.seconds_per_pipe = max(self.seconds_per_pipe - 0.03, 2)
            self.pipe_gap = max(self.pipe_gap - 3, 80)
        
        # pipe operations
        for pipe in self.pipes:

            # remove out of bounds pipes
            if pipe.past_player():
                self.pipes.remove(pipe)
                reward = 10
                self.score += 1
            else:

                # draw 2 rectangles that make up pipe
                r1, r2 = pipe.rectangles()
                pygame.draw.rect(self.surface, Color.GREEN.value, r1)
                pygame.draw.rect(self.surface, Color.GREEN.value, r2)
                pipe.move()

        # draw bird at correct position
        pygame.draw.circle(self.surface, Color.YELLOW.value, (self.player.X, self.player.y), 10)

        # apply gravity
        self.player.gravity()

        # if out of bounds or collision, game over
        if self.player.out_of_bounds() or any(self.player.touching_pipe(pipe) for pipe in self.pipes):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # display score
        font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = font.render(f'Score: {self.score}', False, Color.BLACK.value)
        self.surface.blit(text_surface, (30, 30))

        # update frame
        pygame.display.flip()
        self.frame_iteration += 1

        return reward, game_over, self.score


# if __name__ == '__main__':
#     game = GameAI()
#     running = True

#     try:
#         while running:
#             reward, game_over, score = game.play_step()
#             if game_over: running = False
            
#     finally:
#         pygame.quit()