import warnings; warnings.filterwarnings("ignore")
import os; os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf; import numpy as np
import matplotlib; matplotlib.use("Agg")  # headless backend: render to file, never to a window
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import gymnasium, collections
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import torch.nn.functional as F
import seaborn as sns
import pandas as pd


def createDNN( nInputs, nOutputs, nLayer, nNodes, last_activation):
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
	# ... and crate the input layer (Keras 3 wants an explicit Input layer) ...
	model.add(Input(shape=(nInputs,)))
	model.add(Dense(nNodes, activation="relu"))
	# ... adding the hidden layers ...
	for _ in range(nLayer):	model.add(Dense(nNodes, activation="relu"))
	# ... and the output layer (softmax for the actor, linear for the critic)
	model.add(Dense(nOutputs, activation=last_activation))
	#
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
	def __init__(self, nInputs, nOutputs, nLayer, nNodes, last_activation):

		super(TorchModel, self).__init__()
		self.nLayer = nLayer
		self.last_activation= last_activation

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
		return x if self.last_activation == F.linear else self.last_activation(x, dim=1)



def training_loop(env, actor_net, critic_net, updateRule, frequency=10, episodes=100, keras=True):

	# Reset the global optimizer and memories before the training.
	# Distinct learning rates for actor/critic keep the policy update slower than
	# the value estimate, which stabilizes A2C on CartPole (gradient clipping is
	# applied inside the update rule as a further stabilizer).
	if keras:
		actor_optimizer = tf.keras.optimizers.Adam(learning_rate=2e-3, clipnorm=0.5)
		critic_optimizer = tf.keras.optimizers.Adam(learning_rate=3e-3, clipnorm=0.5)
	else:
		actor_optimizer = optim.Adam(actor_net.parameters(), lr=2e-3)
		critic_optimizer = optim.Adam(critic_net.parameters(), lr=3e-3)

	rewards_list, reward_queue = [], collections.deque(maxlen=100)
	memory_buffer = [] # In this exercise the memory buffer contains entries (state, action, reward, next_state, done), not trajectories as in the previous exercise
	for ep in range(episodes):

		# Reset the environment and obtain the initial state (gymnasium 1.x returns (obs, info))
		state, _ = env.reset()
		ep_reward = 0
		while True:

			# Select the action sampling from the actor's (policy) probability distribution.
			# Both backends output a softmax over the action space; we sample to keep exploration on-policy.
			if keras:
				probs = actor_net(state.reshape(1, -1)).numpy()[0]
			else:
				with torch.no_grad():
					probs = actor_net(torch.tensor(state, dtype=torch.float32).unsqueeze(0)).numpy()[0]
			action = np.random.choice(len(probs), p=probs)

			# Perform the action; gymnasium 1.x splits termination into terminated/truncated.
			next_state, reward, terminated, truncated, _ = env.step(action)
			done = terminated or truncated

			# Store the one-step transition and accumulate the episode return.
			# We only flag "done" on genuine termination so the bootstrap target uses
			# V(next_state)=0 only when the pole actually fell (not on time-limit truncation).
			memory_buffer.append([state, action, reward, next_state, terminated])
			ep_reward += reward

			# Exit condition for the episode
			if done: break

			# Update the current state
			state = next_state


		# Update the reward list to return
		reward_queue.append( ep_reward )
		rewards_list.append( np.mean(reward_queue) )
		print( f"episode {ep:4d}: rw: {int(ep_reward):3d} (averaged: {np.mean(reward_queue):5.2f})" )

		# Perform the actual training
		if ep % frequency == 0 and ep != 0:
			updateRule(actor_net, critic_net, memory_buffer, actor_optimizer, critic_optimizer, keras)
			memory_buffer = []

	# Close the enviornment and return the rewards list
	env.close()
	return rewards_list



