import warnings; warnings.filterwarnings("ignore")
import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf;
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import torch.nn.functional as F
import random
import matplotlib; matplotlib.use("Agg")  # headless backend: render to file, no display
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense
import seaborn as sns
import gymnasium, collections
import pandas as pd

def createDNN( nInputs, nOutputs, nLayer, nNodes ):
	"""
	Function that generates a neural network with the given requirements.

	Args:
		nInputs: number of input nodes
		nOutputs: number of output nodes
		nLayer: number of hidden layers
		nNodes: number nodes in the hidden layers
		
	Returns:
		model: the generated tensorflow model

	"""
	# Initialize the neural network
	model = Sequential()
	# ... and create the input layer (Keras 3: explicit Input layer with the state dimension) ...
	model.add(Input(shape=(nInputs,)))
	# ... adding the hidden layers: nLayer fully-connected ReLU layers ...
	for _ in range(nLayer):
		model.add(Dense(nNodes, activation="relu"))
	# ... and the output layer: softmax over actions -> a probability distribution pi(a|s)
	model.add(Dense(nOutputs, activation="softmax"))
	#
	return model

def createValueDNN( nInputs=4, nOutputs=1, nLayer=1, nNodes=64 ):
	"""
	Function that generates a neural network with the given requirements.

	Args:
		nInputs: number of input nodes
		nOutputs: number of output nodes
		nLayer: number of hidden layers
		nNodes: number nodes in the hidden layers
		
	Returns:
		model: the generated tensorflow model

	"""
	# Initialize the value function neural network
	model = Sequential()
	model.add(Dense(nNodes, input_dim=nInputs, activation="relu")) 
	for _ in range(nLayer):	
		model.add(Dense(nNodes, activation="relu")) 
	model.add(Dense(nOutputs, activation="linear")) 

	return model

class TorchModel(nn.Module):
	"""
	Class that generates a neural network with PyTorch and specific parameters.

	Args:
		nInputs: number of input nodes
		nOutputs: number of output nodes
		nLayer: number of hidden layers
		nNodes: number nodes in the hidden layers
		
	"""
	
	# Initialize the neural network
	def __init__(self, nInputs, nOutputs, nLayer, nNodes):
		
		super(TorchModel, self).__init__()
		self.nLayer = nLayer

		# input layer: maps the state (nInputs) to the first hidden representation (nNodes)
		self.fc1 = nn.Linear(nInputs, nNodes)

		# hidden layers: nLayer extra Linear(nNodes, nNodes) registered as fc2, fc3, ...
		# (the forward pass iterates over getattr(self, f'fc{i}') for i in 2..nLayer+1)
		for i in range(nLayer):
			layer_name = f"fc{i+2}"
			self.add_module(layer_name, nn.Linear(nNodes, nNodes))

		#output: logits over actions (softmax applied in forward) -> policy pi(a|s)
		self.output = nn.Linear(nNodes, nOutputs)

	def forward(self, x):
		x = F.relu(self.fc1(x))
		for i in range(2, self.nLayer + 2):
			x = F.relu(getattr(self, f'fc{i}')(x).to(x.dtype))
		x = self.output(x)
		return F.softmax(x, dim=1)
	


def mse(predicted_value, target):
	"""
	Compute the MSE loss function

	"""
	
	# Compute MSE between the predicted value and the expected labels
	mse = tf.math.square(predicted_value - target)
	mse = tf.math.reduce_mean(mse)
	
	# Return the averaged values for computational optimization
	return mse
	
class ValueModel(nn.Module):
	"""
	Class that generates a neural network with PyTorch and specific parameters.

	Args:
		nInputs: number of input nodes
		nOutputs: number of output nodes
		nLayer: number of hidden layers
		nNodes: number nodes in the hidden layers
		
	"""
	
	# Initialize the neural network
	def __init__(self, nInputs=4, nOutputs=1, nLayer=1, nNodes=64):
		
		super(ValueModel, self).__init__()
		self.nLayer = nLayer

		# input layer
		self.fc1 = nn.Linear(nInputs, nNodes)

		#hidden layers
		for i in range(nLayer):
			layer_name = f"fc{i+2}"
			self.add_module(layer_name, nn.Linear(nNodes, nNodes))  

		#output
		self.output = nn.Linear(nNodes, nOutputs)

	def forward(self, x):
		x = F.relu(self.fc1(x))
		for i in range(2, self.nLayer + 2):
			x = F.relu(getattr(self, f'fc{i}')(x).to(x.dtype))
		x = self.output(x)
		return x



