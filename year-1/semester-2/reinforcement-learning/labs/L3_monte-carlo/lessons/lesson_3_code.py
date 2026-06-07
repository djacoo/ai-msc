import os, sys, numpy
module_path = os.path.abspath(os.path.join('../tools'))
if module_path not in sys.path: sys.path.append(module_path)
from DangerousGridWorld import GridWorld


def on_policy_mc_epsilon_soft( environment, maxiters=5000, eps=0.3, gamma=0.99 ):
	"""
	Performs the on policy version of the every-visit MC control starting from the same state
	
	Args:
		environment: OpenAI Gym environment
		maxiters: timeout for the iterations
		eps: random value for the eps-greedy policy (probability of random action)
		gamma: gamma value, the discount factor for the Bellman equation
		
	Returns:
		policy: 1-d dimensional array of action identifiers where index `i` corresponds to state id `i`
	"""

	p = [[0 for _ in range(environment.action_space)] for _ in range(environment.observation_space)]
	Q = [[0 for _ in range(environment.action_space)] for _ in range(environment.observation_space)]

	#
	# YOUR CODE HERE!
	#

	# Initialize the policy 'p' as a uniform (fully random) epsilon-soft policy:
	# every action has the same probability 1/|A| in every state. This guarantees
	# that all state-action pairs keep a non-zero probability of being explored.
	n_actions = environment.action_space
	p = [[1 / n_actions for _ in range(n_actions)] for _ in range(environment.observation_space)]

	# returns[s][a] accumulates the (sum, count) of observed returns G for the
	# pair (s, a). We average incrementally so Q(s,a) is the mean return.
	returns_sum = [[0.0 for _ in range(n_actions)] for _ in range(environment.observation_space)]
	returns_cnt = [[0 for _ in range(n_actions)] for _ in range(environment.observation_space)]

	for _ in range(maxiters):
		# Generate one episode following the current epsilon-soft policy.
		# No exploring start here: episodes begin from a random (non-terminal) state.
		episode = environment.sample_episode(p)

		# Compute the return G backward through the episode (every-visit MC):
		# G_t = r_{t+1} + gamma * G_{t+1}. Every occurrence of (s,a) is used.
		G = 0
		for t in range(len(episode) - 1, -1, -1):
			state, action, reward = episode[t]
			G = reward + gamma * G

			# Incremental average of returns -> Q(s,a) estimate.
			returns_sum[state][action] += G
			returns_cnt[state][action] += 1
			Q[state][action] = returns_sum[state][action] / returns_cnt[state][action]

			# Policy improvement: make the policy epsilon-greedy w.r.t. Q in this
			# state. The greedy action gets prob 1-eps+eps/|A|, the others eps/|A|.
			best_action = numpy.argmax(Q[state])
			for a in range(n_actions):
				if a == best_action:
					p[state][a] = 1 - eps + eps / n_actions
				else:
					p[state][a] = eps / n_actions

	# Return the greedy (deterministic) policy extracted from the learned Q values.
	deterministic_policy = [numpy.argmax(Q[state]) for state in range(environment.observation_space)]
	return deterministic_policy


def on_policy_mc_exploring_starts( environment, maxiters=5000, eps=0.3, gamma=0.99 ):
	"""
	Performs the on policy version of the every-visit MC control starting from different states
	
	Args:
		environment: OpenAI Gym environment
		maxiters: timeout for the iterations
		eps: random value for the eps-greedy policy (probability of random action)
		gamma: gamma value, the discount factor for the Bellman equation
		
	Returns:
		policy: 1-d dimensional array of action identifiers where index `i` corresponds to state id `i`
	"""
	p = [[0 for _ in range(environment.action_space)] for _ in range(environment.observation_space)]
	Q = [[0 for _ in range(environment.action_space)] for _ in range(environment.observation_space)]

	#
	# YOUR CODE HERE!
	#

	# Start from a uniform epsilon-soft policy. With exploring starts, exploration
	# is mainly guaranteed by forcing a random initial state-action pair in each
	# episode; the policy itself is still kept epsilon-soft for extra robustness.
	n_actions = environment.action_space
	p = [[1 / n_actions for _ in range(n_actions)] for _ in range(environment.observation_space)]

	# Incremental averaging buffers for the returns of each (s, a) pair.
	returns_sum = [[0.0 for _ in range(n_actions)] for _ in range(environment.observation_space)]
	returns_cnt = [[0 for _ in range(n_actions)] for _ in range(environment.observation_space)]

	for _ in range(maxiters):
		# Exploring start: pick a random non-terminal state and a random first
		# action, so every (s, a) pair can be visited regardless of the policy.
		init_state = environment.random_initial_state()
		init_action = numpy.random.randint(0, n_actions)
		episode = environment.sample_episode(p, initial_state=init_state, initial_action=init_action)

		# Backward pass to compute the discounted return (every-visit MC).
		G = 0
		for t in range(len(episode) - 1, -1, -1):
			state, action, reward = episode[t]
			G = reward + gamma * G

			# Update Q(s,a) as the running mean of observed returns.
			returns_sum[state][action] += G
			returns_cnt[state][action] += 1
			Q[state][action] = returns_sum[state][action] / returns_cnt[state][action]

			# Policy improvement towards the greedy action (epsilon-soft form).
			best_action = numpy.argmax(Q[state])
			for a in range(n_actions):
				if a == best_action:
					p[state][a] = 1 - eps + eps / n_actions
				else:
					p[state][a] = eps / n_actions

	# Extract the final deterministic (greedy) policy from Q.
	deterministic_policy = [numpy.argmax(Q[state]) for state in range(environment.observation_space)]
	return deterministic_policy


def main():
	print( "\n*************************************************" )
	print( "*  Welcome to the third lesson of the RL-Lab!   *" )
	print( "*            (Monte Carlo RL Methods)            *" )
	print( "**************************************************" )

	print("\nEnvironment Render:")
	env = GridWorld()
	env.render()

	print( "\n3) MC On-Policy (with exploring starts)" )
	mc_policy = on_policy_mc_exploring_starts( env, maxiters=5000 )
	env.render_policy( mc_policy )
	print( "\tExpected reward following this policy:", env.evaluate_policy(mc_policy) )
	
	print( "\n3) MC On-Policy (for epsilon-soft policies)" )
	mc_policy = on_policy_mc_epsilon_soft( env, maxiters=5000 )
	env.render_policy( mc_policy )
	print( "\tExpected reward following this policy:", env.evaluate_policy(mc_policy) )
	

if __name__ == "__main__":
	main()