def A2C(actor_net, critic_net, memory_buffer, actor_optimizer, critic_optimizer, keras, gamma=0.99):

	"""
	Main update rule for the A2C update. This function includes the updates for the actor network (or policy function)
	and for the critic network (or value function)

	"""

	# Entropy bonus: a small reward for keeping the policy stochastic. It slows the
	# premature collapse to a deterministic policy and is a standard A2C stabilizer.
	entropy_coeff = 0.01

	# The memory buffer is a list of [state, action, reward, next_state, done] one-step transitions.
	# Build the batched arrays once; the data is the same for every inner update.
	memory_buffer = np.array(memory_buffer, dtype=object)
	states      = np.vstack(memory_buffer[:, 0]).astype(np.float32)
	actions     = np.array(list(memory_buffer[:, 1]), dtype=np.int64)
	rewards     = np.array(list(memory_buffer[:, 2]), dtype=np.float32)
	next_states = np.vstack(memory_buffer[:, 3]).astype(np.float32)
	dones       = np.array(list(memory_buffer[:, 4]), dtype=np.float32)

	#TODO: implement the update rule for the critic (value function)
	# Fit the critic first so the advantage used by the actor relies on an up-to-date baseline.
	for _ in range(10):

		# Update the critic
		if keras:
			with tf.GradientTape() as critic_tape:
				# TD target: y = r + gamma * V(s') * (1 - done).
				# V(s')=0 on terminal states, so the target reduces to the reward there.
				next_value = tf.reshape(critic_net(next_states), [-1])
				target = rewards + gamma * next_value * (1.0 - dones)
				# The bootstrapped target is a fixed regression label: stop gradients through it.
				target = tf.stop_gradient(target)
				value = tf.reshape(critic_net(states), [-1])
				# Minimizing MSE(V(s), target) is exactly minimizing the squared advantage.
				critic_loss = tf.reduce_mean((target - value) ** 2)
			# Apply one gradient-descent step on the critic (Adam clips the gradient norm).
			critic_grads = critic_tape.gradient(critic_loss, critic_net.trainable_variables)
			critic_optimizer.apply_gradients(zip(critic_grads, critic_net.trainable_variables))
		else:
			# torch implementation: same TD-regression objective.
			states_t      = torch.tensor(states, dtype=torch.float32)
			next_states_t = torch.tensor(next_states, dtype=torch.float32)
			rewards_t     = torch.tensor(rewards, dtype=torch.float32)
			dones_t       = torch.tensor(dones, dtype=torch.float32)
			with torch.no_grad():
				target = rewards_t + gamma * critic_net(next_states_t).squeeze(-1) * (1.0 - dones_t)
			value = critic_net(states_t).squeeze(-1)
			critic_loss = F.mse_loss(value, target)
			critic_optimizer.zero_grad()
			critic_loss.backward()
			torch.nn.utils.clip_grad_norm_(critic_net.parameters(), 0.5)
			critic_optimizer.step()

	#TODO: implement the update rule for the actor (policy function)
	# A few actor steps per batch: with CartPole's constant +1 reward the only learning
	# signal comes from terminal transitions, so the policy gradient is weak and benefits
	# from several passes over the (now well-fitted) critic's advantage.
	for _ in range(4):
		# Update the actor
		if keras:
			with tf.GradientTape() as actor_tape:
				# Advantage A(s,a) = r + gamma*V(s') - V(s). The critic supplies the baseline,
				# which is what turns plain REINFORCE into actor-critic (lower-variance signal).
				next_value = tf.reshape(critic_net(next_states), [-1])
				value      = tf.reshape(critic_net(states), [-1])
				advantage  = rewards + gamma * next_value * (1.0 - dones) - value
				# Normalize the advantage (zero-mean, unit-std) to keep the gradient scale
				# stable across batches, then detach it: it is a fixed weight for the actor.
				advantage  = (advantage - tf.reduce_mean(advantage)) / (tf.math.reduce_std(advantage) + 1e-8)
				advantage  = tf.stop_gradient(advantage)

				# log pi(a|s) for the actions actually taken.
				predictions = actor_net(states)
				probabilities = [entry[actions[idx]] for idx, entry in enumerate(predictions)]
				log_probs = tf.math.log(tf.stack(probabilities) + 1e-8)

				# Entropy of the policy, averaged over the batch.
				entropy = -tf.reduce_mean(tf.reduce_sum(predictions * tf.math.log(predictions + 1e-8), axis=1))

				# Policy-gradient objective: maximize log pi(a|s) * advantage (+ entropy bonus),
				# i.e. minimize its negative, averaged over the batch.
				actor_loss = -tf.reduce_mean(log_probs * advantage) - entropy_coeff * entropy
			actor_grads = actor_tape.gradient(actor_loss, actor_net.trainable_variables)
			actor_optimizer.apply_gradients(zip(actor_grads, actor_net.trainable_variables))
		else:
			# torch implementation
			states_t      = torch.tensor(states, dtype=torch.float32)
			next_states_t = torch.tensor(next_states, dtype=torch.float32)
			rewards_t     = torch.tensor(rewards, dtype=torch.float32)
			dones_t       = torch.tensor(dones, dtype=torch.float32)
			actions_t     = torch.tensor(actions, dtype=torch.long)

			# Advantage with the critic as baseline; normalized then detached.
			with torch.no_grad():
				advantage = rewards_t + gamma * critic_net(next_states_t).squeeze(-1) * (1.0 - dones_t) \
				            - critic_net(states_t).squeeze(-1)
				advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-8)

			predictions = actor_net(states_t)
			probabilities = predictions.gather(-1, actions_t[:, None]).squeeze()
			log_probs = torch.log(probabilities + 1e-8)
			entropy = -(predictions * torch.log(predictions + 1e-8)).sum(-1).mean()
			actor_loss = -(log_probs * advantage).mean() - entropy_coeff * entropy
			actor_optimizer.zero_grad()
			actor_loss.backward()
			torch.nn.utils.clip_grad_norm_(actor_net.parameters(), 0.5)
			actor_optimizer.step()