def training_loop(env, neural_net, updateRule, keras=True, total_episodes=1500, gamma=0.99, baseline=False):
	"""
	Main loop of the reinforcement learning algorithm. Execute the actions and interact
	with the environment to collect the experience for the trainign.

	Args:
		env: gymnasium environment for the training
		neural_net: the model to train 
		updateRule: external function for the training of the neural network
		
	Returns:
		averaged_rewards: array with the averaged rewards obtained

	"""

	# Reset the global optimizer and memories before the training.
	# NOTE: the lab template used lr=4e-5, which is far too small to show clear learning within
	# a few hundred episodes. We use lr=1e-3 (policy) / 5e-3 (value net), the usual range for
	# REINFORCE on CartPole, so the return curve rises visibly inside the episode budget.
	policy_lr, value_lr = 1e-3, 5e-3
	optimizer = tf.keras.optimizers.Adam(learning_rate=policy_lr) if keras else optim.Adam(neural_net.parameters(), lr=policy_lr)
	if baseline:
		value_net = createValueDNN() if keras else ValueModel()
		optimizer_v = tf.keras.optimizers.Adam(learning_rate=value_lr) if keras else optim.Adam(value_net.parameters(), lr=value_lr)
	

	rewards_list, reward_queue = [], collections.deque(maxlen=100) # reward_queue: last 100 episode rewards, rewards_list: average of the last 100 episode rewards
	memory_buffer = [] # One entry of the list for each episode. Each entry contains all steps of the episode
	for episode in range(total_episodes): # Loop on episodes

		# Reset the environment and the episode reward before the episode
		# gymnasium 1.x: reset() returns (observation, info)
		state, _ = env.reset()
		ep_reward = 0
		memory_buffer.append([])

		while True:

			# Select the action to perform by sampling from the policy pi(.|s).
			# The network expects a batched 2D input, so we add a leading axis.
			if keras:
				distribution = neural_net(state[None, :]).numpy()[0]          # softmax probabilities
				action = np.random.choice(len(distribution), p=distribution)  # sample an action
			else:
				state_t = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
				distribution = neural_net(state_t)                            # softmax probabilities (tensor)
				action = Categorical(distribution).sample().item()            # sample an action

			# Perform the action, store the (s, a, r) transition and update the episode reward.
			# gymnasium 1.x: step() returns (obs, reward, terminated, truncated, info)
			next_state, reward, terminated, truncated, _ = env.step(action)
			memory_buffer[-1].append((state, action, reward))
			ep_reward += reward

			# Exit condition for the episode: terminated (goal/failure) or truncated (time limit)
			done = terminated or truncated
			if done: break
			state = next_state

		# Update the reward list to return
		reward_queue.append(ep_reward)
		rewards_list.append(np.mean(reward_queue))
		print( f"episodes {episode:4d}:  reward: {int(ep_reward):3d} (mean reward: {np.mean(reward_queue):5.2f})" )


		# An episode is over: apply the REINFORCE update on the collected trajectory.
		# Same update rule for both variants; the baseline flag toggles the value-network usage.
		if not baseline:
			updateRule(neural_net, keras, memory_buffer, gamma, optimizer, baseline)
		else:
			updateRule(neural_net, keras, memory_buffer, gamma, optimizer, baseline, value_net, optimizer_v)

		# clean the memory buffer: REINFORCE is on-policy, every episode uses fresh trajectories
		memory_buffer = []

	# Close the enviornment and return the rewards list
	env.close()
	return rewards_list


