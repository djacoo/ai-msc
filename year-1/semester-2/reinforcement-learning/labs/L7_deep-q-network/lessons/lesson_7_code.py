import warnings; warnings.filterwarnings("ignore")
import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf; import numpy as np
import matplotlib; matplotlib.use("Agg")   # headless backend: render to file, never to a window
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import gymnasium, collections
import torch
import torch.nn as nn
import torch.optim as optim
import seaborn as sns
import pandas as pd


def createDNN_keras(nInputs, nOutputs, nLayer, nNodes):
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
	#
	# YOUR CODE HERE!
	#
	# Keras 3 requires an explicit Input layer to fix the input shape.
	model.add(Input(shape=(nInputs,)))
	# Stack 'nLayer' fully-connected hidden layers with ReLU non-linearities:
	# this is the function approximator that replaces the tabular Q-table.
	for _ in range(nLayer):
		model.add(Dense(nNodes, activation="relu"))
	# Output layer: one linear unit per action -> it predicts Q(s, a) for every action a.
	# Linear activation because Q-values are unbounded real numbers.
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
		self.fc1 = nn.Linear(nInputs, nNodes)
		#
		# YOUR CODE HERE!
		#
		# Additional hidden layers (fc1 above is already the first one), so we add
		# 'nLayer - 1' more nNodes->nNodes layers to mirror the Keras architecture.
		self.hidden = nn.ModuleList(
			[nn.Linear(nNodes, nNodes) for _ in range(nLayer - 1)]
		)
		self.output = nn.Linear(nNodes, nOutputs)

	def forward(self, x):
		#
		# YOUR CODE HERE!
		#
		# Forward pass: each hidden layer is followed by a ReLU activation; the final
		# layer is linear so the network outputs raw Q-values (one per action).
		x = torch.relu(self.fc1(x))
		for layer in self.hidden:
			x = torch.relu(layer(x))
		x = self.output(x)
		return x


def mse(network, dataset_input, target):
	"""
	Compute the MSE loss function

	"""

	# Compute the predicted value, over time this value should
	# looks more like to the expected output (i.e., target)
	predicted_value = network(dataset_input)

	# Compute MSE between the predicted value and the expected labels
	mse = tf.math.square(predicted_value - target)
	mse = tf.math.reduce_mean(mse)

	# Return the averaged values for computational optimization
	return mse


def training_loop(env, neural_net, updateRule, keras=True, eps=1.0, updates=1, episodes=100):
	"""
	Main loop of the reinforcement learning algorithm. Execute the actions and interact
	with the environment to collect the experience for the training.

	Args:
		env: gymnasium environment for the training
		neural_net: the model to train
		updateRule: external function for the training of the neural network

	Returns:
		averaged_rewards: array with the averaged rewards obtained

	"""

	# initialize the optimizer (Adam is robust and is the standard choice for DQN).
	# Keras and PyTorch use different optimizer objects, hence the branch. A modest
	# learning rate keeps the online-target updates stable on CartPole.
	if keras:
		optimizer = tf.keras.optimizers.Adam(learning_rate=5e-4)
	else:
		optimizer = optim.Adam(neural_net.parameters(), lr=5e-4)


	# A larger replay buffer keeps a more diverse history of transitions, which
	# decorrelates mini-batches and noticeably stabilizes learning.
	rewards_list, memory_buffer = [], collections.deque( maxlen=10000 )
	averaged_rewards = []
	for ep in range(episodes):

		# reset the environment and obtain the initial state.
		# gymnasium 1.x: reset() returns (observation, info).
		state, _ = env.reset()
		ep_reward = 0
		while True:

			# select the action to perform exploiting an epsilon-greedy strategy:
			# with probability eps explore (random action), otherwise exploit the
			# action with the highest predicted Q-value, argmax_a Q(state, a).
			if np.random.random() < eps:
				action = env.action_space.sample()
			else:
				# query the network with a single state; model(x)/forward is much
				# faster than model.predict for one-sample inference.
				if keras:
					q_values = neural_net(state.reshape(1, -1)).numpy()[0]
				else:
					with torch.no_grad():
						q_values = neural_net(torch.tensor(state, dtype=torch.float32)).numpy()
				action = int(np.argmax(q_values))

			# Perform the action, store the transition in the memory buffer and update the reward.
			# gymnasium 1.x: step() returns (obs, reward, terminated, truncated, info);
			# the episode is done when it terminates OR is truncated (time limit).
			next_state, reward, terminated, truncated, _ = env.step(action)
			done = terminated or truncated
			memory_buffer.append([state, action, reward, next_state, done])
			ep_reward += reward

			# Perform the actual training (experience replay): sample mini-batches
			# from the buffer and run the chosen update rule 'updates' times.
			for _ in range(updates):
				# call the update rule (DQN gradient step on a sampled mini-batch).
				updateRule(neural_net, keras, memory_buffer, optimizer)


			# exit condition for the episode: stop when the environment signals done.
			if done: break

			# update the current state for the next step.
			state = next_state

		# update epsilon value once per episode: exponential decay (with a small floor)
		# so the agent explores heavily at first and gradually shifts to exploiting the
		# greedy policy it has learned.
		eps = max(0.01, eps * 0.97)

		# Update the reward list to return
		rewards_list.append(ep_reward)
		averaged_rewards.append(np.mean(rewards_list))
		print( f"episode {ep:2d}: mean reward: {averaged_rewards[-1]:3.2f}, eps: {eps:3.2f}" )

	# Close the enviornment and return the rewards list
	env.close()
	return averaged_rewards


