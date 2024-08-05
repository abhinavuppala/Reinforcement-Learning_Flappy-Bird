import torch, random, numpy as np
from game_ai_playable import *
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000        # store maximum 100,000 games
BATCH_SIZE = 1000           # batch size for training
LR = 0.001                  # learning rate

# STATE
# ------
# Player Y
# Player V
# Gap Y
# Gap Width
# Pipe X

class Agent:
    
    def __init__(self) -> None:
        self.n_games = 0
        self.epsilon = 0                            # control randomness
        self.gamma = 0.9                            # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)      # automatically removes oldest (left) elems
        self.model = Linear_QNet(5, 100, 2)
        self.trainer = QTrainer(self.model, LR, self.gamma)

    
    def get_state(self, game: GameAI):
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
        state = [player_y, player_v, gap_y, gap_width, pipe_x]
        return np.array(state, dtype=float)


    def remember(self, state, action, reward, next_state, game_over):
        '''
        Adds the current state's info to memory, popleft if over MAX_MEMORY
        '''
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        '''
        Take random sample of 1000 from memory if exists, otherwise the entire memory 
        '''
        if len(self.memory) > BATCH_SIZE:
            random_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            random_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*random_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)


    def train_short_memory(self, state, action, reward, next_state, game_over):
        '''
        Train 1 step of STM (1 move in game)
        '''
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        '''
        Do random modes first, then predicted (exploration / exploitation)
        '''
        self.epsilon = 180 - self.n_games
        final_move = [0, 0]

        # random move (more likely earlier on)
        if random.randint(0, 200) < self.epsilon:
            final_move = random.choices([[1, 0], [0, 1]], weights=[0.05, 0.95])[0]
            print("   RANDOM MOVE")

        # predicted move (more likely later on)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            print(">> MODEL MOVE")

        # this will be a 1-element list of what move to
        return final_move



def train():
    '''
    Start training agent
    '''
    # variables for plotting & tracking progress
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    agent = Agent()
    game = GameAI()
    while True:

        # get prev state, predict move & get results of the move
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, game_over, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train ST memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            
            # train LT memory, reset, and plot
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            # new record
            if score > record:
                record = score
            
            # save model every 20 epochs (after first 50)
            if agent.n_games % 20 == 0:
                agent.model.save()
                print("===== MODEL SAVED =====")
            
            print(f'Game {agent.n_games} - Score: {score}, Record: {record}')
            
            plot_scores.append(score)
            total_score += score
            plot_mean_scores.append(total_score / agent.n_games)
            plot(plot_scores, plot_mean_scores)
            


if __name__ == '__main__':
    train()