def REINFORCE(neural_net, keras, memory_buffer, gamma, optimizer, baseline, value_net=None, optimizer_v=None):

	"""
	Main update rule for the REINFORCE process, the naive implementation of the policy-gradient theorem.

	"""
	
	for ep in range(len(memory_buffer)):
		# Extraction of the information from the buffer (for the considered episode).
		# Each trajectory entry is a tuple (state, action, reward).
		trajectory = memory_buffer[ep]
		states  = np.array([step[0] for step in trajectory], dtype=np.float32)
		actions = np.array([step[1] for step in trajectory], dtype=np.int64)
		rewards = np.array([step[2] for step in trajectory], dtype=np.float32)

		# Calculate the return G reversely using the reward-to-go technique:
		#   G_t = r_t + gamma * G_{t+1}
		# so G[t] is the discounted sum of future rewards from step t onward.
		G = np.zeros_like(rewards, dtype=np.float32)
		running = 0.0
		for t in reversed(range(len(rewards))):
			running = rewards[t] + gamma * running
			G[t] = running

		if not baseline:
			# ---- Naive REINFORCE: loss = - sum_t log pi(a_t|s_t) * G_t ----
			if not keras:
				states_t  = torch.as_tensor(states, dtype=torch.float32)
				actions_t = torch.as_tensor(actions, dtype=torch.int64)
				G_t       = torch.as_tensor(G, dtype=torch.float32)

				probs = neural_net(states_t)                       # pi(.|s) for every step
				dist  = Categorical(probs)
				log_probs = dist.log_prob(actions_t)               # log pi(a_t|s_t)
				policy_loss = -(log_probs * G_t).sum()             # policy-gradient objective

				optimizer.zero_grad()
				policy_loss.backward()                             # backprop the policy gradient
				optimizer.step()
			else:
				states_t  = tf.convert_to_tensor(states, dtype=tf.float32)
				actions_oh = tf.one_hot(actions, depth=neural_net.output_shape[-1])
				G_t       = tf.convert_to_tensor(G, dtype=tf.float32)

				with tf.GradientTape() as tape:
					probs = neural_net(states_t)                                  # pi(.|s)
					# pick the probability of the action actually taken at each step
					a_prob = tf.reduce_sum(probs * actions_oh, axis=1)
					log_probs = tf.math.log(a_prob + 1e-8)                        # numerical safety
					policy_loss = -tf.reduce_sum(log_probs * G_t)                 # policy-gradient objective

				grad = tape.gradient(policy_loss, neural_net.trainable_variables) # compute gradients
				optimizer.apply_gradients(zip(grad, neural_net.trainable_variables))

		else:
			# ---- REINFORCE with baseline: advantage A_t = G_t - V(s_t) ----
			# The value network is trained (MSE to G_t) and used to reduce gradient variance.
			if not keras:
				states_t  = torch.as_tensor(states, dtype=torch.float32)
				actions_t = torch.as_tensor(actions, dtype=torch.int64)
				G_t       = torch.as_tensor(G, dtype=torch.float32)

				# --- value network update: fit V(s_t) towards the observed return G_t ---
				v_s = value_net(states_t).squeeze(-1)
				value_loss = F.mse_loss(v_s, G_t)
				optimizer_v.zero_grad()
				value_loss.backward()
				optimizer_v.step()

				# --- policy update with the baseline subtracted (advantage) ---
				advantage = (G_t - value_net(states_t).squeeze(-1)).detach()      # stop grad through V
				probs = neural_net(states_t)
				dist  = Categorical(probs)
				log_probs = dist.log_prob(actions_t)
				policy_loss = -(log_probs * advantage).sum()
				optimizer.zero_grad()
				policy_loss.backward()
				optimizer.step()
			else:
				states_t  = tf.convert_to_tensor(states, dtype=tf.float32)
				actions_oh = tf.one_hot(actions, depth=neural_net.output_shape[-1])
				G_t       = tf.convert_to_tensor(G, dtype=tf.float32)

				# --- value network update: MSE between V(s_t) and the return G_t ---
				with tf.GradientTape() as value_tape:
					v_s = tf.squeeze(value_net(states_t), axis=-1)
					value_loss = mse(v_s, G_t)
				grad_vf = value_tape.gradient(value_loss, value_net.trainable_variables)
				optimizer_v.apply_gradients(zip(grad_vf, value_net.trainable_variables))

				# baseline = current value estimate; advantage drives the policy gradient
				advantage = G_t - tf.squeeze(value_net(states_t), axis=-1)

				# --- policy update using the advantage as the weighting term ---
				with tf.GradientTape() as policy_tape:
					probs = neural_net(states_t)
					a_prob = tf.reduce_sum(probs * actions_oh, axis=1)
					log_probs = tf.math.log(a_prob + 1e-8)
					policy_loss = -tf.reduce_sum(log_probs * tf.stop_gradient(advantage))
				grad = policy_tape.gradient(policy_loss, neural_net.trainable_variables)
				optimizer.apply_gradients(zip(grad, neural_net.trainable_variables))


			