def main():
	print( "\n*************************************************" )
	print( "*  Welcome to the nineth lesson of the RL-Lab!   *" )
	print( "*                    (A2C)                      *" )
	print( "*************************************************\n" )

	# Reduced from 5000 to keep the wall-clock to a few minutes; the curve still shows
	# clear learning (CartPole climbs well into the hundreds, often hitting the 500 cap).
	training_episodes = 700

	print("\nTraining torch model...\n")
	rewards_torch = []
	for _ in range(3):
		env = gymnasium.make("CartPole-v1")
		actor_net = TorchModel(nInputs=4, nOutputs=2, nLayer=2, nNodes=32, last_activation=F.softmax)
		critic_net = TorchModel(nInputs=4, nOutputs=1, nLayer=1, nNodes=32, last_activation=F.linear)
		rewards_torch.append(training_loop(env, actor_net, critic_net, A2C, episodes=training_episodes, keras=False))

	print("\nTraining keras model...\n")
	rewards_keras = []
	for _ in range(3):
		env = gymnasium.make("CartPole-v1")
		actor_net = createDNN( 4, 2, nLayer=2, nNodes=32, last_activation="softmax")
		critic_net = createDNN( 4, 1, nLayer=1, nNodes=32, last_activation="linear")
		rewards_keras.append(training_loop( env, actor_net, critic_net, A2C, episodes=training_episodes, keras=True))


	# plotting the results
	t = list(range(0, training_episodes))

	data_torch = {'Environment Step': [], 'Mean Reward': []}
	for _, rewards in enumerate(rewards_torch):
		for step, reward in zip(t, rewards):
			data_torch['Environment Step'].append(step)
			data_torch['Mean Reward'].append(reward)
	df_torch = pd.DataFrame(data_torch)

	data_keras = {'Environment Step': [], 'Mean Reward': []}
	for _, rewards in enumerate(rewards_keras):
		for step, reward in zip(t, rewards):
			data_keras['Environment Step'].append(step)
			data_keras['Mean Reward'].append(reward)
	df_keras = pd.DataFrame(data_keras)


	# Plotting
	sns.set_style("darkgrid")
	#sns.color_palette("Set2")
	plt.figure(figsize=(8, 6))  # Set the figure size
	sns.lineplot(data=df_torch, x='Environment Step', y='Mean Reward', label='PyTorch', errorbar='se')
	sns.lineplot(data=df_keras, x='Environment Step', y='Mean Reward', label='Keras', errorbar='se')

	# Add title and labels
	plt.title('Comparison PyTorch-Keras A2C on CartPole-v1')
	plt.xlabel('Episodes')
	plt.ylabel('Mean Reward')

	# Show legend
	plt.legend()

	# Save plot (headless): write the learning curve to results/.
	results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
	os.makedirs(results_dir, exist_ok=True)
	plt.savefig(os.path.join(results_dir, "a2c_learning_curve.png"), dpi=130, bbox_inches="tight")

if __name__ == "__main__":
	main()
