import pygame
from enum import Enum
import random

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

# used in agent, testing here
def get_state(game: 'Game'):
        '''
        Returns game state info to use for training
        [player_y, player_v, gap_y, gap_width, pipe_x]
        '''
        # get player position & velocity scaled from 0-1 as input
        raw_player_y, raw_player_v = game.player.y, game.player.v
        player_y = raw_player_y / VH
        player_v = raw_player_v / (game.player.MAX_GRAVITY - game.player.JUMP_POWER)

        # get closest pipe to player, based on if leftmost is past player yet or not
        pipes: list[Pipe] = game.pipes
        try:
            if pipes[0].x < game.player.X - pipes[0].WIDTH:
                closest_pipe = pipes[1]
            else:
                closest_pipe = pipes[0]
        except:

            # there is no pipe currently, these are defaults
            gap_y = 0.5
            gap_width = 1
            pipe_x = 1
        else:

            # get information about the closest pipe, scaled from 0-1
            raw_gap_width = closest_pipe.gap_height
            raw_gap_y = closest_pipe.gap_center
            raw_pipe_x = closest_pipe.x

            gap_y = raw_gap_y / VH
            gap_width = (raw_gap_width - closest_pipe.MIN_GAP) / (closest_pipe.MAX_GAP - closest_pipe.MIN_GAP)
            pipe_x = (raw_pipe_x - game.player.X - closest_pipe.WIDTH) / (VW - game.player.X - closest_pipe.WIDTH)

        # some of the values might be negative but don't exceed 1
        return [player_y, player_v, gap_y, gap_width, pipe_x]


class Pipe:

    def __init__(self, gap_center: float = -1, gap_height: float = 200) -> None:
        self.MAX_GAP, self.MIN_GAP = 200, 80
        self.WIDTH = 50
        self.VELOCITY = 5
        self.gap_center = gap_center if gap_center != -1 else random.randint(100, VH - 100)
        self.gap_height = self.MAX_GAP
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
     
    def __init__(self, y_pos: float = 50, velocity: float = 0) -> None:
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



class Game:

    def __init__(self) -> None:
        '''
        Initialize game variables
        '''

        # initialize PyGame variables
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((VW, VH), vsync=1)
        pygame.display.set_caption('Walmart Flappy Bird')
        pygame.font.init()

        # initialize game variables
        self.player = Player()
        self.pipes: list[Pipe] = []
        self.seconds_per_pipe = 3
        self.time_till_pipe = self.seconds_per_pipe * FRAMERATE
        self.score = 0
        self.seconds_alive = 0
        self.pipe_gap = 200
    
    def play_step(self):
        '''
        play 1 frame of the game
        '''
        self.clock.tick(FRAMERATE)
        self.time_till_pipe -= 1
        game_over = False

        # handle events (jumping & quit)
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
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

        # if out of bounds, game over
        if self.player.out_of_bounds():
            print('OUT OF BOUNDS')
            game_over = True

        # check player collision
        if any(self.player.touching_pipe(pipe) for pipe in self.pipes):
            print('COLLISION')
            game_over = True
        self.seconds_alive += (1 / FRAMERATE)

        # display score
        font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = font.render(f'Score: {self.score}', False, Color.BLACK.value)
        self.surface.blit(text_surface, (30, 30))

        # update frame
        pygame.display.flip()

        return game_over, self.score


if __name__ == '__main__':
    game = Game()
    running = True

    try:
        while running:
            game_over, score = game.play_step()
            # print(get_state(game))
            if game_over: running = False
            
    finally:
        print(f'FINAL SCORE: {score}')
        pygame.quit()