def main():
	print( "\n*************************************************" )
	print( "*  Welcome to the ninth lesson of the RL-Lab!   *" )
	print( "*                 (REINFORCE)                   *" )
	print( "*************************************************\n" )

	# Reduced from 1200 to 500 episodes and from 3 to 2 seeds to keep the wall-clock to a few
	# minutes while the learning curve still clearly rises and plateaus (see README "Expected results").
	training_episodes = 500
	number_seeds_to_test = 2
	gamma=0.99

	# Directory for the headless plot / log output (created if missing).
	results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
	os.makedirs(results_dir, exist_ok=True)

	# setting DNN configuration
	nInputs=4
	nOutputs=2
	nLayer=2
	nNodes=32
	use_torch = False
 
	if use_torch:
		print("\nTraining torch model using REINFORCE baseline...\n")
		rewards_torch_baseline = []
		for _ in range(number_seeds_to_test):
			env = gymnasium.make("CartPole-v1")#, render_mode="human" )
			neural_net_torch = TorchModel(nInputs, nOutputs, nLayer, nNodes)
			rewards_torch_baseline.append(training_loop(env, neural_net_torch, REINFORCE, keras=False, total_episodes=training_episodes, gamma=gamma, baseline=True))

		print("\nTraining torch model using REINFORCE...\n")
		rewards_torch_naive = []
		for _ in range(number_seeds_to_test):
			env = gymnasium.make("CartPole-v1")#, render_mode="human" )
			neural_net_torch = TorchModel(nInputs, nOutputs, nLayer, nNodes)
			rewards_torch_naive.append(training_loop(env, neural_net_torch, REINFORCE, keras=False, total_episodes=training_episodes, gamma=gamma, baseline=False))

		
		# plotting the results
		t = list(range(0, training_episodes))

		data_torch = {'Environment Step': [], 'Mean Reward': []}
		for _, rewards in enumerate(rewards_torch_naive):
			for step, reward in zip(t, rewards):
				data_torch['Environment Step'].append(step)
				data_torch['Mean Reward'].append(reward)
		df_torch = pd.DataFrame(data_torch)

		data_torch_baseline = {'Environment Step': [], 'Mean Reward': []}
		for _, rewards in enumerate(rewards_torch_baseline):
			for step, reward in zip(t, rewards):
				data_torch_baseline['Environment Step'].append(step)
				data_torch_baseline['Mean Reward'].append(reward)
		df_torch_baseline = pd.DataFrame(data_torch_baseline)

		
		# Plotting
		sns.set_style("darkgrid")
		#sns.color_palette("Set2")
		plt.figure(figsize=(8, 6))  # Set the figure size
		sns.lineplot(data=df_torch, x='Environment Step', y='Mean Reward', label='REINFORCE', errorbar='se')
		sns.lineplot(data=df_torch_baseline, x='Environment Step', y='Mean Reward', label='REINFORCE_baseline', errorbar='se')

		# Add title and labels
		plt.title('Comparison REINFORCE vs REINFORCE_baseline PyTorch on CartPole-v1')
		plt.xlabel('Episodes')
		plt.ylabel('Mean Reward')

		# Show legend
		plt.legend()

		# Headless: save the learning curve to file instead of opening a window
		plt.savefig(os.path.join(results_dir, "reinforce_learning_curve.png"), dpi=130, bbox_inches="tight")


	else:

		print("\nTraining keras model using REINFORCE baseline...\n")
		rewards_keras_baseline = []
		for _ in range(number_seeds_to_test):
			env = gymnasium.make("CartPole-v1")#, render_mode="human" )
			neural_net_keras = createDNN(nInputs, nOutputs, nLayer, nNodes)
			rewards_keras_baseline.append(training_loop(env, neural_net_keras, REINFORCE, keras=True, total_episodes=training_episodes, gamma=gamma, baseline=True))

		print("\nTraining keras model using REINFORCE...\n")
		rewards_keras_naive = []
		for _ in range(number_seeds_to_test):
			env = gymnasium.make("CartPole-v1")#, render_mode="human" )
			neural_net_keras = createDNN(nInputs, nOutputs, nLayer, nNodes)
			rewards_keras_naive.append(training_loop(env, neural_net_keras, REINFORCE, keras=True, total_episodes=training_episodes, gamma=gamma, baseline=False))


		# x-axis: one point per episode
		t = list(range(0, training_episodes))

		data_keras = {'Environment Step': [], 'Mean Reward': []}
		for _, rewards in enumerate(rewards_keras_naive):
			for step, reward in zip(t, rewards):
				data_keras['Environment Step'].append(step)
				data_keras['Mean Reward'].append(reward)
		df_keras = pd.DataFrame(data_keras)

		data_keras_baseline = {'Environment Step': [], 'Mean Reward': []}
		for _, rewards in enumerate(rewards_keras_baseline):
			for step, reward in zip(t, rewards):
				data_keras_baseline['Environment Step'].append(step)
				data_keras_baseline['Mean Reward'].append(reward)
		df_keras_baseline = pd.DataFrame(data_keras_baseline)

			
		# Plotting
		sns.set_style("darkgrid")
		#sns.color_palette("Set2")
		plt.figure(figsize=(8, 6))  # Set the figure size
		sns.lineplot(data=df_keras, x='Environment Step', y='Mean Reward', label='REINFORCE', errorbar='se')
		sns.lineplot(data=df_keras_baseline, x='Environment Step', y='Mean Reward', label='REINFORCE_baseline', errorbar='se')

		# Add title and labels
		plt.title('Comparison REINFORCE vs REINFORCE_baseline Keras on CartPole-v1')
		plt.xlabel('Episodes')
		plt.ylabel('Mean Reward')

		# Show legend
		plt.legend()

		# Headless: save the learning curve to file instead of opening a window
		plt.savefig(os.path.join(results_dir, "reinforce_learning_curve.png"), dpi=130, bbox_inches="tight")
			



if __name__ == "__main__":
	main()	
