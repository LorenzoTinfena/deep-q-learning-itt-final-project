# %%
from core.DQNAgent import DQNAgent
from core.CartPoleNeuralNetwork import CartPoleNeuralNetwork
import gym
import numpy as np
import torch
from tqdm import tqdm
import glob
import os
from IPython.display import Video
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle
from CartPoleWrapper import CartPoleWrapper
import sys

import pyvirtualdisplay
_display = pyvirtualdisplay.Display(visible=False, size=(1400, 900))
_ = _display.start()

def plot_videos(videos_path='.', output_file_path='.'):
  stringa = 'ffmpeg -i \"concat:'
  elenco_video = glob.glob(f'{videos_path}/*.mp4')
  if len(elenco_video) == 0:
      print('0 mp4 found in this path')
      return
  elenco_file_temp = []
  for f in elenco_video:
    file = videos_path + '/temp' + str(elenco_video.index(f) + 1) + '.ts'
    os.system('ffmpeg -i ' + f + ' -c copy -bsf:v h264_mp4toannexb -f mpegts ' + file)
    elenco_file_temp.append(file)
  for f in elenco_file_temp:
    stringa += f
    if elenco_file_temp.index(f) != len(elenco_file_temp)-1:
      stringa += '|'
    else:
      stringa += f'\" -c copy -y -bsf:a aac_adtstoasc {output_file_path}'
  os.system(stringa)
  display(Video(output_file_path))

def plot_metrics():
    cycol = cycle('bgrcmk')
    f, (ax1, ax2, ax3) = plt.subplots(1, 3)

    samples = 20
    metrics = [n_episodes, total_rewards, number_steps, total_rewards]
    for metric in metrics:
        metric.append([np.array(metric[-(metric%samples):]).mean()] * (metric/samples - metric%samples))
        metric = np.array(metric).reshape(samples, -1).mean(axis=1)

    number_steps.append([np.array(total_rewards[-(total_rewards%samples):]).mean()] * (total_rewards/samples - total_rewards%samples))
    number_steps = np.array(total_rewards).reshape(samples, -1).mean(axis=1)

    total_rewards.append([np.array(total_rewards[-(total_rewards%samples):]).mean()] * (total_rewards/samples - total_rewards%samples))
    total_rewards = np.array(total_rewards).reshape(samples, -1).mean(axis=1)
    
    ax1.set_xlabel('episodes')
    ax1.set_ylabel('total_rewards')
    ax1.plot(n_episodes, total_rewards, c=next(cycol))
    
    ax2.set_xlabel('episodes')
    ax2.set_ylabel('number_steps')
    ax2.plot(episodes, number_steps, c=next(cycol))

    ax3.set_xlabel('episodes')
    ax3.set_ylabel('cost_function_means')
    ax3.plot(episodes, cost_means, c=next(cycol))
    
    f.tight_layout()


# %% [markdown]
# Initialize deep Q-learning agent, neural network, and parameters
# %%
np.random.seed(2)
agent = DQNAgent(env=CartPoleWrapper(gym.make("CartPole-v1")), nn=CartPoleNeuralNetwork())

DISCOUNT_FACTOR = 0.95
LEARNING_RATE = 0.00001

total_rewards = []
number_steps = []
cost_means = []
n_episodes = []
total_episodes = 0


# %% [markdown]
# Training
# %%
while True:
    total_reward, steps, mean_cost_function = agent.start_episode_and_evaluate(DISCOUNT_FACTOR, LEARNING_RATE, 0, render=False, optimize=False)
    print(f'\nn_episodes_training: {n_episodes}\tsteps: {steps}\ttotal_reward: {total_reward}\tmean_cost_function:{mean_cost_function}', flush = True)
    s.append(total_reward)
    number_steps.append(steps)
    cost_means.append(mean_cost_function)
    n_episodes.append(total_episodes)

    for i in tqdm(range(1000), 'learning...'):
        agent.start_episode(DISCOUNT_FACTOR, LEARNING_RATE, 1)
    total_episodes += i+1

    if n_episodes % 110 == 0:
        agent.nn.save(f'saves/data{total_episodes}.nn')


# %% [markdown]
# Visualize training metrics
# %%
plot_metrics()


# %% [markdown]
# Evaluating
# %%

agent.env = gym.wrappers.Monitor(agent.env, 'recording/tmp-videos', force=True, video_callable=lambda episode_id: True)
agent.nn.load('saves/data396000.nn')

for i in range(2):
    total_reward, steps, mean_cost_function = agent.start_episode_and_evaluate(DISCOUNT_FACTOR, LEARNING_RATE, 0, render=True, optimize=False)
    print(f'{i}\t{steps}\t{total_reward}\t{mean_cost_function}')
agent.env.close()

agent.env = agent.env.env
plot_videos('recording/tmp-videos', f'recording/{396000}-episodes.mp4')


# %% [markdown]
evaluation

train 1 000 (with %10 evaluation)

evaluation

train 9 000 - 10 000 (with %90 evaluation)

evaluation

train 90 000 - 100 000

evaluation

train 900 000 - 1 000 0000

evaluation1