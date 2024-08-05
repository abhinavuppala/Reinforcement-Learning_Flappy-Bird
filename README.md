# Reinforcement Learning with Flappy Bird
Deep Q Learning Model with PyTorch made to play Flappy Bird (first attempt). My model was based on this model by Patrick Loeber, modified to work with Flappy Bird rather than Snake.
https://www.youtube.com/watch?v=L8ypSXwyBds&t=4241s

I used a learning rate of 0.001, discount rate of 0.9, and max epsilon value of 180. I initially had max epsilon at 80, but found that the model would have to get lucky in order to even pass one pipe before it stopped exploring.

After ~400 epochs, the model achieved a high score of 12 points, and was regularly getting multi-point games. Overall, by the end, the model was good at navigating most pipes; it only struggled when there was a large difference in heights between gaps.