def DQNupdate(neural_net, keras, memory_buffer, optimizer, batch_size=32, gamma=0.99):

	"""
	Main update rule for the DQN process. Extract data from the memory buffer and update
	the newtwork computing the gradient.

	"""

	if len(memory_buffer) < batch_size: return

	# Sample a random mini-batch of transitions from the replay buffer. Sampling
	# (instead of using the last transitions) decorrelates the training data, which
	# is the core idea of "experience replay" that stabilizes DQN. We unpack the
	# batch into vectorized arrays so the whole update is a few tensor ops rather
	# than a Python loop over single samples (much faster and numerically identical).
	indices = np.random.randint( len(memory_buffer), size=batch_size)
	batch = [memory_buffer[idx] for idx in indices]
	states      = np.array([b[0] for b in batch], dtype=np.float32)
	actions     = np.array([b[1] for b in batch], dtype=np.int32)
	rewards     = np.array([b[2] for b in batch], dtype=np.float32)
	next_states = np.array([b[3] for b in batch], dtype=np.float32)
	dones       = np.array([b[4] for b in batch], dtype=np.float32)

	# compute the target for the training. We start from the network's current
	# prediction for each state (a full Q-vector), then overwrite ONLY the entry of
	# the action actually taken with the TD target. This way the MSE only pushes
	# Q(s, a) towards y and leaves the other actions' predictions unchanged.
	#
	# Bellman optimality update rule:
	#   y = r                            if the next state is terminal (done)
	#   y = r + gamma * max_a' Q(s', a') otherwise (bootstrap from the next state)
	if keras:
		target = neural_net(states).numpy()
		next_q = neural_net(next_states).numpy()
	else:
		with torch.no_grad():
			target = neural_net(torch.tensor(states)).numpy()
			next_q = neural_net(torch.tensor(next_states)).numpy()

	# (1 - dones) zeroes out the bootstrap term for terminal transitions.
	y = rewards + gamma * np.max(next_q, axis=1) * (1.0 - dones)
	target[np.arange(batch_size), actions] = y

	# compute the gradient and perform the backpropagation step: a single
	# gradient-descent step minimizing the MSE between the predicted Q-vectors and
	# the targets, using the selected framework.
	if keras:
		with tf.GradientTape() as tape:
			objective = mse(neural_net, states, target)
		grad = tape.gradient(objective, neural_net.trainable_variables)
		optimizer.apply_gradients(zip(grad, neural_net.trainable_variables))

	else:
		target_t = torch.tensor(target, dtype=torch.float32)
		predicted = neural_net(torch.tensor(states))
		objective = torch.mean(torch.square(predicted - target_t))
		optimizer.zero_grad()
		objective.backward()
		optimizer.step()


def main():
	print( "\n************************************************" )
	print( "*  Welcome to the seventh lesson of the RL-Lab!   *" )
	print( "*               (Deep Q-Network)                 *" )
	print( "**************************************************\n" )

	# Number of training episodes per run and number of independent runs per
	# framework. The original template used 50 episodes x 10 runs; here we trade a
	# few more episodes (so the learning curve has time to clearly rise) for fewer
	# runs, keeping the total wall-clock to a few minutes (see README).
	training_steps = 150
	runs = 3

	# setting DNN configuration
	nInputs=4
	nOutputs=2
	nLayer=2
	nNodes=32

	print("\nTraining torch model...\n")
	rewards_torch = []
	for _ in range(runs):
		env = gymnasium.make("CartPole-v1")#, render_mode="human" )
		neural_net_torch = TorchModel(nInputs, nOutputs, nLayer, nNodes)
		rewards_torch.append(training_loop(env, neural_net_torch, DQNupdate, keras=False, episodes=training_steps))

	print("\nTraining keras model...\n")
	rewards_keras = []
	for _ in range(runs):
		env = gymnasium.make("CartPole-v1")#, render_mode="human" )
		neural_net_keras = createDNN_keras(nInputs, nOutputs, nLayer, nNodes)
		rewards_keras.append(training_loop(env, neural_net_keras, DQNupdate, keras=True, episodes=training_steps))


	# plotting the results
	t = list(range(0, training_steps))

	data = {'Environment Step': [], 'Mean Reward': []}
	for _, rewards in enumerate(rewards_torch):
		for step, reward in zip(t, rewards):
			data['Environment Step'].append(step)
			data['Mean Reward'].append(reward)
	df_torch = pd.DataFrame(data)

	data_keras = {'Environment Step': [], 'Mean Reward': []}
	for _, rewards in enumerate(rewards_keras):
		for step, reward in zip(t, rewards):
			data_keras['Environment Step'].append(step)
			data_keras['Mean Reward'].append(reward)
	df_keras = pd.DataFrame(data_keras)

	# Plotting
	sns.set_style("darkgrid")
	plt.figure(figsize=(8, 6))  # Set the figure size
	sns.lineplot(data=df_torch, x='Environment Step', y='Mean Reward', label='torch', errorbar='se')
	sns.lineplot(data=df_keras, x='Environment Step', y='Mean Reward', label='keras', errorbar='se')

	# Add title and labels
	plt.title('Comparison Keras and PyTorch on CartPole-v1')
	plt.xlabel('Episodes')
	plt.ylabel('Mean Reward')

	# Show legend
	plt.legend()

	# Save the learning curve to the lab's results/ directory (headless: no plt.show()).
	results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
	os.makedirs(results_dir, exist_ok=True)
	plt.savefig(os.path.join(results_dir, "dqn_learning_curve.png"), dpi=130, bbox_inches="tight")


if __name__ == "__main__":
	main()
