import pickle as pk
import random

import gym
import numpy as np
from gym import wrappers

from core.neural_network import NeuralNetwork
from core.replay_memory import ReplayMemory
from copy import copy
class DQNAgent:
	""" Deep Q learning agent
	"""
	def __init__(self, env: gym.Env, nn: NeuralNetwork, replay_memory_max_size, batch_size):
		"""
		Args:
			env: enviroment to use
				is assumed that implements these methods:
				- reset() return first_observation
				- step(action) return next_observation, reward, is_done, info
				- close()
				- render(mode='human')
				and action_space is discrete:------------------------
		"""
		self.env = env
		self._nn = nn
		self._target_nn = copy(self._nn)
		self._sync_target_nn_weights()
		self._replay_memory = ReplayMemory(max_size=replay_memory_max_size)
		self._batch_size = batch_size
	
	def load_weights(self, path):
		self._nn.load_weights(path)
		
	def save_weights(self, path):
		self._nn.save_weights(path)
  
	def _sync_target_nn_weights(self):
		self._target_nn.weights = self._nn.clone_weights()
	
	def start_episode(self, discount_factor, learning_rate, exploration_epsilon: float = 0):
## THIS FUNCTION ISN'T COMPLETE, SEE THE NEXT ONE
		""" start the episode, finish when enviroment return done=True
			Use epsilon-greedy algorithm to
		Args:
			discount_factor: how much the immediate rewards matter than future rewards
				0 <= discount_factor <= 1
			learning_rate: with how much strength you want to learn
				0 < learning_rate
			exploration_epsilon: exploration probability
		"""
		# get the first state
		current_state = self.env.reset()
		
		done = False
		while not done:
			# choose action
			a, z = self._nn.forward_propagate(current_state)
			q_values_predicted = a[-1]
			action = self.env.action_space.sample()  if np.random.uniform(0, 1) < exploration_epsilon else np.argmax(q_values_predicted)
			
			# execute action
			next_state, reward, done, _ = self.env.step(action)
			
			# find target q(s)
			q_values_target = np.copy(q_values_predicted)
			if done: q_values_target[action] = reward
			else: q_values_target[action] = reward + discount_factor * np.max(self._nn.predict(next_state))

			# update neural network
			self._nn.backpropagate(z, a, q_values_target, learning_rate)

			# set current state
			current_state = next_state
		
	def start_episode_and_evaluate(self, discount_factor, learning_rate,
                                epsilon, epsilon_decay = 0.99, min_epsilon = 0.01, render=False, optimize=True):
		""" start the episode, finish when enviroment return done=True
			Use epsilon-greedy algorithm to 
		Args:
			discount_factor: how much the immediate rewards matter than future rewards
				0 <= discount_factor <= 1
			learning_rate: with how much strength you want to learn
				0 < learning_rate
			epsilon: exploration epsilon
			epsilon_decay: epsilon decrease factor at every optimization
			min_epsilon: minimum epsilon value
			render: if env is rendered at each step
			optimize: if _nn optimization in saved after this episode
		"""
		if not optimize:
			# backup weights
			original_weights = self._nn.clone_weights()
		
		# initialize metrics
		total_reward = 0
		steps = 0

		# get the first state
		state = self.env.reset()

		done = False
		while not done:
			# choose action
			if np.random.uniform(0, 1) < epsilon:
				action = self.env.action_space.sample()
			else:
				action = np.argmax(self._nn.predict(state))

			# render
			if render: self.env.render()
			
			# execute action
			next_state, reward, done, _ = self.env.step(action)

			# update monitor metrics
			total_reward += reward
			steps += 1
			
			# store experience
			if optimize: self._replay_memory.put(state, action, reward, done, next_state)
			
			if len(self._replay_memory) >= self._batch_size:
				# get experience batch from replay memory
				for state_exp, action_exp, reward_exp, done_exp, next_state_exp in self._replay_memory.get(batch_size=self._batch_size):
					# find target q(s)
					z, a = self._nn.forward_propagate(state_exp)
					q_values_target = np.copy(a[-1])
					if done: q_values_target[action_exp] = reward_exp
					else: q_values_target[action_exp] = reward_exp + discount_factor * np.max(self._target_nn.predict(next_state_exp))
					
					
					y = []
     				x = []
					for i in range(-100, 100, 0.01):
						self._nn.weights[0][0][0] = i
						x.append(i)
						cost = self._nn.cost_function(a[-1], q_values_target)
						y.append(cost)

     
					# update neural network
					self._nn.backpropagate(z, a, q_values_target, learning_rate)
				
				# sync target nn weights
				self._sync_target_nn_weights()
    
				# epsilon-decay algorithm
				epsilon *= epsilon_decay
				if epsilon < min_epsilon:
					epsilon = min_epsilon

			# set current state
			state = next_state

		if not optimize:
			# restore original weights
			self._nn.weights = original_weights
			self._sync_target_nn_weights()

		return total_reward, steps