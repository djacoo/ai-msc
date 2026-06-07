import os, sys, numpy
module_path = os.path.abspath(os.path.join('../tools'))
if module_path not in sys.path: sys.path.append(module_path)
from DangerousGridWorld import GridWorld


def random_dangerous_grid_world( environment ):
	"""
	Performs a random trajectory on the given Dangerous Grid World environment 
	
	Args:
		environment: OpenAI Gym environment
		
	Returns:
		trajectory: an array containing the sequence of states visited by the agent
	"""
	trajectory = []

	# Start the rollout from the environment's start state.
	# Each trajectory entry is a (state, action) pair: the state the agent is in
	# and the random action it selected from there.
	state = environment.start_state

	for step in range(10):
		# Stop early if we land on a terminal cell (goal [G] or death [X]),
		# since no further actions are taken from a terminal state.
		if environment.is_terminal( state ):
			break

		# Random policy: pick a uniformly random action among the 4 moves
		action = numpy.random.randint( 0, environment.action_space )

		# Record the (state, action) taken, then sample the (stochastic) next state
		trajectory.append( (state, action) )
		state = environment.sample( action, state )

	# Append the final state reached (with a placeholder action) to close the path
	trajectory.append( (state, 0) )

	return trajectory


class RecyclingRobot():
	"""
	Class that implements the environment Recycling Robot of the book: 'Reinforcement
	Learning: an introduction, Sutton & Barto'. Example 3.3 page 52 (second edition).
		
	Attributes
	----------
		observation_space : int
			define the number of possible actions of the environment
		action_space: int
			define the number of possible states of the environment
		actions: dict
			a dictionary that translate the 'action code' in human languages
		states: dict
			a dictionary that translate the 'state code' in human languages
		
	Methods
	-------
		reset( self )
			method that reset the environment to an initial state; returns the state
		step( self, action )
			method that perform the action given in input, computes the next state and the reward; returns 
			next_state and reward
		render( self )
			method that print the internal state of the environment
	"""


	def __init__( self ):

		# Loading the default parameters
		self.alfa = 0.7
		self.beta = 0.7
		self.r_search = 0.5
		self.r_wait = 0.2

		# Defining the environment variables.
		# Two energy levels (states) and three possible actions.
		self.observation_space = 2          # states: HIGH, LOW
		self.action_space = 3               # actions: SEARCH, WAIT, RECHARGE
		self.actions = {0: 'SEARCH', 1: 'WAIT', 2: 'RECHARGE'}
		self.states = {0: 'HIGH', 1: 'LOW'}


	def reset( self ):
		# Episodes start with a fully charged battery (HIGH state)
		self.state = 0
		return self.state


	def step( self, action ):

		reward = 0

		# SEARCH: actively look for cans. High expected reward (r_search) but it
		# drains the battery, so the energy level may drop.
		if self.actions[action] == 'SEARCH':
			reward = self.r_search
			if self.state == 0:
				# From HIGH: stays HIGH with prob alfa, otherwise drops to LOW
				self.state = 0 if numpy.random.random() < self.alfa else 1
			else:
				# From LOW: stays LOW with prob beta; otherwise the battery is
				# depleted -> robot must be rescued (reward -3) and reset to HIGH
				if numpy.random.random() < self.beta:
					self.state = 1
				else:
					self.state = 0
					reward = -3

		# WAIT: stand still and wait for a can. Lower reward (r_wait) but the
		# energy level never changes.
		elif self.actions[action] == 'WAIT':
			reward = self.r_wait

		# RECHARGE: go back to base, no cans collected (reward 0), battery -> HIGH.
		elif self.actions[action] == 'RECHARGE':
			reward = 0
			self.state = 0

		return self.state, reward, False, None


	def render( self ):
		# Print the current energy level of the robot
		print( f"\tRobot energy level: {self.states[self.state]}" )
		return True


def main():
	print( "\n************************************************" )
	print( "*  Welcome to the first lesson of the RL-Lab!  *" )
	print( "*             (MDP and Environments)           *" )
	print( "************************************************" )

	print( "\nA) Random Policy on Dangerous Grid World:" )
	env = GridWorld()
	env.render()
	random_trajectory = random_dangerous_grid_world( env )
	print( "\nRandom trajectory generated:", random_trajectory )


	print( "\nB) Custom Environment: Recycling Robot" )
	env = RecyclingRobot()
	state = env.reset()
	ep_reward = 0
	
	for step in range(10):
		a = numpy.random.randint( 0, env.action_space )
		new_state, r, _, _ = env.step( a )
		ep_reward += r
		print( f"\tFrom state '{env.states[state]}' selected action '{env.actions[a]}': \t total reward: {ep_reward:1.1f}" )
		state = new_state


if __name__ == "__main__":
	main()
