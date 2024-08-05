# Reinforcement Learning with Flappy Bird
Deep Q Learning Model with PyTorch made to play Flappy Bird (first attempt). My model was based on this model by Patrick Loeber, modified to work with Flappy Bird rather than Snake.
https://www.youtube.com/watch?v=L8ypSXwyBds&t=4241s

Flappy Bird game was made using Pygame, while the agent & model were developed using PyTorch.

Model details - The model has an input layer of size 5, a hidden layer size 100, and an output layer size 2. Input is a tensor in the format of [Player Y position, Player Velocity, Nearest Pipe Gap Y position, Nearest Pipe Gap Width], Nearest Pipe X position. Output is just [jump, don't jump] 

I used a learning rate of 0.001, discount rate of 0.9, and max epsilon value of 180. I initially had max epsilon at 80 as per the guide, but found that the model would have to get lucky in order to even pass one pipe before it stopped exploring. After ~400 epochs, the model achieved a high score of 12 points, and was regularly getting multi-point games. Overall, by the end, the model was good at navigating most pipes; it only struggled when there was a large difference in heights between gaps. In the future, I plan to experiement with modifying other hyperparameters or adding additional nodes to the hidden layer.

How to train your own version of the model:
1. Download this repo to your local directory
2. Install dependencies through ```pip install -r requirements.txt```
3. Modify hyperparameters or model structure as you want
4. Run agent.py to start training, it should bring up a window of the Flappy Bird game & the graph of scores
5. When the model seems satistfactory, exit the Flappy Bird window. The model autosaves every 20 epochs

![Screenshot of flappy bird game](https://github.com/abhinavuppala/Reinforcement-Learning_Flappy-Bird/blob/main/readme_assets/flappybird_screenshot.png)
Screenshot of the flappy bird game. Basic graphics but has the same functionality overall.

![Screenshot of Graph of scores over epochs](https://github.com/abhinavuppala/Reinforcement-Learning_Flappy-Bird/blob/main/readme_assets/training_graph.png)
Screenshot of graph recording training. Blue line shows points per epoch, and orange line shows total average score.
