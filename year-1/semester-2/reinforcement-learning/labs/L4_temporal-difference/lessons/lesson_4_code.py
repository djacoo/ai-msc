import os, sys, numpy
module_path = os.path.abspath(os.path.join('../tools'))
if module_path not in sys.path: sys.path.append(module_path)
from DangerousGridWorld import GridWorld


def epsilon_greedy(q, state, epsilon):
	"""
	Epsilon-greedy action selection function
	
	Args:
		q: q table
		state: agent's current state
		epsilon: epsilon parameter
	
	Returns:
		action id
	"""
	if numpy.random.random() < epsilon:
		return numpy.random.choice(q.shape[1])
	return q[state].argmax()


def q_learning(environment, episodes, alpha, gamma, expl_func, expl_param):
	"""
	Performs the Q-Learning algorithm for a specific environment
	
	Args:
		environment: OpenAI Gym environment
		episodes: number of episodes for training
		alpha: alpha parameter
		gamma: gamma parameter
		expl_func: exploration function (epsilon_greedy, softmax)
		expl_param: exploration parameter (epsilon, T)
	
	Returns:
		(policy, rewards, lengths): final policy, rewards for each episode [array], length of each episode [array]
	"""
	
	q = numpy.zeros((environment.observation_space, environment.action_space))  # Q(s, a)
	rews = numpy.zeros(episodes)
	lengths = numpy.zeros(episodes)
	#
	# YOUR CODE HERE!
	#

	# Q-Learning is an OFF-policy TD control method: it behaves with an
	# exploratory (epsilon-greedy) policy but bootstraps using the GREEDY action
	# (max_a' Q(s', a')) regardless of what action is actually taken next.
	for ep in range(episodes):
		# Start every episode from the environment's start state.
		state = environment.start_state
		total_reward = 0
		step = 0

		# Episode loop: stop on a terminal state (or a safety cap on steps).
		while not environment.is_terminal(state):
			# Behaviour policy: epsilon-greedy action selection.
			action = expl_func(q, state, expl_param)

			# Sample the (stochastic) transition and the reward of the new state.
			next_state = environment.sample(action, state)
			reward = environment.R[next_state]

			# TD target uses the best next action value (off-policy / greedy bootstrap).
			td_target = reward + gamma * numpy.max(q[next_state])
			# TD update: move Q(s,a) towards the target by a fraction alpha.
			q[state][action] += alpha * (td_target - q[state][action])

			state = next_state
			total_reward += reward
			step += 1
			if step >= 100:  # safety cap to avoid infinite episodes
				break

		rews[ep] = total_reward
		lengths[ep] = step

	policy = q.argmax(axis=1) # q.argmax(axis=1) automatically extract the policy from the q table
	return policy, rews, lengths


def sarsa(environment, episodes, alpha, gamma, expl_func, expl_param):
	"""
	Performs the SARSA algorithm for a specific environment
	
	Args:
		environment: OpenAI gym environment
		episodes: number of episodes for training
		alpha: alpha parameter
		gamma: gamma parameter
		expl_func: exploration function (epsilon_greedy, softmax)
		expl_param: exploration parameter (epsilon, T)
	
	Returns:
		(policy, rewards, lengths): final policy, rewards for each episode [array], length of each episode [array]
	"""

	q = numpy.zeros((environment.observation_space, environment.action_space))  # Q(s, a)
	rews = numpy.zeros(episodes)
	lengths = numpy.zeros(episodes)
	#
	# YOUR CODE HERE!
	#

	# SARSA is an ON-policy TD control method: it bootstraps using the action
	# actually chosen by the (epsilon-greedy) behaviour policy in the next state,
	# hence the name State-Action-Reward-State-Action.
	for ep in range(episodes):
		state = environment.start_state
		# Choose the first action with the behaviour policy before the loop.
		action = expl_func(q, state, expl_param)
		total_reward = 0
		step = 0

		while not environment.is_terminal(state):
			# Sample transition and reward for the current (state, action).
			next_state = environment.sample(action, state)
			reward = environment.R[next_state]

			# Pick the next action on-policy (epsilon-greedy) and use ITS value
			# as the TD target's bootstrap term.
			next_action = expl_func(q, next_state, expl_param)
			td_target = reward + gamma * q[next_state][next_action]
			q[state][action] += alpha * (td_target - q[state][action])

			state = next_state
			action = next_action
			total_reward += reward
			step += 1
			if step >= 100:  # safety cap to avoid infinite episodes
				break

		rews[ep] = total_reward
		lengths[ep] = step

	policy = q.argmax(axis=1) # q.argmax(axis=1) automatically extract the policy from the q table
	return policy, rews, lengths


def main():
	print( "\n*************************************************" )
	print( "*  Welcome to the fourth lesson of the RL-Lab!   *" )
	print( "*        (Temporal Difference Methods)           *" )
	print( "**************************************************" )

	print("\nEnvironment Render:")
	env = GridWorld()
	env.render()

	# Learning parameters
	episodes = 500
	alpha = .3
	gamma = .9
	epsilon = .1

	# Executing the algorithms
	policy_qlearning, rewards_qlearning, lengths_qlearning = q_learning(env, episodes, alpha, gamma, epsilon_greedy, epsilon)
	policy_sarsa, rewards_sarsa, lengths_sarsa = sarsa(env, episodes, alpha, gamma, epsilon_greedy, epsilon)

	print( "\n4) Q-Learning" )
	env.render_policy( policy_qlearning )
	print( "\tExpected reward training with Q-Learning:", numpy.round(numpy.mean(rewards_qlearning), 2) )
	print( "\tAverage steps training with Q-Learning:", numpy.round(numpy.mean(lengths_qlearning), 2) )

	print( "\n5) SARSA" )
	env.render_policy( policy_sarsa )
	print( "\tExpected reward training with SARSA:", numpy.round(numpy.mean(rewards_sarsa), 2) )
	print( "\tAverage steps training with SARSA:", numpy.round(numpy.mean(lengths_sarsa), 2) )
	

if __name__ == "__main__":
	main()
