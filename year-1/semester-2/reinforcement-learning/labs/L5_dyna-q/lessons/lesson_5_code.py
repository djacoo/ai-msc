import os, sys, numpy
module_path = os.path.abspath(os.path.join('../tools'))
if module_path not in sys.path: sys.path.append(module_path)
from DangerousGridWorld import GridWorld

import numpy as np
import matplotlib; matplotlib.use("Agg")  # headless backend: render to file, no display needed
import matplotlib.pyplot as plt


def plot_cumulative_rewards(cumulative_rewards_dyna_q, cumulative_rewards_dyna_q_plus):
    """
    Plots cumulative rewards over time steps.

    Args:
        cumulative_rewards_dyna_q: list of Dyna-Q rewards.
        cumulative_rewards_dyna_q_plus: list of Dyna-Q+ rewards.
    """

    time_steps_dyna_q = np.arange(len(cumulative_rewards_dyna_q))
    time_steps_dyna_q_plus = np.arange(len(cumulative_rewards_dyna_q_plus))

    plt.figure(figsize=(10, 6))
    plt.plot(time_steps_dyna_q, cumulative_rewards_dyna_q, marker='o', linestyle='-', color='b', label='Dyna-Q')
    plt.plot(time_steps_dyna_q_plus, cumulative_rewards_dyna_q_plus, marker='x', linestyle='--', color='r', label='Dyna-Q+')
    plt.title('Cumulative Rewards Over Time Steps', fontsize=14)
    plt.xlabel('Time Steps', fontsize=12)
    plt.ylabel('Cumulative Rewards', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    os.makedirs("../results", exist_ok=True)
    plt.savefig("../results/dyna_q_cumulative_rewards.png", dpi=130, bbox_inches="tight")


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


def dynaQ( environment, maxiters=250, n=10, eps=0.3, alfa=0.3, gamma=0.99 ):
	"""
	Implements the DynaQ algorithm
	
	Args:
		environment: OpenAI Gym environment
		maxiters: timeout for the iterations
		n: steps for the planning phase
		eps: random value for the eps-greedy policy (probability of random action)
		alfa: step size for the Q-Table update
		gamma: gamma value, the discount factor for the Bellman equation
		
	Returns:
		policy: 1-d dimensional array of action identifiers where index `i` corresponds to state id `i`		
		cumulative_rewards: list of cumulative rewards for each policy improvement step (collect one every 20-30 steps to avoid performance issues)
	"""	

	Q = numpy.zeros((environment.observation_space, environment.action_space))
	M = numpy.array([[[None, None] for _ in range(environment.action_space)] for _ in range(environment.observation_space)])

	# Set of (state, action) pairs already experienced: planning only samples
	# from transitions the agent has actually observed (Dyna-Q assumption).
	visited = []
	cumulative_rewards = []

	for it in range(maxiters):
		# --- Real experience: start a fresh episode from a random valid state ---
		state = environment.random_initial_state()

		while not environment.is_terminal(state):
			# (a) Act with the eps-greedy behaviour policy and observe (r, s')
			action = epsilon_greedy(Q, state, eps)
			next_state = environment.sample(action, state)
			reward = environment.R[next_state]

			# (b) Direct RL: standard Q-learning update from the real transition
			Q[state, action] += alfa * (reward + gamma * numpy.max(Q[next_state]) - Q[state, action])

			# (c) Model learning: store the observed deterministic transition
			M[state][action] = [reward, next_state]
			if (state, action) not in visited:
				visited.append((state, action))

			# (d) Planning: n simulated updates from previously seen (s,a) pairs,
			#     using the learned model instead of new real interactions.
			for _ in range(n):
				s_p, a_p = visited[numpy.random.choice(len(visited))]
				r_p, ns_p = M[s_p][a_p]
				Q[s_p, a_p] += alfa * (r_p + gamma * numpy.max(Q[ns_p]) - Q[s_p, a_p])

			state = next_state

		# Track learning progress periodically (greedy policy quality so far)
		if it % 25 == 0:
			cumulative_rewards.append(environment.evaluate_policy(Q.argmax(axis=1)))

	policy = Q.argmax(axis=1)
	return policy, cumulative_rewards


def dynaQplus( environment, maxiters=250, n=10, eps=0.3, alfa=0.3, gamma=0.99 ):
	"""
	Implements the DynaQ+ algorithm
	
	Args:
		environment: OpenAI Gym environment
		maxiters: timeout for the iterations
		n: steps for the planning phase
		eps: random value for the eps-greedy policy (probability of random action)
		alfa: step size for the Q-Table update
		gamma: gamma value, the discount factor for the Bellman equation
		
	Returns:
		policy: 1-d dimensional array of action identifiers where index `i` corresponds to state id `i`
		cumulative_rewards: list of cumulative rewards for each policy improvement step (collect one every 20-30 steps to avoid performance issues)
	"""	

	Q = numpy.zeros((environment.observation_space, environment.action_space))
	M = numpy.array([[[None, None] for _ in range(environment.action_space)] for _ in range(environment.observation_space)])

	kappa = 1e-3  # weight of the exploration bonus
	# tau[s,a] = number of steps since (s,a) was last tried; encourages
	# revisiting transitions that have not been used for a long time.
	tau = numpy.zeros((environment.observation_space, environment.action_space))
	visited_states = []   # states for which at least one action has been observed
	cumulative_rewards = []

	for it in range(maxiters):
		state = environment.random_initial_state()

		while not environment.is_terminal(state):
			# (a) eps-greedy action and real transition
			action = epsilon_greedy(Q, state, eps)
			next_state = environment.sample(action, state)
			reward = environment.R[next_state]

			# Age every transition by one step, then reset the one just taken
			tau += 1
			tau[state, action] = 0

			# (b) Direct RL update
			Q[state, action] += alfa * (reward + gamma * numpy.max(Q[next_state]) - Q[state, action])

			# (c) Model learning. Dyna-Q+ also seeds untried actions of a visited
			#     state as self-loops with reward 0, so planning can consider them.
			if state not in visited_states:
				visited_states.append(state)
				for a in range(environment.action_space):
					if M[state][a][1] is None:
						M[state][a] = [0, state]
			M[state][action] = [reward, next_state]

			# (d) Planning with the exploration bonus r + kappa*sqrt(tau)
			for _ in range(n):
				s_p = visited_states[numpy.random.choice(len(visited_states))]
				a_p = numpy.random.choice(environment.action_space)
				r_p, ns_p = M[s_p][a_p]
				bonus = kappa * numpy.sqrt(tau[s_p, a_p])
				Q[s_p, a_p] += alfa * (r_p + bonus + gamma * numpy.max(Q[ns_p]) - Q[s_p, a_p])

			state = next_state

		if it % 25 == 0:
			cumulative_rewards.append(environment.evaluate_policy(Q.argmax(axis=1)))

	policy = Q.argmax(axis=1)
	return policy, cumulative_rewards


def main():
	print( "\n************************************************" )
	print( "*   Welcome to the fifth lesson of the RL-Lab!   *" )
	print( "*                  (Dyna-Q)                      *" )
	print( "**************************************************" )

	print("\nEnvironment Render:")
	env = GridWorld( deterministic=True )
	env.render()

	print( "\n5) Dyna-Q" )
	dq_policy_n00, _ = dynaQ( env, n=0  )
	dq_policy_n25, _ = dynaQ( env, n=25  )
	dq_policy_n50, dq_rewards = dynaQ( env, n=50  )
	env.render_policy( dq_policy_n50 )
	
	print( "\n5) Dyna-Q+" )
	dqp_policy_n00, _ = dynaQplus( env, n=0 )
	dqp_policy_n25, _ = dynaQplus( env, n=25 )
	dqp_policy_n50, dqp_rewards = dynaQplus( env, n=50 )
	env.render_policy( dqp_policy_n50 )
	print()
	
	print( f"\tExpected Dyna-Q reward with n=0:", env.evaluate_policy(dq_policy_n00) )
	print( f"\tExpected Dyna-Q reward with n=25:", env.evaluate_policy(dq_policy_n25) )
	print( f"\tExpected Dyna-Q reward with n=50:", env.evaluate_policy(dq_policy_n50) )
	
	print()
	
	print( f"\tExpected Dyna-Q+ reward with n=0:", env.evaluate_policy(dqp_policy_n00) )
	print( f"\tExpected Dyna-Q+ reward with n=25:", env.evaluate_policy(dqp_policy_n25) )
	print( f"\tExpected Dyna-Q+ reward with n=50:", env.evaluate_policy(dqp_policy_n50) )
	
	plot_cumulative_rewards(dq_rewards, dqp_rewards)
	

if __name__ == "__main__":
	main()
